import unittest2 as unittest
from mock import patch

from pglib.ha.pod import Role

from pglib.errors import NoLeaderInCluster, LeaderNotRunning, \
    NoFollowerInCluster, FollowerNotRunning, NoAvailablePostgresPod

from pyu.os.shell.errors import CommandFailed

NORMAL = u"""
postgres-0                                            3/3     Running     0          4d17h   replica
postgres-1                                            3/3     Running     0          6d21h   master
postgres-bragent-5c6d48697b-896wp                     3/3     Running     0          17d   
"""

NO_LEADER = u"""
postgres-0                                            3/3     Running     0          4d17h   replica
postgres-1                                            3/3     Running     0          6d21h   
postgres-bragent-5c6d48697b-896wp                     3/3     Running     0          17d   
"""

LEADER_NOT_RUNNING = u"""
postgres-0                                            3/3     Running     0          4d17h   replica
postgres-1                                            3/3     stopped     0          6d21h   master
postgres-bragent-5c6d48697b-896wp                     3/3     Running     0          17d   
"""

NO_FOLLOWER = u"""
postgres-0                                            3/3     Running     0          4d17h   
postgres-1                                            3/3     Running     0          6d21h   master
postgres-bragent-5c6d48697b-896wp                     3/3     Running     0          17d   
"""

FOLLOWER_NOT_RUNNING = u"""
postgres-0                                            3/3     stopped     0          4d17h   replica
postgres-1                                            3/3     Running     0          6d21h   master
postgres-bragent-5c6d48697b-896wp                     3/3     Running     0          17d   
"""

NO_LEADER_NO_FOLLOWER = u"""
postgres-0                                            3/3     Running     0          4d17h   
postgres-1                                            3/3     Running     0          6d21h   
postgres-bragent-5c6d48697b-896wp                     3/3     Running     0          17d   
"""

LEADER_AND_FOLLOWER_NOT_RUNNING = u"""
postgres-0                                            3/3     stopped     0          4d17h   replica
postgres-1                                            3/3     stopped     0          6d21h   master
postgres-bragent-5c6d48697b-896wp                     3/3     Running     0          17d   
"""

leader_msg = 'Leader not available. Attempt to use follower role or ' \
             'running pod.'
follower_msg = 'Follower not available. Attempt to use leader role or ' \
               'running pod.'


class TestPod(unittest.TestCase):

    @patch('pglib.ha.pod.LocalShellClient')
    def test_leader_is_running(self, lshell):
        lshell.rune.return_value = NORMAL
        role = Role(lshell)
        self.assertEqual('postgres-1', role.leader)

    @patch('pyu.log.log.error')
    @patch('pglib.ha.pod.LocalShellClient')
    def test_no_leader_in_cluster(self, lshell, elog):
        lshell.rune.return_value = NO_LEADER
        role = Role(lshell)
        with self.assertRaises(NoLeaderInCluster):
            role.leader
        elog.assert_called_with(leader_msg, stdout=True)

    @patch('pyu.log.log.error')
    @patch('pglib.ha.pod.LocalShellClient')
    def test_leader_not_running(self, lshell, elog):
        lshell.rune.return_value = LEADER_NOT_RUNNING
        role = Role(lshell)
        with self.assertRaises(LeaderNotRunning):
            role.leader
        elog.assert_called_with(leader_msg, stdout=True)

    @patch('pglib.ha.pod.LocalShellClient')
    def test_follower_is_running(self, lshell):
        lshell.rune.return_value = NORMAL
        role = Role(lshell)
        self.assertEqual('postgres-0', role.follower)

    @patch('pyu.log.log.error')
    @patch('pglib.ha.pod.LocalShellClient')
    def test_no_folllower_in_cluster(self, lshell, elog):
        lshell.rune.return_value = NO_FOLLOWER
        role = Role(lshell)
        with self.assertRaises(NoFollowerInCluster):
            role.follower
        elog.assert_called_with(follower_msg, stdout=True)

    @patch('pyu.log.log.error')
    @patch('pglib.ha.pod.LocalShellClient')
    def test_leader_not_running(self, lshell, elog):
        lshell.rune.return_value = FOLLOWER_NOT_RUNNING
        role = Role(lshell)
        with self.assertRaises(FollowerNotRunning):
            role.follower
        elog.assert_called_with(follower_msg, stdout=True)

    @patch('pglib.ha.pod.LocalShellClient')
    def test_available_returns_leader(self, lshell):
        lshell.rune.return_value = NORMAL
        role = Role(lshell)
        self.assertEqual('postgres-1', role.available)

    @patch('pglib.ha.pod.LocalShellClient')
    def test_available_returns_follower(self, lshell):
        lshell.rune.return_value = NO_LEADER
        role = Role(lshell)
        self.assertEqual('postgres-0', role.available)

    @patch('pglib.ha.pod.LocalShellClient')
    def test_available_returns_no_pods(self, lshell):
        lshell.rune.return_value = NO_LEADER_NO_FOLLOWER
        role = Role(lshell)
        with self.assertRaises(NoAvailablePostgresPod):
            role.available

    @patch('pyu.log.log.error')
    @patch('pglib.ha.pod.LocalShellClient')
    def test_pod_raises_commandfailed(self, lshell, elog):
        lshell.rune.side_effect = CommandFailed(
            message='kubectl: command not found', output='Error',
            status_code='RL69', cmd='kubectl Bo Noah')
        role = Role(lshell)
        with self.assertRaises(CommandFailed):
            role.available
        elog.assert_called_with('kubectl: command not found', stdout=True)


if __name__ == '__main__':
    unittest.main()
