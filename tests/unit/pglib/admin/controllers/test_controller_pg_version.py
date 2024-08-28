import unittest2 as unittest
from mock import Mock, patch

from pglib.admin.controllers.pg_version import PGVersionController
from pglib.errors import PsqlAuthenticationFailure, PsqlSessionException

EXPECTED = u"""  PostgreSQL Server Version:
  PostgreSQL 13.3 on x86_64-suse-linux-gnu, compiled by gcc (SUSE Linux) 7.5.0, 64-bit

  DocumentDB Version:
  6.1.0-26

  PostgreSQL Data Directory:
  /var/lib/postgresql/data/pgdata

  PostgreSQL Config File:
  /var/lib/postgresql/data/pgdata/postgresql.conf"""

VERSION = 'PostgreSQL 13.3 on x86_64-suse-linux-gnu, compiled by gcc ' \
          '(SUSE Linux) 7.5.0, 64-bit'
DATA_DIRECTORY = '/var/lib/postgresql/data/pgdata'
CONFIG_FILE = '/var/lib/postgresql/data/pgdata/postgresql.conf'
DOCDB_VERSION = '6.1.0-26'

MSG = 'Exception: Failed to retrieve Postgres Version information.\n' \
      'Please try again later.\nIf issue persists please contact customer ' \
      'support.'


class TestControllerPGVersion(unittest.TestCase):

    def setUp(self):
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        self.shell = Mock()
        self.shell.os.sg.pg.credentials_class = \
            PgServiceGroupCenm.credentials_class
        credentials.setup(self.shell.os.sg.pg.credentials_class)
        self.controller = PGVersionController(self.shell)

    def tearDown(self):
        self.shell = None
        self.controller = None

    @patch('pglib.admin.controllers.pg_version.PostgresVersion')
    def test_pg_version_ctl_returns_expected_values(self, pgv):
        pgv.return_value.version = VERSION
        pgv.return_value.data_directory = DATA_DIRECTORY
        pgv.return_value.config_file = CONFIG_FILE
        pgv.return_value.docdb_version = DOCDB_VERSION

        self.assertEqual(self.controller.execute(), EXPECTED)

    def test_class_attributes_are_set(self):
        self.assertEqual(self.controller.name, 'pg_version')
        self.assertEqual(self.controller.title, 'Postgres Version')


if __name__ == '__main__':
    unittest.main(verbosity=2)
