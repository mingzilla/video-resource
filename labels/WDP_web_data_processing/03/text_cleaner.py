#!/usr/bin/env python3
"""Clean HTML text from stdin. Used by web_fetch.sh."""

import re
import sys
from collections import Counter


def clean_text(text, n_gram_min_phrase_words=8, n_gram_repeat_threshold=3, quality_min_unique_word_ratio=0.15):
    css_pattern = re.compile(r'<style[^>]*>.*?</style>', re.DOTALL | re.IGNORECASE)
    js_pattern = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL | re.IGNORECASE)
    html_tag_pattern = re.compile(r'<[^>]+>')
    css_property_pattern = re.compile(r'\{[^}]*\}')

    # Remove CSS, JS, HTML tags, CSS properties
    text = css_pattern.sub('', text)
    text = js_pattern.sub('', text)
    text = html_tag_pattern.sub('', text)
    text = css_property_pattern.sub('', text)

    # Remove metadata patterns
    for pattern in [r'charset=[\w-]+', r'encoding=[\w-]+', r'content-type:[\w\s/;=-]+',
                    r'viewport[\w\s:;=",-]+', r'http-equiv[\w\s:;=",-]+']:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Deduplicate paragraphs
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    seen = set()
    unique_paragraphs = []
    for para in paragraphs:
        normalized = ' '.join(para.split())
        if len(normalized) < 30 or normalized not in seen:
            seen.add(normalized)
            unique_paragraphs.append(para)
    text = '\n\n'.join(unique_paragraphs)

    # Deduplicate sentences
    sentences = re.split(r'[.!?]+\s+', text)
    normalized_sentences = []
    original_sentences = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        normalized = ' '.join(s.split())
        if len(normalized) < 15:
            continue
        normalized_sentences.append(normalized)
        original_sentences.append(s)

    sentence_counts = Counter(normalized_sentences)
    boilerplate = {s for s, c in sentence_counts.items() if c >= 3}
    seen = set()
    unique_sentences = []
    for original, normalized in zip(original_sentences, normalized_sentences):
        if normalized in boilerplate:
            continue
        if normalized not in seen:
            seen.add(normalized)
            unique_sentences.append(original)
    text = '. '.join(unique_sentences) + '.' if unique_sentences else ''

    # Remove repeated phrases
    words = text.split()
    if len(words) >= n_gram_min_phrase_words:
        for n in range(10, n_gram_min_phrase_words - 1, -1):
            if len(words) < n:
                continue
            ngram_counts = Counter()
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i + n])
                ngram_counts[ngram] += 1
            for ngram, count in ngram_counts.items():
                if count >= n_gram_repeat_threshold:
                    text = text.replace(ngram, ' ')
            words = text.split()

    # Normalize whitespace
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines).strip()

    # Quality check
    if not text or len(text) < 100:
        print(f"[quality filter: too short ({len(text)} chars)]", file=sys.stderr)
        print(text)
        return
    w = text.split()
    if len(w) < 20:
        print(f"[quality filter: too few words ({len(w)})]", file=sys.stderr)
        print(text)
        return
    unique_words = len(set(word.lower() for word in w))
    if unique_words / len(w) < quality_min_unique_word_ratio:
        print(f"[quality filter: too repetitive ({unique_words}/{len(w)} unique)]", file=sys.stderr)
        print(text)
        return

    print(text)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    n_gram_threshold = 10**9 if '--no-ngrams' in sys.argv else 3
    clean_text(sys.stdin.read(), n_gram_repeat_threshold=n_gram_threshold)
