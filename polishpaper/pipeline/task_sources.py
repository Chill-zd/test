"""Freeze manuscript inputs while preserving, but not freezing, build outputs."""
from pathlib import Path
import hashlib,json,re,shutil

_AUXILIARY=('.aux','.log','.fdb_latexmk','.fls','.blg','.out','.toc','.lof','.lot','.bcf','.run.xml','.synctex.gz','.nav','.snm','.vrb')


def generated_paths(workspace,main):
    root=Path(workspace);main=Path(main);tex=root/main
    from ..corpus.parser import strip_comments
    bodies=[strip_comments(p.read_text(errors='replace')) for p in root.rglob('*.tex')]
    text='\n'.join(bodies)
    explicit_bbl={Path(v).name for v in re.findall(r'\\(?:input|include)\s*\{([^{}]+\.bbl)\}',text)}
    bibs=[name.strip() for group in re.findall(r'\\bibliography\s*\{([^{}]+)\}',text) for name in group.split(',')]
    bibs+=re.findall(r'\\addbibresource(?:\[[^\]]*\])?\s*\{([^{}]+)\}',text)
    # A supplied bbl without reproducible bibliography inputs is source material.
    reproducible=bool(bibs) and all(any((base/Path(name).with_suffix('.bib')).is_file() for base in (root,tex.parent)) for name in bibs)
    figure_names={Path(v).with_suffix('.pdf').name for v in re.findall(r'\\(?:includegraphics|includepdf)\*?(?:\[[^\]]*\])?\s*\{([^{}]+)\}',text)}
    found=set()
    for path in root.rglob('*'):
        if not path.is_file():continue
        rel=path.relative_to(root);name=path.name
        if name.endswith(_AUXILIARY):found.add(str(rel))
        elif rel==main.with_suffix('.pdf') and name not in figure_names:found.add(str(rel))
        elif rel==main.with_suffix('.bbl') and reproducible and name not in explicit_bbl:found.add(str(rel))
    return found


def preserve_generated_originals(task,source,main):
    """Save exact pre-task output bytes outside the editable workspace."""
    task=Path(task);source=Path(source);rows=[]
    candidates=generated_paths(source,main)
    if (source/Path(main).with_suffix('.bbl')).is_file():candidates.add(str(Path(main).with_suffix('.bbl')))
    for rel in sorted(candidates):
        original=source/rel;target=task/'original_build_artifacts'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target)
        rows.append({'relative_path':rel,'original_path':str(original.resolve()),'sha256':hashlib.sha256(original.read_bytes()).hexdigest()})
    (task/'original_build_artifacts.json').write_text(json.dumps({'schema':'original-build-artifacts-1','files':rows,'policy':'Original bytes preserved; regenerable build outputs are not frozen manuscript inputs. Figure PDFs and explicit/bbl-only inputs remain frozen.'},indent=2)+'\n')
    return rows
