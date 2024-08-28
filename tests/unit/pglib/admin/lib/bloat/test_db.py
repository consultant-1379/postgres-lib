import unittest2 as unittest
from mock import patch, Mock, PropertyMock

from pglib.admin.lib.bloat.db import FsData, get_bloat_table_data, \
    show_bloat_table

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


class TestFsData(unittest.TestCase):

    @patch('pglib.db.database.PgStore.databases', new_callable=PropertyMock)
    def testFsDataForADb(self, dbs):
        from pglib.db.database import DatabaseInstance
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        from pyu.os.fs.units import Size
        shell = Mock()
        shell.os.sg.pg.credentials_class = PgServiceGroupCenm.credentials_class
        credentials.setup(shell.os.sg.pg.credentials_class)
        db1 = DatabaseInstance('db-1', 1, Size('1G'))
        db2 = DatabaseInstance('db-2', 2, Size('2G'))
        dbs.return_value = [db1, db2]
        data = FsData(db2, shell)
        self.assertEqual(data.name, 'Db-2')
        self.assertEqual(data.db_size, Size('2G'))
        self.assertEqual(data.db_id, 2)

    @patch('pglib.db.database.DatabaseInstance')
    def test_bloat_data_returned(self, db):
        from pglib.db.database import Bloat
        bloat = [Bloat(*bloat) for bloat in RESULT]
        db.bloat = bloat
        self.assertEqual(get_bloat_table_data(db.bloat), [HEADER] + BODY)

    @patch('pglib.admin.lib.bloat.db.Table')
    @patch('pglib.admin.lib.bloat.db.get_bloat_table_data')
    @patch('pglib.db.database.DatabaseInstance')
    def test_bloat_shown(self, db, data, table):
        from pglib.db.database import Bloat
        data.return_value = [HEADER] + BODY
        bloat = [Bloat(*bloat) for bloat in RESULT]
        db.bloat = bloat
        show_bloat_table(db.bloat)
        self.assertTrue(table.call_count, 1)


if __name__ == '__main__':
    unittest.main()
