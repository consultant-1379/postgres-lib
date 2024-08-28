import unittest2 as unittest
from mock import Mock, patch

from pyu.os.fs.units import Size

from pglib.db.database import PgStore, DatabaseInstance, Table, Bloat
from pglib.env.cenm.credentials import PostgresUserEncryptedPasswordCenm
from pglib.env.credentials import PostgresEnmCredentialsGroup

PSQL_DB_SIZES = u'''id|name|size
123|richie|9000000
234|chantalle|1024000000
345|bobo|4096000000
 (3 rows)
'''

DBS = {'123': {'id': '123', 'name': 'richie', 'size': '9000000'},
       '234': {'id': '234', 'name': 'chantalle', 'size': '1024000000'},
       '345': {'id': '345', 'name': 'bobo', 'size': '4096000000'}}

SESSION_TABLE_LIST = [{'test_table1', '1704 kB' '2433'},
                      {'test_table2', '736 kB', '263'},
                      {'test_table3', '32 kB', '14'}]

BLOAT_LIST = [('test_table1', 1, 0, 2, 0, 8, 0, None, 2, None),
              ('test_table2', 0, 1, 0, 1, 4, 0, None, 2, None),
              ('test_table3', 13, 0, 0, 0, 0, 0, None, 2, None)]


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.shell = Mock()
        self.credentials = PostgresEnmCredentialsGroup()
        self.credentials.setup(PostgresUserEncryptedPasswordCenm)
        self.store = PgStore(self.shell)

    def tearDown(self):
        self.shell = None
        self.credentials = None
        self.store = None

    @patch('pglib.postgres.PsqlClient.run')
    def test_get_database_data_returns_dict(self, _run):
        _run.return_value = PSQL_DB_SIZES
        actual = self.store._get_databases_data()
        self.assertEqual(DBS, actual)

    @patch('pglib.postgres.PsqlClient.run')
    def test_get_database_data_return_empty_list(self, _run):
        _run.return_value = []
        actual = self.store._get_databases_data()
        self.assertEqual([], actual)

    @patch('pglib.postgres.PsqlClient.run')
    def test_databases_returns_instances_of_dbs(self, _run):
        _run.return_value = PSQL_DB_SIZES
        dbs = self.store.databases
        self.assertIsInstance(dbs, list)
        self.assertIsInstance(dbs[0], DatabaseInstance)
        self.assertEqual(len(dbs), 3)

    @patch('pglib.postgres.PsqlClient.run')
    def test_databases_returns_none_if_no_dbs(self, _run):
        _run.return_value = []
        actual = self.store.databases
        self.assertEqual(len(actual), 0)

    @patch('pglib.db.database.PostgresSession')
    def test_tables_returns_instances_of_tables(self, session):
        session.return_value.__enter__.return_value.fetchall \
            .return_value = SESSION_TABLE_LIST
        database = DatabaseInstance(name='db1', id='456', size=Size('1024M'))
        tables = database.tables
        self.assertIsInstance(tables, list)
        self.assertIsInstance(tables[0], Table)
        self.assertEqual(len(tables), 3)

    @patch('pglib.db.database.PostgresSession')
    def test_tables_returns_empty_list(self, session):
        session.return_value.__enter__.return_value.fetchall \
            .return_value = []
        database = DatabaseInstance(name='db1', id='456', size=Size('1024M'))
        tables = database.tables
        self.assertEqual(len(tables), 0)

    @patch('pglib.db.database.PostgresSession')
    def test_bloat_returns_instances_of_bloat(self, session):
        session.return_value.__enter__.return_value.fetchall \
            .return_value = BLOAT_LIST
        database = DatabaseInstance(name='db1', id='456', size=Size('1024M'))
        bloat = database.bloat
        self.assertIsInstance(bloat, list)
        self.assertIsInstance(bloat[0], Bloat)
        self.assertEqual(bloat[2].rows, 13)
        self.assertEqual(len(bloat), 3)

    @patch('pglib.db.database.PostgresSession')
    def test_bloat_returns_empty_list(self, session):
        session.return_value.__enter__.return_value.fetchall \
            .return_value = []
        database = DatabaseInstance(name='db1', id='456', size=Size('1024M'))
        bloat = database.bloat
        self.assertEqual(len(bloat), 0)


class TestDatabaseInstance(unittest.TestCase):

    def test_database_representation(self):
        self.assertEqual('DB: noah | ID: 456 | Size: 1G',
                         repr(DatabaseInstance(name='noah', id='456',
                                               size=Size('1024M'))))

    def test_database_string_representation(self):
        self.assertEqual('noah | 1G',
                         str(DatabaseInstance(name='noah', id='456',
                                              size=Size('1024M'))))


class TestTableInstance(unittest.TestCase):

    def test_table_representation(self):
        self.assertEqual('Table: test_table | Size: ' + str(Size('1704 kB'))
                         + ' | Rows: 983', str(Table(table_name='test_table',
                                                     size='1704 kB',
                                                     row_count='983')))


class TestBloatInstance(unittest.TestCase):

    def test_bloat_properties_get_set(self):
        bloat = Bloat(*BLOAT_LIST[2])
        self.assertEqual('test_table3', bloat.table)
        self.assertEqual(13, bloat.rows)
        self.assertEqual(0, bloat.inserts)
        self.assertEqual(0, bloat.updates)
        self.assertEqual(0, bloat.deletes)
        self.assertEqual(0, bloat.bloat)
        self.assertEqual(0, bloat.autovac)
        self.assertEqual(None, bloat.last_autovac)
        self.assertEqual(2, bloat.analayze)
        self.assertEqual(None, bloat.last_autoanalayze)


if __name__ == '__main__':
    unittest.main(verbosity=2)
