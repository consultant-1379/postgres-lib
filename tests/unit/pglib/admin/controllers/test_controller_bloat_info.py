import unittest2 as unittest
from mock import patch, Mock

RESULT = [('act_ru_job', 6, 47623, 28466, 47623, 528, 46,
           '2021-11-25 15:21:54.551008+00', 170,
           '2021-11-25 15:03:54.494919+00'),
          ('act_ru_execution', 23, 34735, 47623, 34735, 384, 34,
           '2021-11-25 15:23:54.56314+00', 170,
           '2021-11-25 15:09:54.507483+00')]

HEADER = ['Table', 'Row Count', 'Inserts', 'Updates', 'Deletes', 'Bloat',
          'Autovac Count', 'Last Autovac', 'Analyze Count', 'Last Autoanalyze']

BODY = [
    ['act_ru_job', 6, 47623, 28466, 47623, 528, 46,
     '2021-11-25 15:21:54.551008+00', 170, '2021-11-25 15:03:54.494919+00'],
    ['act_ru_execution', 23, 34735, 47623, 34735, 384, 34,
     '2021-11-25 15:23:54.56314+00', 170, '2021-11-25 15:09:54.507483+00']]


class TestControllerBloatInfo(unittest.TestCase):

    def setUp(self):
        from pglib.admin.controllers.bloat_info import BloatController
        self.shell = Mock()
        self.bloat = BloatController(self.shell)

    @patch('pglib.db.database.DatabaseInstance')
    def test_bloat_table_returned(self, db):
        from pglib.db.database import Bloat
        bloat = [Bloat(*bloat) for bloat in RESULT]
        db.bloat = bloat
        self.assertEqual(self.bloat.execute(db.bloat), [HEADER] + BODY)

    def test_table_size_class_attributes(self):
        self.assertEqual(self.bloat.name, 'bloat_info')
        self.assertEqual(self.bloat.title, 'Bloat Information')


if __name__ == '__main__':
    unittest.main()
