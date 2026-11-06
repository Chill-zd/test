"""Conservative descriptive phrase counting with hard TeX boundaries."""
import re


def prose_chunks(text):
    # No token sequence is joined across math, a command, its argument, a
    # reference/citation, comment, sentence or physical paragraph boundary.
    boundary = re.compile(r'(?<!\\)%[^\n]*|\$\$[\s\S]*?\$\$|(?<!\\)\$[^$]*\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\\[A-Za-z@]+\*?(?:\s*\[[^\]]*\])?(?:\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})*|[{}.!?;:]|\n\s*\n')
    return [re.findall(r"[a-z]+(?:'[a-z]+)?", part.lower()) for part in boundary.split(text) if part.strip()]


def phrase_count(chunks, phrase):
    pattern=phrase.split(); n=len(pattern)
    return sum(sum(tokens[i:i+n]==pattern for i in range(len(tokens)-n+1)) for tokens in chunks)
