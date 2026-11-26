import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from scripts.verify_archives import verify


class ArchiveTests(unittest.TestCase):
    def test_directory_bundle_and_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            buf = io.BytesIO()
            with ZipFile(buf, 'w') as z:
                z.writestr('result.json', '{}')
            data = buf.getvalue()
            name = 'round.zip'
            digest = hashlib.sha256(data).hexdigest()
            manifest = root / 'manifest'
            manifest.write_text(f'{digest}  {name}\n')
            (root / name).write_bytes(data)
            bundle = root / 'bundle.zip'
            with ZipFile(bundle, 'w') as z:
                z.writestr(name, data)
            self.assertEqual(verify(manifest, root), [name])
            self.assertEqual(verify(manifest, bundle), [name])
            (root / name).write_bytes(data + b'changed')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                verify(manifest, root)
            (root / name).unlink()
            with self.assertRaises(FileNotFoundError):
                verify(manifest, root)
            manifest.write_text(f'{digest}  ../{name}\n')
            with self.assertRaisesRegex(ValueError, 'invalid'):
                verify(manifest, bundle)
