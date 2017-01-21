import unittest

from cfisdapi.grades import HomeAccessCenter

class GradesTest(unittest.TestCase):

    def test_letters(self):
        c = HomeAccessCenter('s123456')
        
        self.assertEqual(c._get_letter_grade('90%'),   'A')
        self.assertEqual(c._get_letter_grade('89.5%'), 'A')
        self.assertEqual(c._get_letter_grade('85%'),   'B')
        self.assertEqual(c._get_letter_grade('70%'),   'C')
        self.assertEqual(c._get_letter_grade('0.0%'),  'F')

if __name__ == "__main__":
    unittest.main()
