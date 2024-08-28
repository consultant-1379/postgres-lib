import unittest2 as unittest
from mock import Mock, patch

# TODO: change overview to the new patroni output
OVERVIEW = u"""
+ Cluster: postgres (6992537990930645040) ----+---------+----+-----------+
| Member     | Host            | Role         | State   | TL | Lag in MB |
+------------+-----------------+--------------+---------+----+-----------+
| postgres-0 | 192.168.159.166 | Sync Standby | running |  7 |         0 |
| postgres-1 | 192.168.253.231 | Leader       | running |  7 |           |
+------------+-----------------+--------------+---------+----+-----------+"""

NO_SYNC_STANDBY = u"""
+------------+-----------------+---------+---------+----+-----------+
| Member     | Host            | Role    | State   | TL | Lag in MB |
+------------+-----------------+---------+---------+----+-----------+
| postgres-0 | 192.168.253.216 | Replica | running | 9  | 37027     |
| postgres-1 | 192.168.98.217  | Leader  | running | 9  |           |
+------------+-----------------+---------+---------+----+-----------+"""

NO_SYNC_STANDBY_TAG = u"""
+------------+-----------------+---------+---------+----+-----------+--------------+
| Member     | Host            | Role    | State   | TL | Lag in MB | Tags         |
+------------+-----------------+---------+---------+----+-----------+--------------+
| postgres-0 | 192.168.253.216 | Replica | running | 9  | 37027     | nosync: true |
| postgres-1 | 192.168.98.217  | Leader  | running | 9  |           |              |
+------------+-----------------+---------+---------+----+-----------+--------------+"""

TAB_OVERVIEW = [
    ['Member', 'Host', 'Role', 'State', 'TL', 'Lag in MB'],
    ['postgres-0', '192.168.159.166', 'Sync Standby',
     'running', '7', '0'],
    ['postgres-1', '192.168.253.231', 'Leader',
     'running', '7', '']]

NO_SYNC_OVERVIEW = [
    ['Member', 'Host', 'Role', 'State', 'TL', 'Lag in MB'],
    ['postgres-0', '192.168.253.216', 'Replica',
     'running', '9', '37027'],
    ['postgres-1', '192.168.98.217', 'Leader',
     'running', '9', '']]

NO_SYNC_OVERVIEW_TAG = [
    ['Member', 'Host', 'Role', 'State', 'TL', 'Lag in MB', 'Tags'],
    ['postgres-0', '192.168.253.216', 'Replica',
     'running', '9', '37027', 'nosync: true'],
    ['postgres-1', '192.168.98.217', 'Leader',
     'running', '9', '', '']]

MSG = 'Cluster Issue: Failed to retrieve Postgres cluster-overview. Please ' \
      'try again later.\nIf issue persists please contact customer support.'
REP_MSG = 'Replication maybe broken due to Housekeeping.You may need to ' \
          're-initialise the follower node. Refer to the documentation.'


class TestControllerClusterOverview(unittest.TestCase):

    def setUp(self):
        from pglib.admin.controllers.cluster_overview import \
            ClusterOverviewController
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        self.shell = Mock()
        self.shell.os.sg.pg.credentials_class = \
            PgServiceGroupCenm.credentials_class
        credentials.setup(self.shell.os.sg.pg.credentials_class)
        self.co = ClusterOverviewController(self.shell)

    def tearDown(self):
        self.shell = None
        self.co = None

    @patch('pglib.admin.controllers.cluster_overview.Role')
    @patch('pglib.admin.controllers.cluster_overview.EnmKubeSession')
    def test_tabulated_cluster_overview_returned(self, eks, role):
        eks.return_value.__enter__.return_value.rune.return_value = OVERVIEW
        self.assertEqual(self.co.execute(), TAB_OVERVIEW)

    @patch('pglib.admin.controllers.cluster_overview.Role')
    @patch('pglib.admin.controllers.cluster_overview.EnmKubeSession')
    def test_cluster_returns_no_sync_standby(self, eks, role):
        eks.return_value.__enter__.return_value.rune.return_value = \
            NO_SYNC_STANDBY
        self.assertEqual(self.co.execute(), NO_SYNC_OVERVIEW)

    @patch('pglib.admin.controllers.cluster_overview.Role')
    @patch('pglib.admin.controllers.cluster_overview.EnmKubeSession')
    def test_cluster_returns_no_sync_standby_tag(self, eks, role):
        eks.return_value.__enter__.return_value.rune.return_value = \
            NO_SYNC_STANDBY_TAG
        self.assertEqual(self.co.execute(), NO_SYNC_OVERVIEW_TAG)

    @patch('pglib.admin.controllers.cluster_overview.Role')
    @patch('pglib.admin.controllers.cluster_overview.EnmKubeSession')
    def test_cluster_overview_shell_returns_empty_list(self, eks, role):
        from pyu.os.shell.errors import CommandFailed
        eks.return_value.__enter__.return_value.rune.side_effect = \
            CommandFailed(message='patronictl: command not found',
                          output='Error', status_code='RL69',
                          cmd='patronictl list')
        with self.assertRaises(IndexError):
            self.co.execute()

    def test_class_attributes_are_set(self):
        self.assertEqual(self.co.name, 'cluster_overview')
        self.assertEqual(self.co.title, 'Cluster Overview')
        self.assertEqual(self.co.rows_border, False)


if __name__ == '__main__':
    unittest.main(verbosity=2)
