import unittest
from benchmarks.independent import cases,run_case,instance
from benchmarks.provenance import seed_for,digest,compare

class ProvenanceTests(unittest.TestCase):
    def test_order_independent(self):
        a,b=cases()[:2]
        self.assertTrue(compare(run_case(a)+run_case(b),run_case(b)+run_case(a)))
        self.assertNotEqual(seed_for(1,a,'instance'),seed_for(1,a,'holdout'))
        self.assertNotEqual(digest(instance(a)[1]),digest(instance(b)[1]))
    def test_schema_and_duplicate(self):
        rows=run_case(cases()[0]);changed=[dict(x) for x in rows]
        changed[0]['queries']+=1
        self.assertFalse(compare(rows,changed))
        with self.assertRaises(ValueError):compare(rows+rows,rows)
