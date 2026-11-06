#!/usr/bin/env python3
"""Whitelist-only reproducible plugin staging; no install, inference, or data copying.

--check is read-only. --stage-only cleans/recreates plugin-dist/polishpaper.
--build stages and creates dist/polishpaper-VERSION-plugin.zip. No old bundle is read.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def encode(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def sha(data):return hashlib.sha256(data).hexdigest()


def collect(root):
    spec=json.loads((root/'scripts/plugin_package.json').read_text())
    if spec['schema']!='polishpaper-plugin-package-1':raise ValueError('Unknown package list schema')
    if set(spec['generated'])!={'.codex-plugin/plugin.json','PACKAGE_MANIFEST.json'}:
        raise ValueError('Generated package list differs from implemented metadata outputs')
    manifest=json.loads((root/'plugin.json').read_text())
    project=(root/'pyproject.toml').read_text().split('[project]',1)[1].split('\n[',1)[0]
    match=re.search(r'^version\s*=\s*"([^"]+)"',project,re.M)
    if not match or manifest['version']!=match[1]:raise ValueError('Plugin and Python package versions disagree')
    paths={root/name for name in spec['files']}
    for pattern in spec['globs']:
        matches=list(root.glob(pattern))
        if not matches:raise ValueError('Package glob matched no source: '+pattern)
        paths.update(matches)
    for relative in spec.get('excluded_files',[]):
        excluded=root/relative
        if excluded not in paths:raise ValueError('Excluded experimental source was not selected: '+relative)
        paths.remove(excluded)
    payload={}
    forbidden={'data','.venv','.venv-test','__pycache__','.git','plugin-dist','dist','build','.pytest_cache'}
    for path in sorted(paths):
        relative=path.relative_to(root)
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError('Invalid or missing package source: '+str(relative))
        if forbidden.intersection(relative.parts) or any(part.startswith('.env') or part.endswith('.egg-info') for part in relative.parts):
            raise ValueError('Runtime/private/generated source cannot enter package: '+str(relative))
        payload[relative.as_posix()]=path.read_bytes()
    # Generate compatibility metadata from the current source manifest. Never copy
    # the historical .codex-plugin descriptor or any prior installed plugin.
    payload['.codex-plugin/plugin.json']=encode({k:manifest[k] for k in ('name','version','description')}|{'skills':['skills/polishpaper']})
    receipt={'schema':'polishpaper-package-manifest-1','name':manifest['name'],'version':manifest['version'],'files':{name:sha(data) for name,data in sorted(payload.items())},'excludes':'Runtime data, source corpora, credentials, environments, caches and previous bundles are excluded by explicit package list.'}
    payload['PACKAGE_MANIFEST.json']=encode(receipt)
    return manifest['version'],payload


def stage(root,payload):
    parent=root/'plugin-dist';target=parent/'polishpaper'
    if parent.is_symlink() or target.is_symlink():raise ValueError('Refusing to clean a symlinked stage')
    if target.exists():shutil.rmtree(target)
    target.mkdir(parents=True)
    for name,data in sorted(payload.items()):
        path=target/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    return target


def build(root,version,payload):
    target=stage(root,payload);dist=root/'dist'
    if dist.is_symlink():raise ValueError('Refusing a symlinked archive directory')
    dist.mkdir(exist_ok=True);archive=dist/f'polishpaper-{version}-plugin.zip'
    if archive.is_symlink():raise ValueError('Refusing a symlinked archive file')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as output:
        for name,data in sorted(payload.items()):
            item=zipfile.ZipInfo(name,(1980,1,1,0,0,0));item.create_system=3;item.external_attr=0o100644<<16;item.compress_type=zipfile.ZIP_DEFLATED
            output.writestr(item,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(archive) as check:
        if check.testzip() is not None or set(check.namelist())!=set(payload):raise ValueError('Archive verification failed')
        if any(check.read(name)!=data for name,data in payload.items()):raise ValueError('Archive payload differs from staged source')
    return target,archive


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check',action='store_true',help='Read-only metadata and package-list validation')
    modes.add_argument('--stage-only',action='store_true',help='Recreate the clean local marketplace stage, without installing')
    modes.add_argument('--build',action='store_true',help='Recreate stage and deterministic plugin archive, without installing')
    args=parser.parse_args();version,payload=collect(ROOT)
    report={'version':version,'file_count':len(payload),'payload_sha256':sha(encode({name:sha(data) for name,data in sorted(payload.items())})),'installed':False}
    if args.build:
        target,archive=build(ROOT,version,payload);report.update(stage=str(target),archive=str(archive),archive_sha256=sha(archive.read_bytes()))
    elif args.stage_only:report['stage']=str(stage(ROOT,payload))
    else:report.update(mode='read_only_check',files=sorted(payload))
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
