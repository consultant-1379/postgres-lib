from pyu.enm.kube import EnmKubeSession
from pyu.log import log
from pyu.ui.menuapp.controller import TabulatedController

from pglib.ha.pod import Role
from pglib.errors import PsqlSessionException
from pglib.postgres import PsqlClient


class UptimeController(TabulatedController):
    name = "uptime"
    title = "Postgres Start and Uptime"
    rows_border = False

    def execute(self):
        header = [['PostgreSQL instance', 'Start-Time', 'Total Up-Time']]
        body = []

        pod = Role()

        with EnmKubeSession(pod=pod.leader, container='postgres') as shell:
            body.append([pod.leader, self.get_start_time(shell),
                         self.get_uptime(shell)])

        with EnmKubeSession(pod=pod.follower, container='postgres') as shell:
            body.append([pod.follower, self.get_start_time(shell),
                         self.get_uptime(shell)])

        return header + body

    def get_data(self, query, shell):
        psql = PsqlClient(shell)
        try:
            return psql.runq(query, remotely=False)
        except PsqlSessionException as err:
            log.error('Postgres session exception: %s' % err, stdout=True)
            return "Unavailable"

    def get_uptime(self, shell):
        query = 'select DATE_TRUNC(\'second\',' \
                'now() - pg_postmaster_start_time());'
        return self.get_data(query, shell)

    def get_start_time(self, shell):
        query = 'select DATE_TRUNC(\'second\',' \
                'pg_postmaster_start_time());'
        return self.get_data(query, shell)
