from pyu.enm.kube import EnmKubeSession
from pyu.ui.menuapp.controller import TabulatedController

from pglib.ha.cluster import PostgresCluster
from pglib.ha.pod import Role


class ClusterOverviewController(TabulatedController):
    name = 'cluster_overview'
    title = 'Cluster Overview'
    rows_border = False

    def execute(self):
        pod = Role(self.shell)
        with EnmKubeSession(pod=pod.available, container='postgres') as shell:
            overview = PostgresCluster(shell).overview

        header = list(overview[0].keys())
        body = [list(i.values()) for i in overview]
        return [header] + body
