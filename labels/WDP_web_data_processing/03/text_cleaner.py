import re
import regex
from enum import Enum
from typing import TypedDict


class CleaningStats(TypedDict):
    """Statistics from text cleaning process"""
    original_length: int
    cleaned_length: int
    paragraphs_removed: int
    sentences_removed: int
    foreign_char_length: int       # exact chars the foreign-strip removed (non-Latin + astral), via subn
    foreign_char_perc: float      # foreign_char_length / original_length * 100
    overall_removal_perc: float   # (original_length - cleaned_length) / original_length * 100
    quality_status: "QualityPattern"  # the quality signal the cleaned text trips (GOOD, or a kept-advisory pattern)
    cleaned_text_if_rejected: str  # cleaned text even when the quality filter rejected it


class QualityPattern(Enum):
    """The single quality signal a cleaned text first trips (or GOOD)."""
    GOOD = "GOOD"
    EMPTY = "EMPTY"
    TOO_SHORT = "TOO_SHORT"
    TOO_FEW_WORDS = "TOO_FEW_WORDS"
    AVG_WORD_TOO_SHORT = "AVG_WORD_TOO_SHORT"
    AVG_WORD_TOO_LONG = "AVG_WORD_TOO_LONG"
    TOO_MANY_SPECIAL = "TOO_MANY_SPECIAL"
    TOO_REPETITIVE = "TOO_REPETITIVE"
    LINES_TOO_SHORT = "LINES_TOO_SHORT"


