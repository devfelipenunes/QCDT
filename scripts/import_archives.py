"""Stage verified historical archives and member inventory without modifying bytes."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
from scripts.verify_archives import verify

def stage(source, manifest, destination):
    names=verify(manifest,source)
    source,destination=Path(source),Path(destination)
    payloads={}
    if source.is_dir():
        payloads={name:(source/name).read_bytes() for name in names}
    else:
        with ZipFile(source) as z:
            payloads={name:z.read(name) for name in names}
    # Validate the exact payloads to be written (not just the original path).
    expected=dict((name,digest) for digest,name in
                  (line.split() for line in Path(manifest).read_text().splitlines() if line.strip()))
    rows=[]
    for name,data in payloads.items():
        if hashlib.sha256(data).hexdigest()!=expected[name]:
            raise ValueError('archive changed after verification')
        with ZipFile(io.BytesIO(data)) as z:
            seen=set()
            for info in z.infolist():
                p=PurePosixPath(info.filename)
                if p.is_absolute() or '..' in p.parts or '\\' in info.filename or info.filename in seen:
                    raise ValueError('unsafe or duplicate archive member')
                seen.add(info.filename)
                if info.is_dir(): continue
                content=z.read(info)
                rows.append(dict(archive=name,path=info.filename,bytes=len(content),
                                 sha256=hashlib.sha256(content).hexdigest()))
    destination.mkdir(parents=True,exist_ok=True)
    inventory=json.dumps(sorted(rows,key=lambda r:(r['archive'],r['path'])),indent=2)+'\n'
    outputs={**payloads,'inventory.json':inventory.encode()}
    for name,data in outputs.items():
        p=destination/name
        if p.is_symlink() or (p.exists() and p.read_bytes()!=data):
            raise ValueError(f'refusing to overwrite {p}')
    for name,data in outputs.items():
        p=destination/name
        if not p.exists(): p.write_bytes(data)
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source')
    p.add_argument('--manifest',default='docs/ARCHIVES.sha256')
    p.add_argument('--destination',default='historical/archives')
    a=p.parse_args()
    rows=stage(a.source,a.manifest,a.destination)
    print(f'Staged {len({x["archive"] for x in rows})} ZIPs, {len(rows)} members')
