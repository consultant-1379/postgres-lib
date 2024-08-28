import unittest2 as unittest
from mock import Mock, patch

from pglib.env.cenm.credentials import PostgresUserEncryptedPasswordCenm
from pglib.env.credentials import PostgresEnmCredentialsGroup
from pglib.ha.cluster import PostgresCluster

from pyu.os.shell.errors import CommandFailed

CLUSTER_LIST_3 = u"""
+ Cluster: postgres (7020762932214296660) ----+---------+----+-----------+
| Member     | Host            | Role         | State   | TL | Lag in MB |
+------------+-----------------+--------------+---------+----+-----------+
| postgres-0 | 192.168.59.81   | Leader       | running |  9 |           |
| postgres-1 | 192.168.156.181 | Sync Standby | running |  9 |         0 |
| postgres-2 | 192.168.156.182 |              | running |  9 |         0 |
+------------+-----------------+--------------+---------+----+-----------+
"""

CLUSTER_ONLY_LEADER = u"""
+ Cluster: postgres (7020762932214296660) ----+---------+----+-----------+
| Member     | Host            | Role         | State   | TL | Lag in MB |
+------------+-----------------+--------------+---------+----+-----------+
| postgres-0 | 192.168.59.81   | Leader       | running |  9 |           |
+------------+-----------------+--------------+---------+----+-----------+"""

CLUSTER_NO_LEADER = u"""
+ Cluster: postgres (6992537990930645040) ----+---------+----+-----------+
| Member     | Host            | Role         | State   | TL | Lag in MB |
+------------+-----------------+--------------+---------+----+-----------+
| postgres-0 | 192.168.159.166 | Sync Standby | running |  7 |         0 |
+------------+-----------------+--------------+---------+----+-----------+"""

CLUSTER_LIST_SYNC = u"""
+ Cluster: postgres (6992537990930645040) ----+---------+----+-----------+
| Member     | Host            | Role         | State   | TL | Lag in MB |
+------------+-----------------+--------------+---------+----+-----------+
| postgres-0 | 192.168.159.166 | Sync Standby | running |  7 |         0 |
| postgres-1 | 192.168.253.231 | Leader       | running |  7 |           |
+------------+-----------------+--------------+---------+----+-----------+"""

NO_SYNC_STANDBY = u"""
+ Cluster: postgres (6992537990930645040) ---------+----+-----------+--------------+
| Member     | Host            | Role    | State   | TL | Lag in MB | Tags         |
+------------+-----------------+---------+---------+----+-----------+--------------+
| postgres-0 | 192.168.253.216 | Replica | running | 9  | 37027     | nosync: true |
| postgres-1 | 192.168.98.217  | Leader  | running | 9  |           |              |
+------------+-----------------+---------+---------+----+-----------+--------------+"""

PARSED_LIST = [
    {'Member': 'postgres-0', 'Host': '192.168.159.166', 'Role': 'Sync Standby',
     'State': 'running', 'TL': '7', 'Lag in MB': '0'},
    {'Member': 'postgres-1', 'Host': '192.168.253.231', 'Role': 'Leader',
     'State': 'running', 'TL': '7', 'Lag in MB': ''
                                                 ''}]


