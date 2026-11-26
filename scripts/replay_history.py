"""Replay selected original scripts in isolated temporary directories.

Run only against the trusted, SHA-256 verified historical bundle. Scripts are
research code, not sandboxed untrusted executables. A timeout is not a pass.
"""
import argparse
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
from concurrent.futures import ThreadPoolExecutor
from scripts.verify_archives import verify

JOBS = (
    ('bundle','qcdt.py'), ('round4','validation.py'),
    ('round5','graph_validation.py'), ('round6','lower_bound.py'),
    ('round6','graph_dynamic.py'), ('round7','run_circuit.py'),
    ('round7','crt.py'), ('round8','structural_tests.py'),
    ('round9','certification.py'), ('round9','crosscheck.py'),
    ('round10','noise_audit.py'), ('round11','audit.py'),
    ('round12','audit.py'), ('round12','outer_code.py'),
)

def replay(source, manifest, output, timeout=120, workers=2, selected=JOBS):
    source, output = Path(source).resolve(), Path(output).resolve()
    verify(manifest, source)
    output.mkdir(parents=True, exist_ok=True)
    if not (timeout > 0 and workers > 0):
        raise ValueError('timeout and workers must be positive')
    if not selected or len(set(selected)) != len(selected) or any(j not in JOBS for j in selected):
        raise ValueError('select distinct known jobs')
    def run(job):
        label, script = job
        name = f'quantum_research_{label}.zip'
        if source.is_dir():
            data = (source/name).read_bytes()
        else:
            with ZipFile(source) as z: data = z.read(name)
        with tempfile.TemporaryDirectory() as tmp, ZipFile(io.BytesIO(data)) as z:
            for member in z.infolist():
                p = PurePosixPath(member.filename)
                if p.is_absolute() or '..' in p.parts or '\\' in member.filename:
                    raise ValueError('unsafe archive member')
            z.extractall(tmp)
            scripts = list(Path(tmp).rglob(script))
            if len(scripts) != 1:
                raise ValueError(f'ambiguous script {job}')
            p = scripts[0]
            log = output / f'{label}_{script}.log'
            started = time.monotonic()
            with log.open('wb') as stream:
                try:
                    result = subprocess.run([sys.executable,p.name], cwd=p.parent,
                        stdout=stream, stderr=subprocess.STDOUT, timeout=timeout,
                        env={**os.environ,'OPENBLAS_NUM_THREADS':'1',
                             'OMP_NUM_THREADS':'1','PYTHONHASHSEED':'0'})
                    code = result.returncode
                    status = 'pass' if code == 0 else 'fail'
                except subprocess.TimeoutExpired:
                    code, status = None, 'timeout'
            return dict(round=label,script=script,status=status,returncode=code,
                seconds=round(time.monotonic()-started,3),
                log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(run, selected))
    report = dict(python=platform.python_version(),timeout_seconds=timeout,
                  workers=workers,rows=rows)
    (output/'replay.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--manifest',default='docs/ARCHIVES.sha256')
    parser.add_argument('--output',required=True)
    parser.add_argument('--timeout',type=float,default=120)
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--job',action='append',choices=[':'.join(j) for j in JOBS])
    args=parser.parse_args()
    jobs=tuple(tuple(j.split(':')) for j in args.job) if args.job else JOBS
    result=replay(args.source,args.manifest,args.output,args.timeout,args.workers,jobs)
    print(json.dumps(result,indent=2))
    sys.exit(0 if all(r['status']=='pass' for r in result['rows']) else 1)
