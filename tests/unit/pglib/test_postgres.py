import re

import psycopg2
import unittest2 as unittest

from mock import Mock, patch, call
from io import StringIO

from pyu.os.shell.errors import CommandFailed

from pglib.postgres import PsqlClient, PostgresClient, PostgresSession
from pglib.errors import PsqlSyntaxError, PsqlAuthenticationFailure, \
    PsqlColumnDoesNotExist, PsqlSessionException, \
    PostgresCredentialsException, PostgresHostError, PsqlClientNotAvailable

ASSERT_ERROR = 'AssertionError: Credentials shell must be set'
AUTH_ERROR = 'FATAL:  password authentication failed for user "Richie"'
BIN_ERROR = '-bash: /opt/postgresql/bin/psql: No such file or directory'
CMD_ERROR = '-bash: psql: command not found'
COL_NOT_EXIST = 'ERROR:  column "TEST" does not exist'
HOST_ERROR = 'could not translate host name "wrong_host"'
SYNTAX_ERROR = 'ERROR:  syntax error Test'

DDL_FILE = u"""
INSERT INTO db_version(id, version, comments, updated_date, status)
VALUES (1, '1.0',
        'Create pg_fsmon initial database objects and populate default values',
        CURRENT_DATE, 'current');
"""


class TestPsqlClientCenm(unittest.TestCase):

    @patch('pyu.security.cryptor.OpenSsl128CbcCryptorBash.decrypt',
           return_value='Test_Password')
    @patch('pyu.enm.globalproperties.GlobalProperties.get',
           return_value='Some_Encrypted_Yoke')
    @patch('pglib.postgres.LocalShellClient')
    def test_psql_client_called_with_args_headers(self, lshell, _gp, _pass):
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupCenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell)
        psql.run('SELECT 1;')
        shell.rune.assert_called_with('/usr/bin/psql -U postgres -h postgres '
                                      '-d postgres -qA -c "SELECT 1;"',
                                      env={'PGPASSWORD': 'Test_Password'},
                                      mask=re.compile('PGPASSWORD=([^\\s]+)'))

    @patch('pglib.postgres.LocalShellClient')
    def test_psql_client_ran_remotely_host(self, _shell):
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupCenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell)
        psql.run('SELECT 1;')
        shell.rune.assert_called_with('/usr/bin/psql -U postgres -h postgres '
                                      '-d postgres -qA -c "SELECT 1;"',
                                      env={'PGPASSWORD': 'Test_Password'},
                                      mask=re.compile('PGPASSWORD=([^\\s]+)'))

    @patch('pglib.postgres.LocalShellClient')
    def test_psql_client_ran_locally(self, _shell):
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupCenm(shell)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        credentials.setup(shell.os.sg.pg.credentials_class)
        psql = PsqlClient(shell)
        psql.run('SELECT 1;', remotely=False)
        shell.rune.assert_called_with('/usr/bin/psql -U postgres -d postgres '
                                      '-qA -c "SELECT 1;"',
                                      env={'PGPASSWORD': 'Test_Password'},
                                      mask=re.compile('PGPASSWORD=([^\\s]+)'))

    @patch('pglib.postgres.LocalShellClient')
    def test_psql_client_called_with_args_no_headers(self, _shell):
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupCenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell)
        psql.runq('SELECT 1;')
        shell.rune.assert_called_with('/usr/bin/psql -U postgres -h postgres '
                                      '-d postgres -qAt -c "SELECT 1;"',
                                      env={'PGPASSWORD': 'Test_Password'},
                                      mask=re.compile('PGPASSWORD=([^\\s]+)'))

    @patch('pglib.postgres.LocalShellClient')
    def test_no_psql_command_not_found(self, _shell):
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupCenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell)
        with self.assertRaises(PsqlClientNotAvailable):
            shell.rune.side_effect = CommandFailed(message=CMD_ERROR,
                                                   output='psql cmd test',
                                                   status_code='Richie',
                                                   cmd='psql -c')
            psql.run('SELECT 1;')

    @patch('pglib.postgres.LocalShellClient')
    def test_no_psql_client_in_expected_location(self, _shell):
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupCenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell)
        with self.assertRaises(PsqlClientNotAvailable):
            shell.rune.side_effect = CommandFailed(message=BIN_ERROR,
                                                   output='psql bin test',
                                                   status_code='Noah',
                                                   cmd='psql')
            psql.runq('SELECT 1;')

    @patch('pyu.security.cryptor.OpenSsl128CbcCryptorBash.decrypt',
           return_value='WRONG_PASSWORD')
    @patch('pyu.enm.globalproperties.GlobalProperties.get')
    @patch('pglib.postgres.LocalShellClient')
    def test_psql_client_authentication_exception(self, _shell, _gp, _pass):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell)
        with self.assertRaises(PsqlAuthenticationFailure):
            shell.rune.side_effect = CommandFailed(message=AUTH_ERROR,
                                                   output='Auth Test',
                                                   status_code='28P01',
                                                   cmd='Chantalle')
            psql.runq('SELECT 1;')

    @patch('pglib.postgres.LocalShellClient')
    def test_psql_client_invalid_column_exception(self, _shell):
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupCenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell)
        with self.assertRaises(PsqlColumnDoesNotExist):
            shell.rune.side_effect = CommandFailed(message=COL_NOT_EXIST,
                                                   output='Bad SQL',
                                                   status_code='42703',
                                                   cmd='BoBo')
            psql.run('SELECT 1;')

    @patch('pglib.postgres.LocalShellClient')
    def test_psql_client_syntax_error_exception(self, _shell):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell)
        with self.assertRaises(PsqlSyntaxError):
            shell.rune.side_effect = CommandFailed(message=SYNTAX_ERROR,
                                                   output='Bad Syntax',
                                                   status_code='42601',
                                                   cmd='Noah')
            psql.runq('SELECT 1;')

    @patch('pglib.postgres.LocalShellClient')
    def test_psql_client_raise_assert_error_creds(self, _shell):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell)
        with self.assertRaises(PostgresCredentialsException):
            shell.rune.side_effect = CommandFailed(message=ASSERT_ERROR,
                                                   output='Creds not set',
                                                   status_code='42601',
                                                   cmd='Noah')
            psql.runq('SELECT 1;')

    @patch('pglib.postgres.LocalShellClient')
    def test_psql_client_host_error_exception(self, _shell):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Howya Sham'
        psql = PsqlClient(shell)
        with self.assertRaises(PostgresHostError):
            shell.rune.side_effect = CommandFailed(message=HOST_ERROR,
                                                   output='bad host',
                                                   status_code='42601',
                                                   cmd='BoBo')
            psql.runq('SELECT 1;')

    @patch('pglib.postgres.LocalShellClient')
    def test_psql_client_raise_exception(self, _shell):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell)
        with self.assertRaises(Exception):
            shell.rune.side_effect = KeyError()
            psql.runq('SELECT 1;')

    @patch('pyu.log.log.info')
    @patch('pglib.postgres.LocalShellClient')
    def test_psql_vacuumdb_success(self, _shell, ilog):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell, database='Chantalle')
        shell.run.return_value = (0, 'Richie')
        psql.vacuumdb()
        ilog.assert_called_with('Successfully vacuumed Chantalle')

    @patch('pyu.log.log.error')
    @patch('pglib.postgres.LocalShellClient')
    def test_psql_vacuumdb_fails(self, _shell, elog):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell, database='Chantalle')
        shell.run.return_value = (1, 'Richie')
        psql.vacuumdb()
        elog.assert_called_with('Failed to vacuum Chantalle')

    @patch('pyu.log.log.info')
    @patch('pglib.postgres.LocalShellClient')
    def test_psql_reindexdb_success(self, _shell, ilog):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell, database='Chantalle')
        shell.run.return_value = (0, 'Richie')
        psql.reindexdb()
        ilog.assert_called_with('Successfully reindex Chantalle')

    @patch('pyu.log.log.error')
    @patch('pglib.postgres.LocalShellClient')
    def test_psql_reindexdb_fails(self, _shell, elog):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        shell.os.sg.pg.credentials_class.password = 'Test_Password'
        psql = PsqlClient(shell, database='Chantalle')
        shell.run.return_value = (1, 'Richie')
        psql.reindexdb()
        elog.assert_called_with('Failed to reindex Chantalle')


