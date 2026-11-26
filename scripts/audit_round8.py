"""Reproduce the historical RNG-order discrepancy without changing archives."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from zipfile import ZipFile
from scripts.verify_archives import verify

def scientific_fields(rows):
    # Legacy compare_r8 raw method triples are [correct, queries, seconds].
    return [(r['n'],r['d'],r['reps'],
             [{m:v[:2] for m,v in case.items()} for case in r['raw']]) for r in rows]

def run(source,out):
    source,out=Path(source).resolve(),Path(out).resolve()
    verify('docs/ARCHIVES.sha256',source)
    archive=source/'quantum_research_round8.zip'
    out.mkdir(parents=True,exist_ok=True)
    with ZipFile(archive) as z:
        original=json.loads(z.read('quantum_round7/compare_r8.json'))
    results={}
    for name,args in [('isolated',['compare']),('sequential',['independent_full','compare'])]:
        with tempfile.TemporaryDirectory() as tmp:
            with ZipFile(archive) as z:z.extractall(tmp) # trusted hash-verified artifact
            root=Path(tmp)/'quantum_round7'
            with (out/(name+'.log')).open('wb') as stream:
                subprocess.run([sys.executable,'scientific_tests.py',*args],cwd=root,stdout=stream,
                    stderr=subprocess.STDOUT,check=True,timeout=180,
                    env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PYTHONHASHSEED':'0'})
            data=(root/'compare_r8.json').read_bytes()
            (out/(name+'.json')).write_bytes(data)
            rows=json.loads(data)
            results[name]=dict(matches_original=scientific_fields(rows)==scientific_fields(original),
                sha256=hashlib.sha256(data).hexdigest(),
                summary=[dict(n=r['n'],d=r['d'],methods={m:{k:v for k,v in x.items() if k!='median_seconds'}
                                                       for m,x in r['methods'].items()}) for r in rows])
    report=dict(original_archive=str(archive.name),results=results)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',default='historical/archives')
    p.add_argument('--output',required=True)
    a=p.parse_args()
    r=run(a.source,a.output)
    print(json.dumps(r,indent=2))
    if not r['results']['isolated']['matches_original']:raise SystemExit(1)