# Patterns that NULL the row - only genuinely no-content text (empty / too short / too few words).
# Every other detected pattern is KEPT with its quality_status recorded, so a consumer can filter it
# out for their own use (e.g. keep AVG_WORD_TOO_SHORT/LONG or repetitive text out of embeddings) rather
# than the cleaner destroying it here.
_NULL_PATTERNS = frozenset({
    QualityPattern.EMPTY,
    QualityPattern.TOO_SHORT,
    QualityPattern.TOO_FEW_WORDS,
})


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

    # A NON-Latin char is anything outside Latin script, shared punctuation/digits/symbols
    # (Common), and Latin-attaching combining marks (Inherited). Script-based (not \p{L}) so a script's
    # combining marks strip too (Thai tone marks are \p{M}, which \p{L} would leave behind). regex.V1 is
    # required for the negated \p{Script} set - the module's default flavour cannot express it.
    _foreign_re__non_latin = regex.compile(r'[^\p{Latin}\p{Common}\p{Inherited}]+', regex.V1)
    _foreign_re__astral = regex.compile(r'[\U00010000-\U0010FFFF]+', regex.V1)
    _foreign_re__both = regex.compile(r'[^\p{Latin}\p{Common}\p{Inherited}]+|[\U00010000-\U0010FFFF]+', regex.V1)

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

    def clean_text(self, text: str) -> tuple[str | None, CleaningStats]:
        """Clean company web text with default parameters (non-western + astral strip ON)."""
        return self.clean_text_with_config(
            text,
            n_gram_min_phrase_words=8,
            n_gram_repeat_threshold=3,
            quality_min_unique_word_ratio=0.15,
            quality_max_chars=50000,
            exclude_non_western=True,
            exclude_emoji=True,
        )

    def clean_text_with_config(
        self,
        text: str,
        n_gram_min_phrase_words: int,
        n_gram_repeat_threshold: int,
        quality_min_unique_word_ratio: float,
        quality_max_chars: int,
        exclude_non_western: bool,
        exclude_emoji: bool,
    ) -> tuple[str | None, CleaningStats]:
        """Clean company web text; return (cleaned_text, stats), or (None, stats) when the
        quality filter rejects the cleaned text as empty/degenerate.

        Quality is scored on the first quality_max_chars only: the unique-word-ratio was
        calibrated on the 50k-capped archive and type-token ratio falls with length
        (Heaps' law), so scoring a full multi-page doc under-rates it. The returned
        cleaned text is always full-length.
        """
        original_length = len(text)

        stats: CleaningStats = {
            "original_length": original_length,
            "cleaned_length": 0,
            "paragraphs_removed": 0,
            "sentences_removed": 0,
            "foreign_char_length": 0,
            "foreign_char_perc": 0.0,
            "overall_removal_perc": 0.0,
            "quality_status": QualityPattern.GOOD,
            "cleaned_text_if_rejected": ""
        }

        # Step 1: Remove boilerplate (CSS, JS, HTML tags)
        text = self._remove_boilerplate(text)

        # Step 1b: strip non-western + astral chars. Runs before dedup so a mostly-non-English
        # site's embedded English survives into the later passes; also fixes the no-space avg-word misfire.
        text, stats["foreign_char_length"] = self.strip_foreign_chars(text, exclude_non_western, exclude_emoji)

        # Step 2: Deduplicate paragraphs first (removes large duplicate blocks)
        text, para_removed = self._deduplicate_paragraphs(text)
        stats["paragraphs_removed"] = para_removed

        # Step 3: Deduplicate sentences (keep first occurrence, drop exact dupes)
        text, sent_removed = self._deduplicate_sentences(text)
        stats["sentences_removed"] = sent_removed

        # Step 4: Remove repeated phrases (navigation, footers)
        text = self._remove_repeated_phrases(text, n_gram_min_phrase_words, n_gram_repeat_threshold)

        # Final cleanup before quality check
        text = self._normalize_whitespace(text)

        # Step 5: classify quality (after all cleaning). NULL the empty/degenerate patterns; keep the
        # rest with their status recorded as an advisory signal. One detection, used for both decisions.
        pattern = self._detect_quality_pattern(text, quality_min_unique_word_ratio, quality_max_chars)
        stats["quality_status"] = pattern
        stats["cleaned_length"] = len(text)
        self._stats__derive_percs(stats)

        if pattern in _NULL_PATTERNS:
            stats["cleaned_text_if_rejected"] = text  # cleaned text retained even though the row is nulled
            return None, stats

        return text, stats

    @staticmethod
    def clean_text_without_ngram_dedup(text: str) -> tuple[str | None, CleaningStats]:
        """clean_text with the Step-4 n-gram phrase pass disabled.

        The n-gram pass deletes ALL copies of a repeated 8+ word phrase (not
        keep-first), so it can erase real repeated values (e.g. an RNS issuance
        amount stated three times). Consumers feeding an LLM want every other
        pass but not this one - this is the named entry point for that.
        """
        # Foreign-char strip pinned OFF here so this cross-project LLM-feed entry keeps its exact prior
        # output (non-western strip is a pipeline/embedder concern; the LLM handles non-English). Keeping
        # it behaviour-neutral means no consumer of this entry changes as a side effect of the strip default.
        return CompanyTextCleaner().clean_text_with_config(
            text,
            n_gram_min_phrase_words=8,
            n_gram_repeat_threshold=CompanyTextCleaner.NGRAM_DEDUP_DISABLED,
            quality_min_unique_word_ratio=0.15,
            quality_max_chars=50000,
            exclude_non_western=False,
            exclude_emoji=False,
        )

    def strip_foreign_chars(self, text: str, exclude_non_western: bool,
                            exclude_emoji: bool) -> tuple[str, int]:
        """Strip non-western and/or astral chars in ONE regex pass, returning (text, foreign_char_length).

        Replaces stripped runs with a SPACE, not '': a no-space script between two English words would
        otherwise fuse them into one bogus token; the space is collapsed by the later whitespace pass.
        foreign_char_length is the EXACT number of chars removed: subn returns the replacement (=run)
        count, and each run of k chars collapses to one space (length drops k-1), so
        (len_before - len_after) + runs == the exact char count - no second pass, and no run-collapse
        undercount. Includes astral/emoji when exclude_emoji is on.
        """
        pattern = self._foreign_chars__select_pattern(exclude_non_western, exclude_emoji)
        if pattern is None:
            return text, 0
        stripped, runs = pattern.subn(' ', text)
        foreign_char_length = (len(text) - len(stripped)) + runs
        return stripped, foreign_char_length

    def _stats__derive_percs(self, stats: CleaningStats) -> None:
        """Fill the two derived percents from the collected lengths (after the quality stage)."""
        original = stats["original_length"]
        if original <= 0:
            return
        stats["foreign_char_perc"] = round(100.0 * stats["foreign_char_length"] / original, 2)
        stats["overall_removal_perc"] = round(100.0 * (original - stats["cleaned_length"]) / original, 2)

    def _foreign_chars__select_pattern(self, exclude_non_western: bool, exclude_emoji: bool):
        if exclude_non_western and exclude_emoji:
            return self._foreign_re__both
        if exclude_non_western:
            return self._foreign_re__non_latin
        if exclude_emoji:
            return self._foreign_re__astral
        return None

    def _apply_quality_filters(self, text: str, min_unique_word_ratio: float, max_chars: int) -> bool:
        """Keep the text unless its quality pattern is a null-causing (empty/degenerate) one."""
        return self._detect_quality_pattern(text, min_unique_word_ratio, max_chars) not in _NULL_PATTERNS

    def _detect_quality_pattern(self, text: str, min_unique_word_ratio: float,
                                max_chars: int) -> QualityPattern:
        """Classify text by the FIRST quality signal it trips (Gopher/C4-style), else GOOD.

        Order is load-bearing: the empty/degenerate checks run before the advisory ones,
        so a first-trip of an advisory pattern proves the null-causing checks already
        passed - which is what lets the null decision act on this single returned pattern.
        """
        if not text or not isinstance(text, str):
            return QualityPattern.EMPTY

        # Score on the first max_chars only (Heaps'-law cap; see clean_text_with_config).
        text = text[:max_chars].strip()

        if self._utf16_len(text) < 100:
            return QualityPattern.TOO_SHORT

        words = text.split()
        if len(words) < 20:
            return QualityPattern.TOO_FEW_WORDS

        avg_word_length = sum(self._utf16_len(word) for word in words) / len(words)
        if avg_word_length < 3:
            return QualityPattern.AVG_WORD_TOO_SHORT
        if avg_word_length > 15:
            return QualityPattern.AVG_WORD_TOO_LONG

        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / self._utf16_len(text)
        if special_char_ratio > 0.3:
            return QualityPattern.TOO_MANY_SPECIAL

        unique_words = len(set(w.lower() for w in words))
        if unique_words / len(words) < min_unique_word_ratio:
            return QualityPattern.TOO_REPETITIVE

        lines = [line for line in text.split('\n') if line.strip()]
        if lines:
            avg_line_length = sum(self._utf16_len(line) for line in lines) / len(lines)
            if avg_line_length < 20 and len(lines) > 10:
                return QualityPattern.LINES_TOO_SHORT

        return QualityPattern.GOOD

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
        """Remove repeated 8+ word phrases (nav menus, footers, boilerplate that repeats across pages
        without punctuation), keeping the first occurrence. Tokenize once, mark the copies, rebuild
        once. See the helpers for the single-pass / non-idempotent rationale and the whitespace-set
        subtlety that keeps this byte-identical to the reference engine."""
        words = self._phrase_word_ranges(text)
        if len(words) < min_words:
            return text
        deleted = self._phrase_mark_repeats(text, words, min_words, threshold)
        if deleted is None:
            return text  # nothing repeated -> leave text untouched (no rebuild, no flatten)
        return self._phrase_rebuild(text, words, deleted)

    def _phrase_word_ranges(self, text: str) -> list[tuple[int, int]]:
        """Word (start, end) char spans. Splits on the same whitespace set the reference C# engine's
        word tokenizer uses, which is str.isspace() MINUS U+001C-001F (FS/GS/RS/US): .NET
        char.IsWhiteSpace excludes those four, str.isspace() includes them. This pass runs before
        whitespace normalisation, so those chars can still be present - a plain str.split() here would
        tokenise them differently from the reference engine and break cross-engine byte-identity."""
        ranges: list[tuple[int, int]] = []
        start = -1
        for i, c in enumerate(text):
            if c.isspace() and c not in '\x1c\x1d\x1e\x1f':
                if start != -1:
                    ranges.append((start, i))
                    start = -1
            elif start == -1:
                start = i
        if start != -1:
            ranges.append((start, len(text)))
        return ranges

    def _phrase_mark_repeats(
        self, text: str, words: list[tuple[int, int]], min_words: int, threshold: int
    ) -> list[bool] | None:
        """Mark copies of each repeated phrase for deletion, keeping the first occurrence; return the
        delete-mask, or None when nothing repeats so the caller leaves the text untouched. For each
        phrase length (longest first) the surviving windows are grouped by their word tuple and, where
        a group reaches the threshold, every window after the first is marked. Single descending pass,
        deliberately not a fixpoint: with this pass on the cleaner is intentionally non-idempotent, and
        production cleans raw text once, so re-cleaning is out of contract. A word tuple is equivalent
        to the reference engine's space-joined n-gram (words hold no separator), so it stands in for
        that engine's rolling hash - identical result except on a hash collision."""
        word_strs = [text[s:e] for s, e in words]  # materialize once; tuple keys avoid a per-window join
        deleted = [False] * len(words)
        changed = False
        for n in range(10, min_words - 1, -1):
            if len(words) < n:
                continue
            positions: dict[tuple[str, ...], list[int]] = {}
            for i in range(len(words) - n + 1):
                if any(deleted[i:i + n]):
                    continue
                key = tuple(word_strs[i:i + n])
                positions.setdefault(key, []).append(i)
            for idxs in positions.values():
                if len(idxs) >= threshold:
                    for i in idxs[1:]:
                        for w in range(n):
                            deleted[i + w] = True
                    changed = True
        return deleted if changed else None

    @staticmethod
    def _utf16_len(text: str) -> int:
        """UTF-16 code unit count (matching C# .Length). BMP code points count 1; non-BMP
        (astral) count 2. With default flags astral is stripped, so this equals len() on all
        cleaned text; the divergence only matters on the exclude_emoji=False path."""
        return len(text) + sum(1 for c in text if ord(c) > 0xFFFF)

    def _phrase_rebuild(self, text: str, words: list[tuple[int, int]], deleted: list[bool]) -> str:
        """Rebuild from the surviving words joined by single spaces - matches the reference engine,
        which flattens inter-word whitespace and newlines whenever it removes a phrase."""
        return ' '.join(text[s:e] for (s, e), d in zip(words, deleted) if not d)

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

            # Skip very short paragraphs (likely not meaningful duplicates). Measure the RAW trimmed
            # length (para is already stripped) to match C# `paraSpan.Length`, not the whitespace-
            # normalized length. The dedup KEY below stays normalized.
            if len(para) < 30:
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

            # Raw trimmed length (sentence is already stripped) to match C# `sentSpan.Length`;
            # dedup KEY stays normalized.
            if len(sentence) < 15:
                unique_sentences.append(sentence)
                continue

            if normalized not in seen:
                seen.add(normalized)
                unique_sentences.append(sentence)
            else:
                removed_count += 1

        if not unique_sentences:
            return '', removed_count
        joined = '. '.join(unique_sentences)
        # Don't append '.' if the last sentence already ends with sentence-ending
        # punctuation — avoids unbounded growth on re-clean (TS0017 period-bug).
        if joined and joined[-1] in '.!?':
            return joined, removed_count
        return joined + '.', removed_count

    def _normalize_whitespace(self, text: str) -> str:
        """Verbatim port of the C# NormalizeWhitespace state machine, NOT a regex.
        Byte-identity with C# is the contract, and the edges (whitespace after a newline absorbed,
        leading whitespace dropped, CR dropped, newlines capped at 2, space-before vs after-newline
        asymmetric) are what a regex near-matches and gets wrong. Replaces the old space-only
        `re.sub(' +',...)` which kept tabs and handled CR only incidentally."""
        out: list[str] = []
        newlines = 0
        in_space = False
        for c in text:
            if c == '\n':
                newlines += 1
                in_space = True
            elif c.isspace() and c != '\r' and c not in '\x1c\x1d\x1e\x1f':
                # collapse a run of non-newline whitespace to ONE space - but only mid-line
                # (newlines==0) and never as a leading char (out non-empty).
                # The `c not in '\x1c..\x1f'` guard matches C# char.IsWhiteSpace: Python's
                # str.isspace() treats the C0 separators FS/GS/RS/US as whitespace and .NET does NOT, so
                # without this those 4 chars would collapse in py but survive as content in C# - breaking
                # byte-identity. They fall through to the else-branch (emitted as content), like C#.
                if not in_space and newlines == 0 and out:
                    out.append(' ')
                    in_space = True
            elif c == '\r':
                pass  # drop CR entirely
            else:
                if newlines > 0:
                    if out and out[-1] != '\n':
                        out.extend('\n' * min(newlines, 2))
                    newlines = 0
                out.append(c)
                in_space = False
        return ''.join(out).strip()
