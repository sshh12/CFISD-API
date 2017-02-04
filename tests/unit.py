import unittest
import os.path

from cfisdapi.grades import HomeAccessCenter


class GradesTest(unittest.TestCase):

    def _load(self, filename):
        with open(os.path.join('tests','data', filename + '.html'), 'r') as f:
            return f.read()

    def test_letters(self):
        c = HomeAccessCenter('s123456')

        self.assertEqual(c._get_letter_grade('90%'),   'A')
        self.assertEqual(c._get_letter_grade('89.5%'), 'A')
        self.assertEqual(c._get_letter_grade('85%'),   'B')
        self.assertEqual(c._get_letter_grade('70%'),   'C')
        self.assertEqual(c._get_letter_grade('0.0%'),  'F')
        self.assertEqual(c._get_letter_grade(''),      '')

    def test_honors(self):
        c = HomeAccessCenter('s123456')
        
        self.assertEqual(c._is_honors("U S History AP"), True)
        self.assertEqual(c._is_honors("AP Physics I"), True)
        self.assertEqual(c._is_honors("CHEMISTRY AP"), True)
        self.assertEqual(c._is_honors("ADV COM SCI K"), True)
        self.assertEqual(c._is_honors("Pre-Calculus K"), True)
        self.assertEqual(c._is_honors("Eng III AP"), True)

        self.assertEqual(c._is_honors("NotAnAP Class"), False)
        self.assertEqual(c._is_honors("Kinimatics On Level"), False)

    def test_reportcard(self):
        c = HomeAccessCenter('s123456')

        rc = c.get_reportcard(page=self._load("reportcard_2-3-2017"))

        for classid in rc:

            self.assertEqual(len(rc[classid]), 4)
            
            averages = rc[classid]['averages']
            self.assertEqual(len(averages), 6)

            for i in range(6):
                self.assertIn(averages[i]['letter'], ['A', 'B', 'D', 'F', ''])

        # Simple Spot Checks
        self.assertEqual(len(rc), 7)
        for i, a in enumerate(['93', '90', '93', '', '', '']):
            self.assertEqual(rc['03051 - 15']['averages'][i]['average'], a)

        self.assertEqual(rc['10351 - 6']['name'], 'U S History AP')
        self.assertEqual(rc['10351 - 6']['room'], '2211')
        self.assertEqual(rc['10351 - 6']['teacher'], 'Walter, Christian')

        self.assertEqual(rc['76501 - 1']['name'], 'Bnd IIIP/F-WD EN')

        self.assertEqual(rc['35151 - 3']['teacher'], 'Shull, Jeffrey C')
            
                
        

# TODO
#  - get_classwork
#  - get_org_news
#  - create_org_news

if __name__ == "__main__":
    unittest.main()
