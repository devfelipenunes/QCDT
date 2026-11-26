"""Verify all recorded package versions; emit environment provenance."""
import argparse
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import sys

def verify(lock):
    expected={}
    for line in Path(lock).read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#'):continue
        name,want=line.split('==',1)
        if name in expected:raise ValueError('duplicate package')
        expected[name]=want
    if not expected:raise ValueError('empty lock')
    actual={name:version(name) for name in expected}
    if actual!=expected:
        raise RuntimeError({k:(expected[k],v) for k,v in actual.items() if v!=expected[k]})
    return actual

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('lock');p.add_argument('--python',default='3.13.18')
    p.add_argument('--output',required=True);a=p.parse_args()
    if platform.python_version()!=a.python:raise RuntimeError('Python version differs from lock protocol')
    report=dict(python=platform.python_version(),implementation=platform.python_implementation(),
                platform=platform.platform(),machine=platform.machine(),processor=platform.processor(),
                runner_image=os.getenv('ImageOS'),runner_image_version=os.getenv('ImageVersion'),
                git_sha=os.getenv('GITHUB_SHA'),run_id=os.getenv('GITHUB_RUN_ID'),
                lock=a.lock,packages=verify(a.lock))
    Path(a.output).write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report),flush=True)
