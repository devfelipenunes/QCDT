"""Isolated access to the verified original research implementations.

Exact v0.4/v0.5; BSC sample callback for v0.8 and simplex. The worker
receives only masks and measured bits, not the hidden tensor. Archived
code is trusted research code, not a security sandbox.
"""
from dataclasses import dataclass
import json
import os
from pathlib import Path
from queue import Queue, Empty
from random import Random
import subprocess
import sys
import tempfile
from threading import Thread
import time

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = {'v0.4': 'round5', 'v0.5': 'round6', 'v0.8': 'round10',
            'v0.10-simplex': 'round12'}

@dataclass(frozen=True)
class LegacyResult:
    version: str
    edges: frozenset | None
    acquisition_queries: int
    verification_queries: int
    reason: str | None


def recover_legacy(version, n, d, codegree, sample, *, eta=0.0,
                   observations=None, seed=42, checks=10, delta=.01, timeout=120):
    """Each sample(a,b) is one n-bit observation (four phase-oracle calls).

    eta is the independent stationary bit-flip rate assumed by statistical
    decoders. Exact versions require eta=0. Set observations for exploratory
    v0.8 budgets; such a budget need not meet the theoretical bound.
    The worker has a finite protocol timeout; a callback may have its own timeout.
    """
    if version not in VERSIONS or not 3<=n or not 1<=codegree<=d:
        raise ValueError('invalid version or promise')
    if not 0<=eta<.5 or not 0<delta<1 or checks<1 or timeout<=0:
        raise ValueError('invalid recovery settings')
    if eta and version in ('v0.4','v0.5'):raise ValueError('exact version requires eta=0')
    if observations is not None and (version!='v0.8' or observations<1):
        raise ValueError('observations only apply to v0.8')
    config=dict(version=version,n=n,d=d,codegree=codegree,eta=eta,observations=observations,
                seed=seed,checks=checks,delta=delta)
    env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PYTHONHASHSEED':'0'}
    with tempfile.TemporaryFile(mode='w+t') as err:
        p=subprocess.Popen([sys.executable,'-m','qcdt.legacy','--worker'],cwd=ROOT,env=env,
                           stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,bufsize=1)
        q=Queue()
        def reader():
            for line in p.stdout:q.put(line)
            q.put(None)
        thread=Thread(target=reader,daemon=True);thread.start()
        def send(x):p.stdin.write(json.dumps(x)+'\n');p.stdin.flush()
        start=time.monotonic();counts={'acquisition':0,'verification':0}
        try:
            send(config)
            while True:
                remaining=timeout-(time.monotonic()-start)
                if remaining<=0:raise TimeoutError('legacy worker timeout')
                try:line=q.get(timeout=remaining)
                except Empty as e:raise TimeoutError('legacy worker timeout') from e
                if line is None:
                    err.seek(0);raise RuntimeError('legacy worker exited: '+err.read()[-1000:])
                msg=json.loads(line)
                if msg['type']=='probe':
                    a,b=msg['a'],msg['b'];phase=msg['phase']
                    if phase not in counts or not 0<=a<1<<n or not 0<=b<1<<n:
                        raise RuntimeError('invalid worker request')
                    v=sample(a,b)
                    if not isinstance(v,int) or not 0<=v<1<<n:raise ValueError('invalid probe response')
                    counts[phase]+=4;send(v)
                elif msg['type']=='result':
                    edges=None if msg['edges'] is None else frozenset(tuple(e) for e in msg['edges'])
                    return LegacyResult(version,edges,counts['acquisition'],counts['verification'],msg['reason'])
                else:raise RuntimeError(msg.get('error','invalid worker message'))
        finally:
            if p.poll() is None:p.terminate()
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:p.kill();p.wait()
            p.stdin.close();p.stdout.close();thread.join(timeout=1)


