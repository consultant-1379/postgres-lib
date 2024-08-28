import unittest2 as unittest
from mock import patch, Mock

from pyu.os.fs.units import Size

from pglib.admin.controllers.table_size import TableSizeController
from pglib.db.database import DatabaseInstance

RESULT = [('test_table1', '1704 kB', '2433'),
          ('test_table2', '736 kB', '263'),
          ('test_table3', '32 kB', '14')]

EXPECTED = [['Table Name', 'Table Size', 'Number of Rows'],
            ['test_table1', Size('1704 kB'), '2433'],
            ['test_table2', Size('736 kB'), '263'],
            ['test_table3', Size('32 kB'), '14']]


class TestTableSize(unittest.TestCase):

    def setUp(self):
        self.shell = Mock()
        self.db = DatabaseInstance('test_db', 1, '8G')
        self.tables = TableSizeController(self.shell)

    @patch('pglib.admin.controllers.table_size.MenuDb')
    @patch('pglib.db.database.DatabaseInstance._tables_data')
    def test_table_size_returned(self, dtd, menu):
        dtd.return_value = RESULT
        self.db._table_data = dtd
        menu.return_value.show.return_value = self.db
        self.assertEqual(self.tables.execute(self.tables.prompt()[0]),
                         EXPECTED)

    def test_table_size_class_attributes(self):
        self.assertEqual(self.tables.name, 'table_size')
        self.assertEqual(self.tables.title, 'Table Sizes')
        self.assertEqual(self.tables.rows_border, False)


if __name__ == '__main__':
    unittest.main()