class TestCluster(unittest.TestCase):

    def setUp(self):
        self.shell = Mock()
        self.credentials = PostgresEnmCredentialsGroup()
        self.credentials.setup(PostgresUserEncryptedPasswordCenm)
        self.cluster = PostgresCluster(self.shell)

    def tearDown(self):
        self.shell = None
        self.credentials = None
        self.cluster = None
        self.terminal = None

    def test_overview_returns_parsed_data(self):
        self.shell.rune.return_value = CLUSTER_LIST_SYNC
        self.assertEqual(self.cluster.overview, PARSED_LIST)

    @patch('pyu.log.log.debug')
    def test_overview_raises_commandfailed(self, dlog):
        self.shell.rune.side_effect = CommandFailed(
            message='patronictl: command not found', output='Error',
            status_code='RL69', cmd='patronictl list')
        output = self.cluster.overview
        dlog.assert_called_with('Failed to get DocumentDB cluster overview: '
                                'patronictl: command not found', stdout=True)
        self.assertEqual(output, [])

    def test_instances_returns_postgres_instances(self):
        self.shell.rune.return_value = CLUSTER_LIST_3
        test_instances = self.cluster.instances
        self.assertEqual('Leader', test_instances[0].role)
        self.assertEqual('Pod: postgres-0 | Role: Leader | '
                         'Host: 192.168.59.81 | State: running',
                         str(test_instances[0]))

    def test_instance_returns_empty_list_exception(self):
        self.shell.rune.side_effect = CommandFailed(
            message='patronictl: command not found')
        self.assertEqual(0, len(self.cluster.instances))

    def test_leader_instance_is_returned(self):
        self.shell.rune.return_value = CLUSTER_LIST_3
        test_leader = self.cluster.leader
        self.assertEqual('postgres-0', test_leader.pod)
        self.assertEqual('Leader', test_leader.role)
        self.assertEqual('', test_leader.lag)
        self.assertEqual('Pod: postgres-0 | Role: Leader | '
                         'Host: 192.168.59.81 | State: running',
                         str(test_leader))

    def test_no_leader_instance_is_returned_exception(self):
        self.shell.rune.side_effect = CommandFailed(
            message='patronictl: command not found')
        self.assertEqual(None, self.cluster.leader)

    def test_only_leader_instance_is_returned_only_leader_in_cluster(self):
        self.shell.rune.return_value = CLUSTER_ONLY_LEADER
        self.assertEqual(None, self.cluster.replica)
        self.assertEqual([], self.cluster.followers)
        self.assertEqual('postgres-0', self.cluster.leader.pod)
        self.assertEqual(0, len(self.cluster.followers))

    def test_no_leader_when_cluster_has_no_leader(self):
        self.shell.rune.return_value = CLUSTER_NO_LEADER
        self.assertIsNone(self.cluster.leader)
        self.assertIsNone(self.cluster.replica)
        self.assertEqual('postgres-0', self.cluster.syncstandby.pod)
        self.assertEqual(1, len(self.cluster.followers))

    def test_syncstandby_is_in_cluster(self):
        self.shell.rune.return_value = CLUSTER_LIST_SYNC
        self.assertEqual('Sync Standby', self.cluster.syncstandby.role)

    def test_replica_instance_is_returned(self):
        self.shell.rune.return_value = NO_SYNC_STANDBY
        test_replica = self.cluster.replica
        self.assertEqual('postgres-0', test_replica.pod)
        self.assertEqual('Replica', test_replica.role)
        self.assertEqual('37027', test_replica.lag)

    def test_no_replica_instance_is_returned_exception(self):
        self.shell.rune.side_effect = CommandFailed(
            message='patronictl: command not found')
        self.assertEqual(None, self.cluster.replica)

    def test_follower_instances_are_returned(self):
        self.shell.rune.return_value = CLUSTER_LIST_3
        test_followers = self.cluster.followers
        self.assertEqual(2, len(test_followers))
        self.assertEqual('postgres-1', test_followers[0].pod)
        self.assertEqual('Sync Standby', test_followers[0].role)
        self.assertEqual('', test_followers[1].role)
        self.assertEqual('0', test_followers[1].lag)
        self.assertEqual('[Pod: postgres-1 | Role: Sync Standby | '
                         'Host: 192.168.156.181 | State: running, '
                         'Pod: postgres-2 | Role:  | '
                         'Host: 192.168.156.182 | State: running]',
                         str(test_followers))

    def test_no_follower_instances_are_returned_exception(self):
        self.shell.rune.side_effect = CommandFailed(
            message='patronictl: command not found')
        self.assertEqual(None, self.cluster.followers)

    def test_no_follower_instances_are_returned_only_leader_in_cluster(self):
        self.shell.rune.return_value = CLUSTER_ONLY_LEADER
        self.assertEqual(0, len(self.cluster.followers))

    def test_no_follower_instances_are_returned_for_cluster_of_1(self):
        self.shell.rune.side_effect = CommandFailed(
            message='patronictl: command not found')
        self.assertEqual(None, self.cluster.followers)


if __name__ == '__main__':
    unittest.main(verbosity=2)
