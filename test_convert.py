import unittest

from precompute import convert_to_int

class TestConvert(unittest.TestCase):
    def test_convert(self):
        self.assertEqual(convert_to_int('AAAAA'), 0)
        self.assertEqual(convert_to_int('BBBBB'), 0b00001_00001_00001_00001_00001)
        self.assertEqual(convert_to_int('ABCDE'), 0b00100_00011_00010_00001_00000)
        self.assertEqual(convert_to_int('ZZZZZ'), 0b11001_11001_11001_11001_11001)

if __name__ == "__main__":
    unittest.main()