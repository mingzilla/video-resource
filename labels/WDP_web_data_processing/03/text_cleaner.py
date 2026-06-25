import re
import regex
from collections import Counter
from typing import TypedDict


class CleaningStats(TypedDict):
    """Statistics from text cleaning process"""
    original_length: int
    cleaned_length: int
    paragraphs_removed: int
    sentences_removed: int
    quality_passed: bool
    cleaned_text_if_rejected: str  # Contains cleaned text even if quality filters failed


class CompanyTextCleaner:
    """Cleans company web text using quality filters and within-row deduplication"""

    # Threshold high enough that the Step-4 n-gram phrase pass never fires (no
    # phrase recurs 10**9 times) - the named way to run a clean with that pass off.
    NGRAM_DEDUP_DISABLED = 10 ** 9

    _ABBREVS = frozenset({
        # Titles (EN)
        'mr', 'mrs', 'ms', 'dr', 'prof', 'rev', 'capt', 'jr', 'sr',
        # Titles (DE)
        'hr', 'fr',
        # Titles (FR)
        'mme', 'mlle',
        # Military/official
        'lt', 'col', 'gen', 'sgt',
        # Business (EN)
        'ltd', 'inc', 'co', 'corp', 'llp', 'no', 'reg', 'ref', 'est',
        # Business (DE)
        'gmbh', 'kg', 'ug',
        # Business (FR)
        'sarl', 'sas',
        # EU business entities
        'bv', 'nv', 'ag', 'sa', 'plc',
        # Common
        'eg', 'ie', 'vs', 'etc', 'approx',
        # Address (EN)
        'st', 'ave', 'rd', 'blvd', 'ln', 'ct', 'pl', 'sq', 'ter', 'apt', 'ste', 'mt', 'ft',
        # Address (DE)
        'str', 'nr',
        # Months
        'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
    })
    # Split on .!? + whitespace but not when preceded by a known abbreviation word.
    # Uses the `regex` module for variable-width lookbehind support.
    _ABBREV_SPLIT_RE = regex.compile(
        r'(?<!(?:' + '|'.join(r'\b' + regex.escape(a) for a in sorted(_ABBREVS, key=len, reverse=True)) + r'))[.!?]+\s+',
        regex.IGNORECASE
    )

    def __init__(self):
        # Regex patterns for boilerplate removal
        self.css_pattern = re.compile(r'<style[^>]*>.*?</style>', re.DOTALL | re.IGNORECASE)
        self.js_pattern = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL | re.IGNORECASE)
        self.html_tag_pattern = re.compile(r'<[^>]+>')
        self.css_property_pattern = re.compile(r'\{[^}]*\}')
        # A pipe before each table-cell OPEN tag (see _delimit_html_table_cells): de-fuses adjacent
        # AND malformed cells, preserves boundaries, matches mistral's | shape. Marking the OPEN
        # (not close) is the trick — web HTML drops </td>, never <td>. \b avoids matching <tdfoo>.
        self.cell_open_pattern = re.compile(r'<t[dh]\b[^>]*>', re.IGNORECASE)

    def clean_text(
        self,
        text: str,
        n_gram_min_phrase_words: int = 8,
        n_gram_repeat_threshold: int = 3,
        quality_min_unique_word_ratio: float = 0.15
    ) -> tuple[str | None, CleaningStats]:
        """
        Clean company web text and return cleaned text + stats

        Args:
            text: Raw company web text (concatenated from multiple pages)
            n_gram_min_phrase_words: Only check phrases with this many words or more
            n_gram_repeat_threshold: Remove phrases appearing this many times or more
            quality_min_unique_word_ratio: Minimum unique word ratio (0.0-1.0)

        Returns:
            (cleaned_text, stats_dict) or (None, stats_dict) if filtered out
        """
        original_length = len(text)

        stats: CleaningStats = {
            "original_length": original_length,
            "cleaned_length": 0,
            "paragraphs_removed": 0,
            "sentences_removed": 0,
            "quality_passed": False,
            "cleaned_text_if_rejected": ""
        }

        # Step 1: Remove boilerplate (CSS, JS, HTML tags)
        text = self._remove_boilerplate(text)

        # Step 2: Deduplicate paragraphs first (removes large duplicate blocks)
        text, para_removed = self._deduplicate_paragraphs(text)
        stats["paragraphs_removed"] = para_removed

        # Step 3: Deduplicate sentences (keep first occurrence, drop exact dupes)
        text, sent_removed = self._deduplicate_sentences(text)
        stats["sentences_removed"] = sent_removed

        # Step 4: Remove repeated phrases (navigation, footers) - processes cleaned text
        text = self._remove_repeated_phrases(text, n_gram_min_phrase_words, n_gram_repeat_threshold)

        # Final cleanup before quality check
        text = self._normalize_whitespace(text)

        # Step 5: Apply quality filters (only after all cleaning attempts)
        if not self._apply_quality_filters(text, quality_min_unique_word_ratio):
            # Store cleaned text even though it failed quality filters
            stats["cleaned_text_if_rejected"] = text
            stats["cleaned_length"] = len(text)
            return None, stats

        stats["quality_passed"] = True
        stats["cleaned_length"] = len(text)

        return text, stats

    @staticmethod
    def clean_text_without_ngram_dedup(text: str) -> tuple[str | None, CleaningStats]:
        """clean_text with the Step-4 n-gram phrase pass disabled.

        The n-gram pass deletes ALL copies of a repeated 8+ word phrase (not
        keep-first), so it can erase real repeated values (e.g. an RNS issuance
        amount stated three times). Consumers feeding an LLM want every other
        pass but not this one - this is the named entry point for that.
        """
        return CompanyTextCleaner().clean_text(
            text, n_gram_repeat_threshold=CompanyTextCleaner.NGRAM_DEDUP_DISABLED
        )

    def _apply_quality_filters(self, text: str, min_unique_word_ratio: float) -> bool:
        """
        Apply quality filters inspired by Gopher/C4 rules

        Args:
            text: Text to check
            min_unique_word_ratio: Minimum unique word ratio (0.0-1.0)

        Filters out text that:
        - Is too short (< 100 chars or < 20 words)
        - Has too many special characters
        - Has gibberish (very short or very long words)
        - Is too repetitive
        """
        if not text or not isinstance(text, str):
            return False

        text = text.strip()

        # Filter 1: Minimum length
        if len(text) < 100:
            return False

        words = text.split()

        # Filter 2: Minimum word count
        if len(words) < 20:
            return False

        # Filter 3: Average word length (detect gibberish)
        avg_word_length = sum(len(word) for word in words) / len(words)
        if avg_word_length < 3 or avg_word_length > 15:
            return False

        # Filter 4: Special character ratio
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:
            return False

        # Filter 5: Unique word ratio (detect repetitive content)
        unique_words = len(set(w.lower() for w in words))
        if unique_words / len(words) < min_unique_word_ratio:
            return False

        # Filter 6: Line length check (detect non-natural text)
        lines = [line for line in text.split('\n') if line.strip()]
        if lines:
            avg_line_length = sum(len(line) for line in lines) / len(lines)
            # Filter out text with extremely short lines (likely navigation menus, lists)
            if avg_line_length < 20 and len(lines) > 10:
                return False

        return True

    def _delimit_html_table_cells(self, text: str) -> str:
        """Insert a markdown pipe before each table-cell OPEN tag, BEFORE the tag strip, so adjacent
        cell values can't fuse and cell boundaries survive (| GBP | 7,482,833 | 0.20 …, matching
        mistral). Marking the OPEN (not the close) de-fuses malformed cells too: web HTML usually
        drops the </td>, never the <td>. `<t[dh]\\b[^>]*>` covers <td>/<th> and attributed opens; the
        \\b avoids matching <tdfoo>. Only cell-open tags touched, so all other text is byte-identical.
        (Multi-row tables merge onto one line — pipe-separated, never fused.)"""
        return self.cell_open_pattern.sub('| ', text)

    def _remove_boilerplate(self, text: str) -> str:
        """
        Remove CSS, JavaScript, HTML tags, and common metadata patterns

        This handles text extraction artifacts that shouldn't be in cleaned text
        """
        # Remove CSS blocks
        text = self.css_pattern.sub('', text)

        # Remove JavaScript blocks
        text = self.js_pattern.sub('', text)

        # Pipe-delimit table cells BEFORE the tag strip so adjacent cell values can't fuse
        text = self._delimit_html_table_cells(text)

        # Remove HTML tags
        text = self.html_tag_pattern.sub('', text)

        # Remove CSS properties (e.g., "{color: red; font-size: 12px}")
        text = self.css_property_pattern.sub('', text)

        # Remove common metadata patterns
        metadata_patterns = [
            r'charset=[\w-]+',
            r'encoding=[\w-]+',
            r'content-type:[\w\s/;=-]+',
            r'viewport[\w\s:;=",-]+',
            r'http-equiv[\w\s:;=",-]+'
        ]

        for pattern in metadata_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        return text

    def _remove_repeated_phrases(self, text: str, min_words: int, threshold: int) -> str:
        """
        Remove phrases (consecutive words) that repeat multiple times

        This handles navigation menus, footers, and other boilerplate that repeats
        across multiple pages without punctuation.

        Args:
            text: Input text
            min_words: Minimum phrase length in words (e.g., 4 means 4-word phrases)
            threshold: Remove phrases appearing this many times or more

        Returns:
            Text with repeated phrases removed
        """
        words = text.split()

        # Not enough words to form phrases
        if len(words) < min_words:
            return text

        # Try different n-gram sizes from longest to shortest (greedy matching)
        for n in range(10, min_words - 1, -1):
            if len(words) < n:
                continue

            # Count n-gram occurrences
            ngram_counts = Counter()

            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i + n])
                ngram_counts[ngram] += 1

            # Find and remove repeated n-grams
            for ngram, count in ngram_counts.items():
                if count >= threshold:
                    # Remove all occurrences (leave blank space, normalized later)
                    text = text.replace(ngram, ' ')

            # Re-split words for next iteration (smaller n-grams)
            words = text.split()

        return text

    def _deduplicate_paragraphs(self, text: str) -> tuple[str, int]:
        """
        Remove duplicate paragraphs within the text

        This handles repeated sections like headers, footers, privacy policies
        across multiple pages of the same website.

        Args:
            text: Input text

        Returns:
            (deduplicated_text, removed_count)
        """
        # Split by double newlines or single newlines followed by significant content
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]

        seen = set()
        unique_paragraphs = []
        removed_count = 0

        for para in paragraphs:
            # Normalize whitespace for comparison
            normalized = ' '.join(para.split())

            # Skip very short paragraphs (likely not meaningful duplicates)
            if len(normalized) < 30:
                unique_paragraphs.append(para)
                continue

            if normalized not in seen:
                seen.add(normalized)
                unique_paragraphs.append(para)
            else:
                removed_count += 1

        return '\n\n'.join(unique_paragraphs), removed_count

    def _deduplicate_sentences(self, text: str) -> tuple[str, int]:
        """Deduplicate sentences; short fragments pass through without deduplication."""
        seen = set()
        unique_sentences = []
        removed_count = 0

        for sentence in self._ABBREV_SPLIT_RE.split(text):
            sentence = sentence.strip()
            if not sentence:
                continue

            normalized = ' '.join(sentence.split())

            if len(normalized) < 15:
                unique_sentences.append(sentence)
                continue

            if normalized not in seen:
                seen.add(normalized)
                unique_sentences.append(sentence)
            else:
                removed_count += 1

        return '. '.join(unique_sentences) + '.' if unique_sentences else '', removed_count

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize excessive whitespace while preserving paragraph structure"""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)

        # Replace multiple newlines with double newline (paragraph breaks)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text.strip()
