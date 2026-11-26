"""Replay every archived Python file in its original archive context.

Archives are trusted fixed research artifacts verified against SHA-256.
Import-only modules are smoke checks, not experimental successes.
This is not a sandbox for arbitrary third-party code.
"""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import tempfile
import time
from zipfile import ZipFile
from scripts.verify_archives import verify

def classification(content):
    tree=ast.parse(content)
    for node in tree.body:
        if isinstance(node,ast.If) and '__name__' in ast.unparse(node.test):return 'entrypoint'
        if isinstance(node,(ast.For,ast.While,ast.With,ast.Try)):return 'entrypoint'
        if isinstance(node,ast.Expr) and not isinstance(node.value,ast.Constant):return 'entrypoint'
    return 'module_smoke'

def normalized(x):
    # Only wall-clock/process-resource measurements are excluded.
    if isinstance(x,dict):
        return {k:normalized(v) for k,v in x.items()
                if not any(s in k.lower() for s in ('time','seconds','cpu','duration','tracemalloc','rss','peak_mem'))}
    if isinstance(x,list):return [normalized(v) for v in x]
    return x

def replay(source,archive,manifest,out,timeout=240,workers=3):
    source,out=Path(source).resolve(),Path(out).resolve()
    names=verify(manifest,source)
    if archive not in names or not source.is_dir():raise ValueError('use verified archive directory')
    out.mkdir(parents=True,exist_ok=True)
    with ZipFile(source/archive) as z:
        members=z.namelist()
        if len(members)!=len(set(members)):raise ValueError('duplicate member')
        for name in members:
            p=PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or '\\' in name:raise ValueError('unsafe path')
        files=[n for n in members if n.endswith('.py')]
        originals={n:z.read(n) for n in members if n.endswith('.json')}
        kinds={}
        for name in files:
            content=z.read(name);compile(content,name,'exec');kinds[name]=classification(content)
    def run(name):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with ZipFile(source/archive) as z:z.extractall(root)
            path=root/name;tag=name.replace('/','__')
            log=out/(tag+'.log')
            before={n:(root/n).stat().st_mtime_ns for n in originals}
            started=time.monotonic()
            with log.open('wb') as stream:
                try:
                    r=subprocess.run([sys.executable,path.name],cwd=path.parent,stdout=stream,
                        stderr=subprocess.STDOUT,timeout=timeout,
                        env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1',
                             'MKL_NUM_THREADS':'1','PYTHONHASHSEED':'0'})
                    rc=r.returncode;status='pass' if rc==0 else 'fail'
                except subprocess.TimeoutExpired:rc=None;status='timeout'
            elapsed=round(time.monotonic()-started,3)
            comparisons=[]
            for f in root.rglob('*.json'):
                relative=f.relative_to(root).as_posix()
                if relative in before and f.stat().st_mtime_ns==before[relative]:continue
                data=f.read_bytes()
                generated=out/(tag+'__'+relative.replace('/','__'))
                generated.write_bytes(data)
                if relative not in originals:state='new'
                else:
                    try:state='match' if normalized(json.loads(data))==normalized(json.loads(originals[relative])) else 'different'
                    except (ValueError,TypeError):state='unparseable'
                comparisons.append(dict(path=relative,comparison=state,artifact=generated.name))
            row=dict(path=name,kind=kinds[name],status=status,returncode=rc,seconds=elapsed,
                     log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest(),comparisons=comparisons)
            print(json.dumps(row),flush=True)
            return row
    with ThreadPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(run,files))
    report=dict(archive=archive,python=platform.python_version(),timeout=timeout,workers=workers,
                rows=rows,compiled=len(files))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source');p.add_argument('archive');p.add_argument('--manifest',default='docs/ARCHIVES.sha256')
    p.add_argument('--output',required=True);p.add_argument('--timeout',type=int,default=240)
    p.add_argument('--workers',type=int,default=3);p.add_argument('--strict',action='store_true')
    a=p.parse_args()
    r=replay(a.source,a.archive,a.manifest,a.output,a.timeout,a.workers)
    print(json.dumps(dict(archive=r['archive'],compiled=r['compiled'],
          passes=sum(x['status']=='pass' for x in r['rows']),
          failures=sum(x['status']=='fail' for x in r['rows']),
          timeouts=sum(x['status']=='timeout' for x in r['rows']))),flush=True)
    # The default archive replay is diagnostic. Failed historic entrypoints
    # are reported, not conflated with integrity failures or unit-test passes.
    sys.exit(int(a.strict and any(x['status']!='pass' for x in r['rows'])))