def worker():
    from contextlib import redirect_stdout
    import hashlib
    import importlib
    import math
    from pathlib import PurePosixPath
    from zipfile import ZipFile
    from .core import bounds,contract
    output=sys.stdout
    def send(x):output.write(json.dumps(x)+'\n');output.flush()
    cfg=json.loads(sys.stdin.readline());n,d,lam=cfg['n'],cfg['d'],cfg['codegree']
    eta,version=cfg['eta'],cfg['version'];phase='acquisition'
    def probe(a,b):
        send(dict(type='probe',a=int(a),b=int(b),phase=phase))
        return int(json.loads(sys.stdin.readline()))
    def done(E,reason=None):send(dict(type='result',edges=None if E is None else sorted(E),reason=reason))
    try:
        name='quantum_research_'+VERSIONS[version]+'.zip'
        hashes={b:a for a,b in (line.split() for line in (ROOT/'docs/ARCHIVES.sha256').read_text().splitlines() if line.strip())}
        archive=ROOT/'historical/archives'/name
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=hashes[name]:raise RuntimeError('archive hash mismatch')
        with tempfile.TemporaryDirectory() as tmp, ZipFile(archive) as z, redirect_stdout(sys.stderr):
            for item in z.namelist():
                p=PurePosixPath(item)
                if p.is_absolute() or '..' in p.parts or '\\' in item:raise RuntimeError('unsafe archive path')
            z.extractall(tmp);sys.path.insert(0,str(Path(tmp)/('quantum_'+VERSIONS[version])))
            import numpy as np
            rng=np.random.default_rng(cfg['seed'])
            try:
                if version=='v0.4':
                    E,_=importlib.import_module('research').direct_recover(n,d,probe,compact=True)
                elif version=='v0.5':
                    E,_=importlib.import_module('weighted').recover(n,d,probe)
                elif version=='v0.8':
                    from codegree import draw,p_for,bound
                    from refinement import pooled
                    M=cfg['observations'] or bound(n,d,lam,eta,cfg['delta']/2)
                    A,B=draw(n,M,p_for(d,lam),rng)
                    Y=np.zeros((M,n),dtype=bool)
                    for j,(a,b) in enumerate(zip(A,B)):
                        y=probe(sum(1<<int(i) for i in np.flatnonzero(a)),sum(1<<int(i) for i in np.flatnonzero(b)))
                        Y[j]=[(y>>i)&1 for i in range(n)]
                    E=pooled(A,B,Y,d,lam)
                else:
                    from asymmetric import recover,cap_probes,Reject
                    from outer_code import block_plan,codebook
                    P=cap_probes(n,d,lam)
                    class ShotBlocks:
                        def block_acquire(self,a,bs):
                            out=[];off=0
                            for k,r in block_plan(len(bs),n,P,eta,cfg['delta']/2):
                                block=bs[off:off+k];off+=k;counts=[]
                                for c in range(1,1<<k):
                                    b=0
                                    for j,v in enumerate(block):
                                        if c>>j&1:b^=v
                                    ones=np.zeros(n,dtype=np.int32)
                                    if a and b and a!=b:
                                        for _ in range(r):
                                            y=probe(a,b)
                                            ones+=np.array([(y>>i)&1 for i in range(n)],dtype=np.int32)
                                    counts.append(ones)
                                score=codebook(k)@(r-2*np.asarray(counts));idx=score.argmin(0)
                                if np.any((score==score.min(0)).sum(0)>1):raise Reject('simplex tie')
                                for j in range(k):out.append(sum(1<<int(i) for i in np.flatnonzero(idx>>j&1)))
                            return out
                    E,_=recover(n,d,lam,ShotBlocks())
            except (AssertionError,ValueError,KeyError,ZeroDivisionError,IndexError) as e:
                done(None,'legacy decoder rejected: '+str(e));return
            if E is None:done(None,'legacy decoder rejected');return
            E={tuple(int(x) for x in e) for e in E}
            dg,cd=bounds(E)
            if dg>d or cd>lam or any(len(e)!=3 or tuple(sorted(set(e)))!=e or not 0<=e[0]<e[-1]<n for e in E):
                done(None,'invalid recovered structure');return
            phase='verification';random=Random(cfg['seed']+1)
            if eta==0:
                for _ in range(cfg['checks']):
                    a,b=random.getrandbits(n),random.getrandbits(n)
                    if probe(a,b)!=contract(E,a,b):done(None,'ideal holdout rejected');return
            else:
                gap=3*(1-2*eta)/16;M=math.ceil(math.log(2*n/cfg['delta'])/(2*gap*gap));errors=[0]*n
                for _ in range(M):
                    a,b=random.getrandbits(n),random.getrandbits(n);v=probe(a,b)^contract(E,a,b)
                    for i in range(n):errors[i]+=v>>i&1
                if any(e/M>eta+gap for e in errors):done(None,'BSC holdout rejected');return
            done(E)
    except Exception as e:send(dict(type='error',error=type(e).__name__+': '+str(e)))

if __name__=='__main__':
    if sys.argv[1:]!=['--worker']:raise SystemExit('use recover_legacy()')
    worker()
