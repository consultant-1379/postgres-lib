from pyu.enm.kube import EnmKubeSession
from pyu.os.shell.local import LocalShellClient
from pyu.ui.menuapp.controller import TabulatedController
# pylint: disable=E0611
from pyu.ui.visual.colour import Yellow
from pyu.ui.visual.format.grid import Table
from pyu.ui.visual.format.shortcuts import br, span

from pglib.errors import NonReplicatingCluster
from pglib.ha.cluster import PostgresCluster
from pglib.ha.pod import Role
from pglib.postgres import PsqlClient


def show_overview(overview):
    header = list(overview[0].keys())
    body = [list(i.values()) for i in overview]
    t_cluster = Table(rows=[header] + body, rows_border=True)
    br()
    span(Yellow('Cluster Overview'))
    br()
    t_cluster.show()


class ReplicationLagController(TabulatedController):
    name = "lag"
    title = "Replication Lag"
    rows_border = False

    def execute(self):
        rep_msg = 'Replication maybe broken due to Housekeeping.You may ' \
                  'need to re-initialise the follower node. Refer to the ' \
                  'documentation.'
        pod = Role(LocalShellClient())
        with EnmKubeSession(pod=pod.available, container='postgres') as shell:
            cluster = PostgresCluster(shell)

        show_overview(cluster.overview)

        if not cluster.syncstandby:
            raise NonReplicatingCluster(rep_msg)

        query = 'SELECT application_name AS pod,' \
                'cast (backend_start as timestamp(0)), state, sent_lsn, ' \
                'replay_lsn, write_lag, replay_lag, sync_state FROM ' \
                'pg_stat_replication ORDER BY pod;'

        psql = PsqlClient(shell)
        out = psql.run(query, remotely=False)
        # pylint: disable=R1721
        lines = [line for line in out.split('\n')]
        header = list(lines[0].split('|'))
        body = list(line.split('|') for line in lines[1:-2])
        br()
        br()
        return [header] + body
