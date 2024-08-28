import unittest2 as unittest
from mock import patch, Mock

from pglib.errors import NonReplicatingCluster

OVERVIEW = u"""
+----------+------------+-----------------+--------------+---------+----+-----------+
| Cluster  |   Member   |       Host      |     Role     |  State  | TL | Lag in MB |
+----------+------------+-----------------+--------------+---------+----+-----------+
| postgres | postgres-0 |  192.168.17.126 |    Leader    | running |  2 |           |
| postgres | postgres-1 | 192.168.138.196 | Sync Standby | running |  2 |         0 |
+----------+------------+-----------------+--------------+---------+----+-----------+
"""

LEADER_ONLY = u"""
+----------+------------+-----------------+--------------+---------+----+-----------+
| Cluster  |   Member   |       Host      |     Role     |  State  | TL | Lag in MB |
+----------+------------+-----------------+--------------+---------+----+-----------+
| postgres | postgres-0 |  192.168.17.126 |    Leader    | running |  2 |           |
+----------+------------+-----------------+--------------+---------+----+-----------+
"""

NO_SYNC_STANDBY = u"""
+------------+-----------------+---------+---------+----+-----------+--------------+
| Member     | Host            | Role    | State   | TL | Lag in MB | Tags         |
+------------+-----------------+---------+---------+----+-----------+--------------+
| postgres-0 | 192.168.253.216 | Replica | running | 9  | 37027     | nosync: true |
| postgres-1 | 192.168.98.217  | Leader  | running | 9  |           |              |
+------------+-----------------+---------+---------+----+-----------+--------------+"""

RESULT = 'pod|backend_start|state|sent_lsn|replay_lsn|write_lag|replay_lag' \
         '|sync_state\npostgres-1|2021-05-20 10:19:27|streaming|0/55F05938|' \
         '0/55F05938|00:00:00.000178|00:00:00.000615|sync\n(1 row)\n'

EXPECTED = [['pod', 'backend_start', 'state', 'sent_lsn', 'replay_lsn',
             'write_lag', 'replay_lag', 'sync_state'],
            ['postgres-1', '2021-05-20 10:19:27', 'streaming',
             '0/55F05938', '0/55F05938', '00:00:00.000178',
             '00:00:00.000615', 'sync']]

MSG = 'Failed to retrieve Replication Lag information.\nPlease try again ' \
      'later.\nIf issue persists please contact customer support.'

REP_MSG = 'Replication maybe broken due to Housekeeping.You may need to ' \
          're-initialise the follower node. Refer to the documentation.'


class TestReplicationLag(unittest.TestCase):

    def setUp(self):
        from pglib.admin.controllers.replication_lag import \
            ReplicationLagController
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        self.shell = Mock()
        self.shell.os.sg.pg.credentials_class = \
            PgServiceGroupCenm.credentials_class
        credentials.setup(self.shell.os.sg.pg.credentials_class)
        self.rlc = ReplicationLagController(self.shell)

    @patch('pglib.postgres.PsqlClient.run')
    @patch('pglib.admin.controllers.replication_lag.Role')
    @patch('pglib.admin.controllers.replication_lag.EnmKubeSession')
    def test_tabulated_replication_lag_returned(self, eks, role, pg_run):
        eks.return_value.__enter__.return_value.rune.return_value = OVERVIEW
        pg_run.return_value = RESULT
        self.assertEqual(self.rlc.execute(), EXPECTED)

    @patch('pglib.admin.controllers.replication_lag.Role')
    @patch('pglib.admin.controllers.replication_lag.EnmKubeSession')
    def test_no_sync_standby_overview_throws_NonReplicatingCluster(self, eks,
                                                                   role):
        eks.return_value.__enter__.return_value.rune.return_value = \
            NO_SYNC_STANDBY
        with self.assertRaises(NonReplicatingCluster):
            self.rlc.execute()

    @patch('pglib.admin.controllers.replication_lag.Role')
    @patch('pglib.admin.controllers.replication_lag.EnmKubeSession')
    def test_non_replicating_exception_if_no_replica(self, eks, role):
        eks.return_value.__enter__.return_value.rune.return_value = LEADER_ONLY
        with self.assertRaises(NonReplicatingCluster):
            self.rlc.execute()

    @patch('pglib.postgres.PsqlClient.run')
    @patch('pglib.admin.controllers.replication_lag.Role')
    @patch('pglib.admin.controllers.replication_lag.EnmKubeSession')
    def test_lag_overview_with_invalid_pg_credentials(self, eks, role, pg_run):
        from pglib.errors import PostgresCredentialsException
        eks.return_value.__enter__.return_value.rune.return_value = OVERVIEW
        pg_run.side_effect = PostgresCredentialsException('wrong creds')
        with self.assertRaises(PostgresCredentialsException):
            self.rlc.execute()

    def test_lag_overview_class_attributes(self):
        self.assertEqual(self.rlc.name, 'lag')
        self.assertEqual(self.rlc.title, 'Replication Lag')
        self.assertEqual(self.rlc.rows_border, False)


if __name__ == '__main__':
    unittest.main()
