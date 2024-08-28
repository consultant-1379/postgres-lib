from functools import reduce

from pyu.decor.cache import cached_property
from pyu.os.shell.errors import CommandFailed
from pyu.os.shell.local import LocalShellClient
from pyu.log import log

from pglib.errors import NoLeaderInCluster, LeaderNotRunning, \
    NoFollowerInCluster, FollowerNotRunning, NoAvailablePostgresPod


class Role(object):
    """
    A representation of a Kubernetes role for Postgres Pods
    The local Shell client has to be for the troubleshooting Pod
    as it contains the kubectl binaries.

    > leader: returns the name of the Pod e.g. postgres-0
    > follower: returns the replica role e.g. postgres-1
    > available attempts to return the leader node first, if not then the
      follower node. If not raises NoAvailablePostgresPod.
    """

    def __init__(self, shell=None):
        self.shell = shell or LocalShellClient()
        self.cmd = 'kubectl get pod -L role | grep postgres'

    @cached_property()
    def out(self):
        try:
            return self.shell.rune(self.cmd)
        except CommandFailed as err:
            log.error(err.msg, stdout=True)
            raise

    @property
    def leader(self):
        err_msg = 'Leader not available. Attempt to use follower role or ' \
                  'running pod.'
        try:
            master = reduce(lambda x, y: x + y, [line.split() for line in
                                                 self.out.split('\n') if
                                                 'master' in line])
        except TypeError:
            log.error(err_msg, stdout=True)
            raise NoLeaderInCluster(err_msg)
        if 'Running' not in master:
            log.error(err_msg, stdout=True)
            raise LeaderNotRunning(err_msg)
        return master[0]

    @property
    def follower(self):
        err_msg = 'Follower not available. Attempt to use leader role or ' \
                  'running pod.'
        try:
            follower = reduce(lambda x, y: x + y, [line.split() for line in
                                                   self.out.split('\n') if
                                                   'replica' in line])
        except TypeError:
            log.error(err_msg, stdout=True)
            raise NoFollowerInCluster(err_msg)
        if 'Running' not in follower:
            log.error(err_msg, stdout=True)
            raise FollowerNotRunning(err_msg)
        return follower[0]

    @property
    def available(self):
        try:
            return self.leader
        except (NoLeaderInCluster, LeaderNotRunning):
            pass
        try:
            return self.follower
        except (NoFollowerInCluster, FollowerNotRunning):
            raise NoAvailablePostgresPod('No available Postgres Pods.')
