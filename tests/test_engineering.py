import hashlib
import tempfile
import unittest
from pathlib import Path
from qcdt import contract
from qcdt.api import ResourcePolicy,recover_bounded
from scripts.evidence_manifest import manifest
from scripts.check_environment import verify
from importlib.metadata import version

class EngineeringTests(unittest.TestCase):
    def test_bounded_callback(self):
        E={(0,1,2)};calls=[]
        def p(a,b):
            calls.append((a,b));return contract(E,a,b)
        r=recover_bounded(6,1,1,p)
        self.assertEqual(r.edges,E)
        self.assertEqual(4*len(calls),r.acquisition_queries+r.verification_queries)
        count=len(calls)
        with self.assertRaisesRegex(ValueError,'cap'):recover_bounded(6,1,1,p,policy=ResourcePolicy(max_phase_queries=4))
        self.assertEqual(count,len(calls))
        with self.assertRaises(ValueError):recover_bounded(6,True,1,p)
        with self.assertRaises(ValueError):recover_bounded(6,1,1,lambda a,b:True)
    def test_evidence_and_lock(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'data';p.write_bytes(b'qcdt')
            self.assertEqual(manifest([p])[p.as_posix()]['sha256'],hashlib.sha256(b'qcdt').hexdigest())
            with self.assertRaises(ValueError):manifest([p,p])
            # pip is available on supported Python/CI installation environments.
            p.write_text('pip=='+version('pip')+'\n')
            self.assertEqual(verify(p),{'pip':version('pip')})
            p.write_text('pip==0\n')
            with self.assertRaises(RuntimeError):verify(p)
