import unittest

from precompute import convert_to_int, score

class TestConvert(unittest.TestCase):
    def test_convert(self):
        self.assertEqual(convert_to_int('AAAAA'), 0)
        self.assertEqual(convert_to_int('BBBBB'), 0b00001_00001_00001_00001_00001)
        self.assertEqual(convert_to_int('ABCDE'), 0b00100_00011_00010_00001_00000)
        self.assertEqual(convert_to_int('ZZZZZ'), 0b11001_11001_11001_11001_11001)

class TestScore(unittest.TestCase):
    def test_score(self):
        self.assertEqual(score(convert_to_int('BATHE'), convert_to_int('SPOON')), 0)
        self.assertEqual(score(convert_to_int('TRYST'), convert_to_int('TRYST')), 0b0101010101)
        # remember that these are stored in little endian order, i.e., first letter is the least 
        # significant
        self.assertEqual(score(convert_to_int('DRINK'), convert_to_int('DANDY')), 0b0010000001)

if __name__ == "__main__":
    unittest.main()