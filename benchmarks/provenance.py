"""Order-independent experiment identities and canonical scientific records."""
import hashlib
import json
from random import Random

SCHEMA="qcdt-experiment-v1"

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def seed_for(master,case,stream):
    return int(digest([SCHEMA,master,case,stream])[:16],16)

def rng_for(master,case,stream):
    return Random(seed_for(master,case,stream))

def scientific_fields(row):
    """Explicit allowlist: new/unknown fields cannot silently affect this schema."""
    keys=('schema','case','instance_sha256','seeds','terms','method','outcome',
          'recovered','query_model','acquisition_queries','verification_queries','queries')
    return {key:row[key] for key in keys}

def compare(left,right):
    def indexed(rows):
        result={}
        for row in rows:
            science=scientific_fields(row)
            key=canonical([science['case'],science['method']])
            if key in result:raise ValueError('duplicate experiment key')
            result[key]=science
        return result
    return indexed(left)==indexed(right)
