"""Full research CI must execute every discovered test, with no skips."""
import sys
import unittest

def main():
    suite=unittest.defaultTestLoader.discover('tests')
    if not suite.countTestCases():raise RuntimeError('no tests discovered')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if result.skipped:
        print('Unexpected skipped tests:',result.skipped,file=sys.stderr)
    return int(not result.wasSuccessful() or bool(result.skipped))

if __name__=='__main__':sys.exit(main())
