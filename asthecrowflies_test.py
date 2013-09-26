# http://www.greatcirclemapper.net/

import unittest
from asthecrowflies import load_airports, asthecrowflies


class Test(unittest.TestCase):

    def setUp(self):
        self.airports = load_airports('us_airports.csv')  # openflights.org

    def tearDown(self):
        pass

    def test_SFO_to_LAX(self):
        self.assertAlmostEqual(asthecrowflies(self.airports, 'LAX', 'SFO'),
                               293,
                               delta=10)

    def test_BWI_to_HNL(self):
        self.assertAlmostEqual(asthecrowflies(self.airports, 'BWI', 'HNL'),
                               4219,
                               delta=10)

    def test_ANC_to_MCO(self):
        self.assertAlmostEqual(asthecrowflies(self.airports, 'ANC', 'MCO'),
                               3317,
                               delta=10)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
