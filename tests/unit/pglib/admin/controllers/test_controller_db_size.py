import unittest2 as unittest
from mock import patch, Mock

from pyu.os.fs.units import Size
from pyu.ui.menuapp.controller import ControllerFailedException

DB_DATA = {'16401': {'id': '16401', 'name': 'flsdb', 'size': '8256647'},
           '18274': {'id': '18274', 'name': 'idenmgmt', 'size': '10280071'},
           '21683': {'id': '21683', 'name': 'kpiservdb', 'size': '8281223'},
           '21720': {'id': '21720', 'name': 'openidm', 'size': '12532871'},
           '21210': {'id': '21210', 'name': 'pkicdpsdb', 'size': '8061443'}}

EXPECTED = [['id', 'name', 'size'],
            ['16401', 'flsdb', Size('8256647')],
            ['18274', 'idenmgmt', Size('10280071')],
            ['21683', 'kpiservdb', Size('8281223')],
            ['21720', 'openidm', Size('12532871')],
            ['21210', 'pkicdpsdb', Size('8061443')]]

MSG = 'Failed to retrieve Postgres Db-Size information.\nPlease try again ' \
      'later.\nIf issue persists please contact customer support.'


class TestDbSizes(unittest.TestCase):
    def setUp(self):
        from pglib.admin.controllers.db_sizes import DbSizeController
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials

        self.shell = Mock()
        self.shell.os.sg.pg = PgServiceGroupCenm(shell=self.shell)
        credentials.setup(self.shell.os.sg.pg.credentials_class)
        self.db_sizes = DbSizeController(self.shell)

    @patch('pglib.db.database.PgStore._get_databases_data')
    @patch('pglib.admin.controllers.db_sizes.LocalShellClient')
    def test_db_size_returned(self, shell, db_data):
        db_data.return_value = DB_DATA
        self.assertEqual(self.db_sizes.execute(), EXPECTED)

    @patch('pglib.db.database.PgStore._get_databases_data')
    @patch('pglib.admin.controllers.db_sizes.LocalShellClient')
    def test_db_size_psql_exception(self, shell, db_data):
        from pglib.errors import PsqlAuthenticationFailure
        db_data.side_effect = PsqlAuthenticationFailure('Auth Failure for Bo')
        with self.assertRaises(PsqlAuthenticationFailure):
            self.db_sizes.execute()

    @patch('pglib.db.database.PgStore._get_databases_data')
    @patch('pglib.admin.controllers.db_sizes.LocalShellClient')
    def test_db_size_command_failed_exception(self, shell, db_data):
        from pyu.os.shell.errors import CommandFailed
        db_data.side_effect = CommandFailed(message='psql: command not found',
                                            output='Blah', status_code='RL69',
                                            cmd='psql SELECT richie')
        with self.assertRaises(CommandFailed):
            self.db_sizes.execute()

    def test_db_size_class_attributes(self):
        self.assertEqual(self.db_sizes.name, 'db_sizes')
        self.assertEqual(self.db_sizes.title, 'Databases Size')
        self.assertEqual(self.db_sizes.rows_border, False)


if __name__ == '__main__':
    unittest.main()
