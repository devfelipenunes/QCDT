import hashlib
import json
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]/'evidence'/'2026-11-26'
class RawEvidenceTests(unittest.TestCase):
    def test_archive_integrity_and_reported_counts(self):
        expected={name:digest for digest,name in
                  (line.split() for line in (ROOT/'RAW_ARTIFACTS.sha256').read_text().splitlines())}
        self.assertEqual(len(expected),2)
        for name,digest in expected.items():
            p=ROOT/name
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),digest)
            with ZipFile(p) as z:self.assertIsNone(z.testzip())
        with ZipFile(ROOT/'run-45749367190-simulator-resources.zip') as z:
            r=json.loads(z.read('evidence/independent/results.json'))
            self.assertTrue(r['reverse_order_match'])
            self.assertEqual(len(r['rows']),230)
            self.assertTrue(all(x['outcome']=='exact' for x in r['rows']))
        with ZipFile(ROOT/'run-45749584325-oracle-boundary-evidence.zip') as z:
            rows=json.loads(z.read('oracle-boundary-results.json'))['rows']
            self.assertEqual(len(rows),36)
            self.assertEqual(sum(x['condition']=='ideal' and x['outcome']=='exact' for x in rows),12)
            self.assertEqual(sum(x['condition']=='snapshot' and x['outcome']=='wrong' for x in rows),0)
