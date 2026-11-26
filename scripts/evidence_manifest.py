"""Hash exact benchmark artifact files; do not hash a manifest into itself."""
import argparse
import hashlib
import json
import os
from pathlib import Path

def manifest(paths):
    records={}
    for path in paths:
        p=Path(path)
        if p.as_posix() in records:raise ValueError('duplicate path')
        data=p.read_bytes()
        records[p.as_posix()]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    return records

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('files',nargs='+')
    a=p.parse_args()
    if Path(a.output).resolve() in {Path(x).resolve() for x in a.files}:raise ValueError('self reference')
    result=dict(schema='qcdt-artifacts-v1',git_sha=os.getenv('GITHUB_SHA'),run_id=os.getenv('GITHUB_RUN_ID'),
                files=manifest(a.files))
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
