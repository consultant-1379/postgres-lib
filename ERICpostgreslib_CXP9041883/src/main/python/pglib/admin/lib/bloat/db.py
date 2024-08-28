from pyu.decor.cache import cached_property
from pyu.enm.kube import EnmKubeSession
# pylint: disable=E0611
from pyu.ui.visual.colour import White
from pyu.ui.visual.format.grid import Table
from pyu.ui.visual.format.style import Style

from pglib.db.database import PgStore
from pglib.ha.cluster import PostgresCluster
from pglib.ha.pod import Role


class FsData(object):

    def __init__(self, db, shell):
        self.shell = shell
        self.db = next(filter(lambda x: x.name == db.name,
                              PgStore(self.shell).databases))

    @property
    def name(self):
        return self.db.name.capitalize()

    @property
    def db_size(self):
        return self.db.size

    @property
    def db_id(self):
        return self.db.id

    @property
    def mnt_used(self):
        return self._leader.pg_mount.used

    @property
    def mnt_size(self):
        return self._leader.pg_mount.size

    @property
    def mnt_used_perc(self):
        return self._leader.pg_mount.used_perc

    @property
    def mnt_avail(self):
        return self._leader.pg_mount.available

    @cached_property()
    def _leader(self):
        pod = Role()
        # Get FS data from the leader
        with EnmKubeSession(pod=pod.leader, container='postgres') as shell:
            cluster = PostgresCluster(shell)
        return cluster.leader


def get_bloat_table_data(data):
    body = [[b.table, b.rows, b.inserts, b.updates, b.deletes, b.bloat,
             b.autovac, b.last_autovac, b.analayze, b.last_autoanalayze]
            for b in data[:5]]
    header = ['Table', 'Row Count', 'Inserts', 'Updates', 'Deletes',
              'Bloat', 'Autovac Count', 'Last Autovac', 'Analyze Count',
              'Last Autoanalyze']
    return [header] + body


def show_bloat_table(data):
    table = Table(rows=get_bloat_table_data(data), cel_style=Style(White))
    table.show()


def get_total_db_bloat(data):
    total = 0
    for b in data:
        total += b.bloat
    return total
