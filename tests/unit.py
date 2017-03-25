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
        self.assertEqual(c._get_letter_grade('X'),     'U')

    def test_honors(self):
        c = HomeAccessCenter('s123456')
        
        self.assertEqual(c._is_honors("U S History AP"), True)
        self.assertEqual(c._is_honors("AP Physics I"), True)
        self.assertEqual(c._is_honors("CHEMISTRY AP"), True)
        self.assertEqual(c._is_honors("ADV COM SCI K"), True)
        self.assertEqual(c._is_honors("Pre-Calculus K"), True)
        self.assertEqual(c._is_honors("Eng III AP"), True)

        self.assertEqual(c._is_honors("NotAnAP Class"), False)
        self.assertEqual(c._is_honors("Kinematics On Level"), False)

    def test_reportcard(self):
        
        c = HomeAccessCenter('s123456')

        rc = c.get_reportcard(page=self._load("reportcard_2-3-2017"))

        self.assertEqual(rc['status'], 'success')

        self.assertEqual(len(rc), 8)

        for key in rc:
            
            if key != 'status':
                
                c = rc[key]

                self.assertEqual(len(c), 6)
                self.assertEqual(len(c['averages']), 6)
                self.assertEqual(len(c['exams']), 2)
                self.assertEqual(len(c['semesters']), 2)

        
        self.assertEqual(rc['03051 - 15']['teacher'], 'Rhodes, Ryan')
        self.assertEqual(rc['03051 - 15']['averages'][2]['average'], 93.0)
        self.assertEqual(rc['24111 - 15']['name'], 'Pre-Calculus K')
        self.assertEqual(rc['24111 - 15']['semesters'][0]['average'], 94.0)
        
            
                
        

# TODO
#  - get_classwork
#  - get_org_news
#  - create_org_news

if __name__ == "__main__":
    unittest.main()