class TestPostgresSession(unittest.TestCase):

    @patch('psycopg2.connect')
    def test_default_postgres_client_returned(self, connect):
        from pglib.env.credentials import PostgresEnmCredentialsGroup
        from pglib.env.penm.consts import PgConstantsPenm
        from pglib.env.penm.credentials import \
            PostgresUserEncryptedPasswordPenm
        shell = Mock()
        const = PgConstantsPenm(shell)
        shell.os.sg.pg.consts = const
        cred = (PostgresEnmCredentialsGroup.postgres,
                PostgresUserEncryptedPasswordPenm.password)
        # PostgresClient - psycopg2
        with PostgresSession(credential=cred, host=const.pg_host) as pg_client:
            self.assertEqual(type(pg_client), PostgresClient)
            self.assertEqual(pg_client.database, 'postgres')
            self.assertNotEqual(pg_client._connection, None)

    @patch('psycopg2.connect')
    def test_invalid_pg_credentials(self, connect):
        err = psycopg2.OperationalError()
        connect.side_effect = err
        with self.assertRaises(Exception):
            with PostgresSession(credential=('wrong', 'creds'), host='test') \
                    as pg_client:
                pg_client.run('Mocking query', ('arg1', 'arg2'))
                pg_client._connection.assert_not_called()

    @patch('psycopg2.connect')
    def test_connection_commits_and_closes_on_exit(self, connect):
        from pglib.env.credentials import PostgresEnmCredentialsGroup
        from pglib.env.penm.consts import PgConstantsPenm
        from pglib.env.penm.credentials import \
            PostgresUserEncryptedPasswordPenm
        shell = Mock()
        const = PgConstantsPenm(shell)
        cred = (PostgresEnmCredentialsGroup.postgres,
                PostgresUserEncryptedPasswordPenm.password)
        with PostgresSession(credential=cred, host=const.pg_host) as pg_client:
            pg_client.run('Mocking query', ('arg1', 'arg2'))

        expected_calls = [
            call.cursor(),
            call.cursor().execute('Mocking query', ('arg1', 'arg2')),
            call.cursor().close(),
            call.commit(),
            call.close()
        ]
        pg_client._connection.assert_has_calls(expected_calls)

    @patch('psycopg2.connect')
    def test_connection_error_for_host_name(self, connect):
        err = psycopg2.Error(HOST_ERROR)
        connect.side_effect = err
        with self.assertRaises(Exception):
            with PostgresSession(host='Chantalle',
                                 credential=('Bo', 'Noah')) as pg_client:
                pg_client.run('Mocking query', ('arg1', 'arg2'))
                pg_client._connection.assert_not_called()

    @patch('psycopg2.connect')
    def test_connection_error_for_other_operational_err(self, connect):
        err = psycopg2.OperationalError('Memory Issue')
        connect.side_effect = err
        with self.assertRaises(psycopg2.OperationalError):
            with PostgresSession(host='Chantalle',
                                 credential=('Bo', 'Noah')) as pg_client:
                pg_client.run('Mocking query', ('arg1', 'arg2'))
                pg_client._connection.assert_not_called()

    @patch('psycopg2.connect')
    def test_connection_error_on_unexpected_pscopg_exc(self, connect):
        err = psycopg2.Error('Some Other PSYCOPG Exception')
        connect.side_effect = err
        with self.assertRaises(Exception):
            with PostgresSession(host='Chantalle',
                                 credential=('Bo', 'Noah')) as pg_client:
                pg_client.run('Mocking query', ('arg1', 'arg2'))
                pg_client._connection.assert_not_called()

    @patch('psycopg2.connect')
    def test_connection_error_on_unexpected_exc(self, connect):
        err = Exception('Some Other Exception')
        connect.side_effect = err
        with self.assertRaises(Exception):
            with PostgresSession(host='Chantalle',
                                 credential=('Bo', 'Noah')) as pg_client:
                pg_client.run('Mocking query', ('arg1', 'arg2'))
                pg_client._connection.assert_not_called()

    @patch('psycopg2.connect')
    def test_connection_rollback_on_psycopg_exc(self, connect):
        err = psycopg2.Error('Column does not exist')
        connect.return_value.cursor.return_value.execute.side_effect = err
        with self.assertRaises(PsqlSessionException):
            with PostgresSession(host='Chantalle',
                                 credential=('Bo', 'Noah')) as pg_client:
                pg_client.run('Mocking query', ('arg1', 'arg2'))
        expected_calls = [
            call.cursor(),
            call.cursor().execute('Mocking query', ('arg1', 'arg2')),
            call.rollback(),
            call.cursor().close(),
            call.rollback(),
            call.close()
        ]
        pg_client._connection.assert_has_calls(expected_calls)

    @patch('psycopg2.connect')
    def test_connection_rollback_on_unexpected_exc(self, connect):
        err = Exception('Unexpected error')
        connect.return_value.cursor.return_value.execute.side_effect = err
        with self.assertRaises(Exception):
            with PostgresSession(host='Chantalle',
                                 credential=('Bo', 'Noah')) as pg_client:
                pg_client.fetchall('Mocking query', ('arg1', 'arg2'))
        expected_calls = [
            call.cursor(),
            call.cursor().execute('Mocking query', ('arg1', 'arg2')),
            call.cursor().close(),
            call.rollback(),
            call.close()
        ]
        pg_client._connection.assert_has_calls(expected_calls)

    @patch('psycopg2.connect')
    def test_run_fetchone(self, connect):
        with PostgresSession(host='Chantalle', credential=('Bo', 'Noah')) as \
                pg_client:
            pg_client.fetchone('Add query', ('arg1', 'arg2'))
        expected_calls = [
            call.cursor(),
            call.cursor().execute("Add query", ("arg1", "arg2")),
            call.cursor().fetchone(),
            call.cursor().close(),
            call.commit(),
            call.close()
        ]
        pg_client._connection.assert_has_calls(expected_calls)

    @patch('psycopg2.connect')
    def test_run_fetchall(self, connect):
        with PostgresSession(host='Chantalle', credential=('Bo', 'Noah')) as \
                pg_client:
            pg_client.fetchall('Add query', ('arg1', 'arg2'))
        expected_calls = [
            call.cursor(),
            call.cursor().execute('Add query', ('arg1', 'arg2')),
            call.cursor().fetchall(),
            call.cursor().close(),
            call.commit(),
            call.close()
        ]
        pg_client._connection.assert_has_calls(expected_calls)

    @patch('builtins.open')
    @patch('psycopg2.connect')
    def test_ddl_file_executed_successfully(self, connect, _open):
        _open.return_value = StringIO(DDL_FILE)
        with PostgresSession(host='Chantalle', credential=('Bo', 'Noah')) as \
                pg_client:
            pg_client.load_ddl_file(DDL_FILE)

        expected_calls = [
            call.cursor(),
            call.cursor().execute(DDL_FILE),
            call.cursor().close(),
            call.commit(),
            call.close()
        ]
        pg_client._connection.assert_has_calls(expected_calls)

    @patch('builtins.open')
    @patch('psycopg2.connect')
    def test_ddl_file_loading_failed_with_ioerror(self, connect, _open):
        afile = Mock()
        afile.read.side_effect = IOError('error reading file')
        _open.return_value.__enter__.return_value = afile
        with self.assertRaises(PsqlSessionException):
            with PostgresSession(host='Chantalle',
                                 credential=('Bo', 'Noah')) as pg_client:
                pg_client.load_ddl_file(DDL_FILE)

    @patch('pyu.log.log.debug')
    @patch('psycopg2.connect')
    def test_reset_connections(self, connect, dlog):
        db = 'admindb'
        query = """
                ALTER DATABASE %s CONNECTION LIMIT -1;
                """ % db
        with PostgresSession(host='Chantalle', database=db,
                             credential=('Bo', 'Noah')) as pg_client:
            pg_client.reset_connections()

        expected_calls = [
            call.cursor(),
            call.cursor().execute(query),
            call.cursor().close(),
            call.commit(),
            call.close()
        ]
        pg_client._connection.assert_has_calls(expected_calls)
        dlog.assert_called_with('Resetting connection on admindb.')

    @patch('psycopg2.connect')
    def test_reset_connections_psycopg_exc(self, connect):
        db = 'admindb'
        query = """
                ALTER DATABASE %s CONNECTION LIMIT -1;
                """ % db
        err = psycopg2.Error('UNDEFINED_OBJECT')
        connect.return_value.cursor.return_value.execute.side_effect = err
        with self.assertRaises(PsqlSessionException):
            with PostgresSession(host='Chantalle', database=db,
                                 credential=('Bo', 'Noah')) as pg_client:
                pg_client.reset_connections()
        expected_calls = [
            call.cursor(),
            call.cursor().execute(query),
            call.rollback(),
            call.cursor().close(),
            call.rollback(),
            call.close()
        ]
        pg_client._connection.assert_has_calls(expected_calls)

    @patch('pyu.log.log.debug')
    @patch('psycopg2.connect')
    def test_limit_connections(self, connect, dlog):
        db = 'admindb'
        query = """
                ALTER DATABASE %s CONNECTION LIMIT 0;
                """ % db
        with PostgresSession(host='Chantalle', database=db,
                             credential=('Bo', 'Noah')) as pg_client:
            pg_client.limit_connections()

        expected_calls = [
            call.cursor(),
            call.cursor().execute(query),
            call.cursor().close(),
            call.commit(),
            call.close()
        ]
        pg_client._connection.assert_has_calls(expected_calls)
        dlog.assert_called_with('Limiting connection on %s.' % db)

    @patch('pyu.log.log.debug')
    @patch('psycopg2.connect')
    def test_kill_ongoing_transactions(self, connect, dlog):
        db = 'admindb'
        query = """
                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM 
                    pg_stat_activity WHERE datname='%s' AND 
                pid <> pg_backend_pid();
                """ % db
        with PostgresSession(host='Chantalle', database=db,
                             credential=('Bo', 'Noah')) as pg_client:
            pg_client.kill_ongoing_transactions()

        expected_calls = [
            call.cursor(),
            call.cursor().execute(query),
            call.cursor().close(),
            call.commit(),
            call.close()
        ]
        pg_client._connection.assert_has_calls(expected_calls)
        dlog.assert_called_with('Killing ongoing transactions on %s.' % db)

    @patch('psycopg2.connect')
    def test_kill_ongoing_transactions_psycopg_exc(self, connect):
        db = 'admindb'
        query = """
                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM 
                    pg_stat_activity WHERE datname='%s' AND 
                pid <> pg_backend_pid();
                """ % db
        err = psycopg2.Error('UNDEFINED_OBJECT')
        connect.return_value.cursor.return_value.execute.side_effect = err
        with self.assertRaises(PsqlSessionException):
            with PostgresSession(host='Chantalle', database=db,
                                 credential=('Bo', 'Noah')) as pg_client:
                pg_client.kill_ongoing_transactions()
        expected_calls = [
            call.cursor(),
            call.cursor().execute(query),
            call.rollback(),
            call.cursor().close(),
            call.rollback(),
            call.close()
        ]
        pg_client._connection.assert_has_calls(expected_calls)

    @patch('pglib.postgres.PostgresClient.fetchall')
    @patch('psycopg2.connect')
    def test_get_dbs(self, connect, fetcher):
        fetcher.return_value = (['db-1', 'db-richie'],)
        with PostgresSession(host='Chantalle', credential=('Bo', 'Noah')) as \
                pg_client:
            output = pg_client.get_dbs(ignore_dbs=None)
            self.assertEqual(output, ['db-1', 'db-richie'])

    @patch('pglib.postgres.PostgresClient.fetchall')
    @patch('psycopg2.connect')
    def test_get_dbs_ignore_dbs(self, connect, fetcher):
        ignore_dbs = ['postgres', 'another']
        fetcher.return_value = [['db-1', 'postgres', 'db-richie'], ]
        with PostgresSession(host='Chantalle', credential=('Bo', 'Noah')) as \
                pg_client:
            output = pg_client.get_dbs(ignore_dbs=ignore_dbs)
            self.assertEqual(output, ['db-1', 'db-richie'])

    @patch('pyu.log.log.debug')
    @patch('pglib.postgres.PostgresClient.fetchall')
    @patch('psycopg2.connect')
    def test_rollback_prepared_transaction(self, connect, fetcher, dlog):
        fetcher.return_value = ('1234', 'db-noah', 'bo')
        gid, _, _ = fetcher.return_value
        with PostgresSession(host='Chantalle', credential=('Bo', 'Noah')) as \
                pg_client:
            pg_client.rollback_prepared_transaction(gid)
            dlog.assert_called_with('Rolling back prepared transaction: '
                                    '1234')
            expected_calls = [
                call.set_isolation_level(0),
                call.cursor(),
                call.cursor().execute("ROLLBACK PREPARED '1234'"),
                call.cursor().close()
            ]
            pg_client._connection.assert_has_calls(expected_calls)

    @patch('pglib.postgres.PostgresClient.fetchall')
    @patch('psycopg2.connect')
    def test_get_one_prepared_transactions(self, connect, fetcher):
        fetcher.return_value = [['foo', 'postgres', 'db_name', '1674580827.224359']]
        with PostgresSession(host='Chantalle', credential=('Bo', 'Noah')) as \
                pg_client:
            output = pg_client.get_prepared_transactions()
            self.assertEqual(output, [{'gid': 'foo', 'owner': 'postgres', 'database': 'db_name', 'prepared': '1674580827.224359'}])

    @patch('pglib.postgres.PostgresClient.fetchall')
    @patch('psycopg2.connect')
    def test_get_no_prepared_transactions(self, connect, fetcher):
        fetcher.return_value = []
        with PostgresSession(host='Chantalle', credential=('Bo', 'Noah')) as \
                pg_client:
            output = pg_client.get_prepared_transactions()
            self.assertEqual(output, [])



if __name__ == '__main__':
    unittest.main(verbosity=2)
