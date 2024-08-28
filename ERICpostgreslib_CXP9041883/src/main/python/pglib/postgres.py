import re

from pglib.env.credentials import credentials
from pglib.errors import PsqlSessionException, PsqlClientNotAvailable, \
    PsqlTableDoesNotExist, PsqlColumnDoesNotExist, PsqlObjectIsUndefined, \
    PsqlAuthenticationFailure, PsqlSyntaxError, PostgresCredentialsException, \
    PostgresHostError
from pglib.utils.iterable import flatten_list_tuples

try:
    import psycopg2
    from psycopg2 import errorcodes, extensions
except ImportError:
    pass

from pyu.log import log
from pyu.os.shell.errors import CommandFailed
from pyu.os.shell.local import LocalShellClient

EXCEPTION_MAP = {
    errorcodes.UNDEFINED_TABLE: PsqlTableDoesNotExist,
    errorcodes.UNDEFINED_COLUMN: PsqlColumnDoesNotExist,
    errorcodes.UNDEFINED_OBJECT: PsqlObjectIsUndefined,
    errorcodes.SYNTAX_ERROR: PsqlSyntaxError,
    errorcodes.INVALID_PASSWORD: PsqlAuthenticationFailure,
}

pg_auth_fail_regex = re.compile(
    r'FATAL\s*:\s+password\s+authentication\s+failed')
pg_col_not_exist_regex = re.compile(
    r'ERROR\s*:\s+column\s+"[^\s]+"\s+does\s+not\s+exist')
pg_syntax_err_regex = re.compile(r'ERROR\s*:\s+syntax\s+error\s+')
pg_host_error_regex = re.compile(
    r'could\s+not\s+translate\s+host\s+name\s+"[^\s]+"')
credentials_not_set_regex = re.compile(
    r'AssertionError\s*:\s+Credentials\s+shell\s+must\s+be\s+set')
psql_command_missing_regex = re.compile(r'psql\s*:\s+command\s+not\s+found')
psql_binary_missing_regex = re.compile(r'psql\s*:\s+No\s+such\s+file')


class PsqlClient(object):

    def __init__(self, shell, credential=credentials.postgres, host=None,
                 database='postgres'):
        self.shell = shell
        self.consts = self.shell.os.sg.pg.consts
        self.credential = credential(LocalShellClient())
        self.host = host or self.consts.pg_host
        self.database = database
        self.psql = self.consts.psql
        self.security_mask = re.compile(r"PGPASSWORD=([^\s]+)")
        self.user, self.password = self.credential

    def run(self, sql, host=None, remotely=True, headers=True):
        host = host or self.host
        host_string = ' -h %s' % host if remotely else ''
        header = '' if headers else 't'
        # pylint: disable=W0706
        try:
            output = self.shell.rune('%s -U %s%s -d %s -qA%s -c "%s"'
                                     % (self.psql, self.user, host_string,
                                        self.database, header, sql),
                                     env={"PGPASSWORD": self.password},
                                     mask=self.security_mask)
        except CommandFailed as err:
            output = err.msg
            if psql_command_missing_regex.search(str(output)):
                raise PsqlClientNotAvailable('Postgres command not found.')
            if psql_binary_missing_regex.search(str(output)):
                raise PsqlClientNotAvailable('Postgres Binaries not available '
                                             'in expected location.')
            if pg_auth_fail_regex.search(str(output)):
                log.error('Postgres Authentication Failure for user: %s.'
                          % self.user)
                raise PsqlAuthenticationFailure('Postgres Authentication '
                                                'Failure for user: %s.' %
                                                self.user)
            if pg_col_not_exist_regex.search(str(output)):
                log.error('Invalid SQL query: %s.' % sql)
                exc = EXCEPTION_MAP.get(errorcodes.UNDEFINED_COLUMN,
                                        PsqlSessionException)
                raise exc('Invalid SQL query: %s.' % sql)
            if pg_syntax_err_regex.search(str(output)):
                log.error('SQL syntax error: %s.' % sql)
                exc = EXCEPTION_MAP.get(errorcodes.SYNTAX_ERROR,
                                        PsqlSessionException)
                raise exc('SQL syntax error: %s.' % sql)
            if credentials_not_set_regex.search(str(output)):
                raise PostgresCredentialsException('Shell credentials not '
                                                   'set.')
            if pg_host_error_regex.search((str(output))):
                raise PostgresHostError('Invalid host provided to PSQL '
                                        'client.\nPossible hosts can be: %s, '
                                        '%s, etc' % (self.host, 'localhost'))
        except Exception:
            raise
        return output

    def runq(self, sql, host=None, remotely=True):
        return self.run(sql, headers=False, host=host, remotely=remotely)

    def vacuumdb(self, full=True, analyze=True):
        vac_opts = '%s%s' % ('-f' if full else '', ' -z' if analyze else '')
        status, _ = self.shell.run('%s/vacuumdb -U %s -h %s -d %s %s' %
                                   (self.consts.pg_bin, self.user,
                                    self.host, self.database, vac_opts),
                                   env={"PGPASSWORD": self.password},
                                   mask=self.security_mask)
        if status == 0:
            log.info('Successfully vacuumed %s' % self.database)
        else:
            log.error('Failed to vacuum %s' % self.database)
        return status

    def reindexdb(self):
        status, _ = self.shell.run('%s/reindexdb -U %s -h %s -d %s' %
                                   (self.consts.pg_bin, self.user,
                                    self.host, self.database),
                                   env={"PGPASSWORD": self.password},
                                   mask=self.security_mask)
        if status == 0:
            log.info('Successfully reindex %s' % self.database)
        else:
            log.error('Failed to reindex %s' % self.database)
        return status


