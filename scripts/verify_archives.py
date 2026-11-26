"""Verify the historical ZIPs without extracting or executing their contents."""
import argparse
import hashlib
import io
from pathlib import Path
from zipfile import ZipFile


def verify(manifest, source):
    expected = {}
    for line in Path(manifest).read_text().splitlines():
        if not line.strip():
            continue
        digest, name = line.split()
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('invalid SHA-256')
        if Path(name).name != name or '/' in name or '\\' in name or name in expected or not name.endswith('.zip'):
            raise ValueError('invalid or duplicate archive name')
        expected[name] = digest
    if not expected:
        raise ValueError('empty manifest')
    def check(read):
        for name, digest in expected.items():
            data = read(name)
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError(f'hash mismatch: {name}')
            with ZipFile(io.BytesIO(data)) as archive:
                if archive.testzip() is not None:
                    raise ValueError(f'CRC failure: {name}')
        return sorted(expected)
    source = Path(source)
    if source.is_dir():
        return check(lambda name: (source / name).read_bytes())
    with ZipFile(source) as bundle:
        if len(bundle.namelist()) != len(set(bundle.namelist())):
            raise ValueError('duplicate bundle member')
        return check(bundle.read)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='Directory of ZIPs or combined historical bundle')
    parser.add_argument('--manifest', default='docs/ARCHIVES.sha256')
    args = parser.parse_args()
    for name in verify(args.manifest, args.source):
        print(f'OK {name}')


if __name__ == '__main__':
    main()
