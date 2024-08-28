import re

import unittest2 as unittest
from mock import Mock, patch

LEADER = {'Cluster': 'postgres', 'Member': 'postgres-1',
          'Host': '192.168.17.9', 'Role': 'Leader',
          'State': 'running', 'TL': '3', 'Lag in MB': ''}

MOCK_MNT_DATA = """
Filesystem                                                                                                       Type 1K-blocks     Used Available Use% Mounted on
10.221.21.185:/ahs050124/efs2124/fargo-pg-data-postgres-1-pvc-5b8bf5bd-fe0a-4968-8aa8-247433d3e513/postgresql-db nfs  131294272 22454464 108839808  18% /var/lib/postgresql/data
"""

PASSKEY = u"""fake_pass_key"""


class TestInstance(unittest.TestCase):

    def test_representation_of_an_instance(self):
        from pglib.ha.instance import PostgresInstance
        shell = Mock()
        pg_instance = PostgresInstance(shell, LEADER)
        self.assertEqual('Pod: postgres-1 | Role: Leader | Host: 192.168.17.9 '
                         '| State: running', str(pg_instance))

    @patch('pglib.postgres.PsqlClient')
    @patch('pyu.enm.kube.EnmKubeSession')
    def test_same_shell_is_returned_if_on_postgres_pod(self, eks, psql):
        from pglib.ha.instance import PostgresInstance
        from pyu.tools.dummy import DummyContextManager
        shell = Mock()
        shell.host.short_hostname = 'postgres-1'
        pg_instance = PostgresInstance(shell, LEADER)
        self.assertIsInstance(pg_instance.session, DummyContextManager)

    @patch('pglib.postgres.PsqlClient')
    def test_pg_data_dir_property_returns_data(self, _psql):
        from pglib.env.cenm.consts import PgConstantsCenm
        from pglib.ha.instance import PostgresInstance
        shell = Mock()
        shell.os.fs.get.return_value = '/var/lib/postgresql/data/pgdata'
        const = PgConstantsCenm(shell)
        shell.os.sg.pg.consts = const
        pg_instance = PostgresInstance(shell, LEADER)
        pg_instance.remote_shell = shell
        self.assertEqual(const.pg_data_dir, str(pg_instance.pg_data_dir))

    @patch('pyu.log.log.error')
    @patch('pglib.postgres.PsqlClient')
    def test_pg_data_dir_property_logs_when_no_data(self, psql, elog):
        from pglib.ha.instance import PostgresInstance
        shell = Mock()
        shell.os.fs.get.return_value = ''
        pg_instance = PostgresInstance(shell, LEADER)
        pg_instance.remote_shell = shell
        self.assertEqual(None, pg_instance.pg_data_dir)
        elog.assert_called_with('PG data directory is not available on %s' %
                                pg_instance.pod, stdout=True)

    @patch('pglib.postgres.PsqlClient')
    def test_pg_wal_dir_property_returns_data(self, psql):
        from pglib.env.cenm.consts import PgConstantsCenm
        from pglib.ha.instance import PostgresInstance
        shell = Mock()
        shell.os.fs.get.return_value = '/var/lib/postgresql/data/pgdata/pg_wal'
        const = PgConstantsCenm(shell)
        shell.os.sg.pg.consts = const
        pg_instance = PostgresInstance(shell, LEADER)
        pg_instance.remote_shell = shell
        self.assertEqual(const.pg_wal_dir, str(pg_instance.pg_wal_dir))

    @patch('pyu.log.log.error')
    @patch('pglib.postgres.PsqlClient')
    def test_pg_wal_dir_property_logs_when_no_data(self, psql, elog):
        from pglib.ha.instance import PostgresInstance
        shell = Mock()
        shell.os.fs.get.return_value = ''
        pg_instance = PostgresInstance(shell, LEADER)
        pg_instance.remote_shell = shell
        self.assertEqual(None, pg_instance.pg_wal_dir)
        elog.assert_called_with('PG WAL directory is not available on %s' %
                                pg_instance.pod, stdout=True)

    @patch('pglib.postgres.PsqlClient')
    def test_pg_mount_property_returns_a_file_sys_usage_obj(self, psql):
        from pglib.ha.instance import PostgresInstance
        shell = Mock()
        shell.rune.return_value = MOCK_MNT_DATA
        pg_instance = PostgresInstance(shell, LEADER)
        pg_instance.remote_shell = shell
        self.assertEqual('125.2G', str(pg_instance.pg_mount.size))

    @patch('pyu.log.log.error')
    @patch('pglib.ha.instance.FileSystemUsage')
    @patch('pglib.postgres.PsqlClient')
    def test_pg_mount_property_returns_a_log_no_mount_info(self, psql, _fs,
                                                           elog):
        from pglib.ha.instance import PostgresInstance
        shell = Mock()
        _fs.return_value = ''
        pg_instance = PostgresInstance(shell, LEADER)
        pg_instance.remote_shell = shell
        self.assertEqual(None, pg_instance.pg_mount)
        elog.assert_called_with('Could not retrieve file system usage for '
                                'pg_mount on %s' % pg_instance.pod,
                                stdout=True)

    @patch('pglib.postgres.PsqlClient')
    def test_repr_instance(self, psql):
        from pglib.ha.instance import PostgresInstance
        shell = Mock()
        pg_instance = PostgresInstance(shell, LEADER)
        self.assertEqual(str(pg_instance), 'Pod: postgres-1 | Role: Leader '
                                           '| Host: 192.168.17.9 | State: '
                                           'running')


if __name__ == '__main__':
    unittest.main(verbosity=2)