class PostgresClient(object):

    def __init__(self, database, connection):
        self.database = database
        self._connection = connection

    def _run(self, query, *args):
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, *args)
        except psycopg2.Error as err:
            self._connection.rollback()
            cursor.close()

            log.debug("pg_error_code: %s" % err.pgcode)
            exc = EXCEPTION_MAP.get(err.pgcode, PsqlSessionException)
            raise exc("Failed to execute query on '%s' database. "
                      "Query: '%s', PgCode: %s, Error: %s"
                      % (self.database, query, err.pgcode, err))
        except Exception:
            cursor.close()
            raise

        return cursor

    def run(self, query, *args):
        """
        Execute a query without expecting result back
        :param query: query to execute
        :param args: query arguments
        """
        cursor = self._run(query, *args)
        cursor.close()

    def fetchone(self, query, *args):
        """
        Execute a query and fetch one row from the result set.
        Top record from result set will be returned as a tuple
        :param query: query to execute
        :param args: query arguments
        :return: tuple ()
        """
        cursor = self._run(query, *args)
        row = cursor.fetchone()
        cursor.close()
        return row

    def fetchall(self, query, *args):
        """
        Execute a query and fetch all rows from the result set.
        :param query: query to execute
        :param args: query arguments
        :return: list [(), ()]
        """
        cursor = self._run(query, *args)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def load_ddl_file(self, ddl_file, *args):
        with open(ddl_file, "r") as afile:
            try:
                f_content = afile.read()
            except IOError as io_err:
                raise PsqlSessionException("Failed to read ddl file. "
                                           "Details: %s" % io_err)
        self.run(f_content, *args)

    def reset_connections(self, db=None):
        database = db or self.database
        query = """
                ALTER DATABASE %s CONNECTION LIMIT -1;
                """ % database

        log.debug("Resetting connection on %s." % database)
        self.run(query)

    def limit_connections(self, db=None):
        database = db or self.database
        query = """
                ALTER DATABASE %s CONNECTION LIMIT 0;
                """ % database

        log.debug("Limiting connection on %s." % database)
        self.run(query)

    def kill_ongoing_transactions(self, db=None):
        database = db or self.database
        query = """
                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM 
                    pg_stat_activity WHERE datname='%s' AND 
                pid <> pg_backend_pid();
                """ % database

        log.debug("Killing ongoing transactions on %s." % database)
        self.run(query)

    def get_dbs(self, ignore_dbs=None):
        """
        Fetching names and ids of Postgres managed databases
        :return: list
        """
        query = """
                SELECT datname FROM pg_database ORDER BY datname;
                """
        result_set = self.fetchall(query)
        if ignore_dbs:
            return [db for db in flatten_list_tuples(result_set) if db not
                    in ignore_dbs]
        return flatten_list_tuples(result_set)

    def rollback_prepared_transaction(self, tx_identifier):
        self._connection.set_isolation_level(extensions.
                                             ISOLATION_LEVEL_AUTOCOMMIT)
        log.debug("Rolling back prepared transaction: %s" % tx_identifier)
        self.run("ROLLBACK PREPARED '%s'" % tx_identifier)

    def get_prepared_transactions(self):
        query = """
                SELECT gid, owner, database, extract(epoch from prepared)
                AS prepared FROM pg_catalog.pg_prepared_xacts;
                """

        result = self.fetchall(query)
        colnames = ["gid", "owner", "database", "prepared"]
        return [dict(zip(colnames, i)) for i in result]


class PostgresSession(object):
    """
    Context Manager to access ENM Postgres client connection
    """

    def __init__(self, database="postgres", host=None, credential=None,
                 port=5432):
        self.shell = LocalShellClient()
        credential = credential or credentials(self.shell).postgres
        self.user, self.password = credential
        self.database = database
        self.port = port
        self.host = host or self.shell.os.sg.pg.consts.pg_host
        self.connection = None

    def __enter__(self):
        self.connection = psycopg2.connect(user=self.user,
                                           password=self.password,
                                           database=self.database,
                                           host=self.host, port=self.port)

        return PostgresClient(self.database, self.connection)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type:
            log.debug("Unhandled exception caught in PostgresSession."
                      "Rolling back transaction."
                      "Details: %s : %s : %s" %
                      (exception_type, exception_value, exception_traceback))
            self.connection.rollback()  # e.g.type error, value error,+
            # IntegrityError (duplicate key), etc
        else:
            self.connection.commit()
        self.connection.close()
