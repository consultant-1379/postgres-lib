import unittest2 as unittest
from mock import Mock, patch

from pyu.os.shell.errors import CommandFailed

from pglib.env.cenm.credentials import PostgresUserEncryptedPasswordCenm
from pglib.env.credentials import PostgresEnmCredentialsGroup
from pglib.env.version import PostgresVersion
from pglib.errors import InvalidDeploymentType, PsqlAuthenticationFailure, \
    PsqlSessionException

VERSION = 'PostgreSQL 13.3 on x86_64-suse-linux-gnu, compiled by gcc ' \
          '(SUSE Linux) 7.5.0, 64-bit'
DATA_DIRECTORY = '/var/lib/postgresql/data/pgdata'
CONFIG_FILE = '/var/lib/postgresql/data/pgdata/postgresql.conf'
DOCDB_VERSION = '6.1.0-26'

EXCEPTION_MSG = 'Invalid password'
MSG = 'Postgres session exception: ' + EXCEPTION_MSG
COMMAND_FAILED_MSG = 'kubectl: command not found'
INVALID_DEPLOYMENT_MSG = 'DocDB version is only applicable ' \
                         'for cENM deployments'


class TestVersion(unittest.TestCase):

    def setUp(self):
        self.shell = Mock()
        self.credentials = PostgresEnmCredentialsGroup()
        self.credentials.setup(PostgresUserEncryptedPasswordCenm)
        self.pgv = PostgresVersion(self.shell)

    def tearDown(self):
        self.shell = None
        self.credentials = None
        self.cluster = None
        self.terminal = None

    @patch('pglib.env.version.PostgresSession')
    def test_version_returns_successfully(self, psql):
        psql.return_value.__enter__.return_value.fetchone.return_value = (
            'PostgreSQL 13.3 on x86_64-suse-linux-gnu, compiled by '
            'gcc (''SUSE Linux) 7.5.0, 64-bit',)
        self.assertEqual(self.pgv.version, VERSION)

    @patch('pglib.env.version.PostgresSession')
    def test_config_file_returns_successfully(self, psql):
        psql.return_value.__enter__.return_value.fetchone.return_value = (
            '/var/lib/postgresql/data/pgdata/postgresql.conf',)
        self.assertEqual(self.pgv.config_file, CONFIG_FILE)

    @patch('pglib.env.version.PostgresSession')
    def test_data_directory_returns_successfully(self, psql):
        psql.return_value.__enter__.return_value.fetchone.return_value = (
            '/var/lib/postgresql/data/pgdata',)
        self.assertEqual(self.pgv.data_directory, DATA_DIRECTORY)

    def test_docdb_version_returns_successfully(self):
        self.shell.rune.return_value = DOCDB_VERSION
        self.shell.os.env.type = 'cENM'
        self.assertEqual(self.pgv.docdb_version, DOCDB_VERSION)

    @patch('pyu.log.log.error')
    @patch('pglib.env.version.PostgresSession')
    def test_version_raises_psql_exception(self, pg_ses, elog):
        pg_ses.return_value.__enter__.return_value.fetchone \
            .side_effect = PsqlAuthenticationFailure(EXCEPTION_MSG)

        with self.assertRaises(PsqlSessionException):
            self.pgv.version

        elog.assert_called_with(MSG, stdout=True)

    @patch('pyu.log.log.error')
    @patch('pglib.env.version.PostgresSession')
    def test_config_file_raises_psql_exception(self, pg_ses, elog):
        pg_ses.return_value.__enter__.return_value.fetchone \
            .side_effect = PsqlAuthenticationFailure(EXCEPTION_MSG)

        with self.assertRaises(PsqlSessionException):
            self.pgv.config_file

        elog.assert_called_with(MSG, stdout=True)

    @patch('pyu.log.log.error')
    @patch('pglib.env.version.PostgresSession')
    def test_data_directory_raises_psql_exception(self, pg_ses, elog):
        pg_ses.return_value.__enter__.return_value.fetchone \
            .side_effect = PsqlAuthenticationFailure(EXCEPTION_MSG)

        with self.assertRaises(PsqlSessionException):
            self.pgv.data_directory
        elog.assert_called_with(MSG, stdout=True)

    @patch('pyu.log.log.error')
    def test_docdb_version_raises_command_failed_exception(self, elog):
        self.shell.os.env.type = 'cENM'
        self.shell.rune.side_effect = CommandFailed(
            message='kubectl: command not found', output='Error',
            status_code='RL69', cmd='kubectl get pods')

        with self.assertRaises(CommandFailed):
            self.pgv.docdb_version
        elog.assert_called_with(COMMAND_FAILED_MSG, stdout=True)

    @patch('pyu.log.log.error')
    def test_docdb_version_raises_invalid_deployment_exception(self, elog):
        self.shell.os.env.type = 'pENM'

        with self.assertRaises(InvalidDeploymentType):
            self.pgv.docdb_version
        elog.assert_called_with(INVALID_DEPLOYMENT_MSG, stdout=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
