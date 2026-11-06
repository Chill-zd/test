"""Citation identities from actual BibTeX or supplied compiled bibliography."""
from pathlib import Path
import re


def read_keys(path):
    from ..corpus.parser import strip_comments
    text=strip_comments(Path(path).read_text())
    bibtex=set(re.findall(r'@(?!(?:comment|string|preamble)\b)\w+\s*\{\s*([^,\s]+)',text,re.I))
    # Optional author/year labels can contain balanced braces and inner brackets.
    # Scan to its balanced closing ] before reading the actual bibitem key.
    bbl=set()
    for match in re.finditer(r'\\bibitem\b\s*',text):
        pos=match.end()
        if pos<len(text) and text[pos]=='[':
            depth=0;braces=0
            while pos<len(text):
                char=text[pos]
                if char=='{' and (pos==0 or text[pos-1]!='\\'):braces+=1
                elif char=='}' and (pos==0 or text[pos-1]!='\\'):braces-=1
                elif not braces:
                    if char=='[':depth+=1
                    elif char==']':
                        depth-=1
                        if not depth:pos+=1;break
                pos+=1
        key=re.match(r'\s*\{([^{}\s]+)\}',text[pos:])
        if key:bbl.add(key[1])
    return bibtex|bbl
