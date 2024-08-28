from pyu.log import log
from pyu.os.shell.local import LocalShellClient
# pylint: disable=E0611
from pyu.ui.visual.colour import Cyan, Yellow
from pyu.ui.visual.format.shortcuts import box, br, span

try:
    from pyu.enm.kube import EnmKubeSession
except ImportError:
    pass

from pglib.ha.pod import Role
from pglib.postgres import PsqlClient


def main():
    log.setup_syslog('pg_start_up', verbose=False)
    local_shell = LocalShellClient()
    pod = Role(local_shell)

    query = "select DATE_TRUNC('second',now() - pg_postmaster_" \
            "start_time());"

    box('Using the enmkubsession onto leader: %s pod' % pod.leader)
    session = EnmKubeSession(pod=pod.leader, container='postgres')
    with session as shell:
        psql = PsqlClient(shell)
        out_leader = psql.runq(query)
        log.debug('Start Time Leader: %s' % out_leader, stdout=True)
        br()

    box('Using the enmkubsession onto follower: %s pod' % pod.follower)
    session = EnmKubeSession(pod=pod.follower, container='postgres')
    with session as shell:
        psql = PsqlClient(shell)
        span(Yellow('Start time from follower:'))
        span(Cyan('Note we are providing host=\'localhost\' to the run query'))
        out_follower = psql.runq(query, host='localhost')
        log.debug('Start Time Follower: %s' % out_follower, stdout=True)


if __name__ == '__main__':
    main()
