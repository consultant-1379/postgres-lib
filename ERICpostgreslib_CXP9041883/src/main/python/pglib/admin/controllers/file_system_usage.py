from pyu.enm.kube import EnmKubeSession
from pyu.os.shell.local import LocalShellClient
from pyu.parallel.threads import ThreadPool
from pyu.ui.menuapp.controller import TabulatedController

from pglib.ha.cluster import PostgresCluster
from pglib.ha.pod import Role


class FileSystemUsageController(TabulatedController):
    name = 'fs_usage'
    title = 'Filesystem Usage'
    rows_border = False

    def execute(self):
        pod = Role(LocalShellClient())
        with EnmKubeSession(pod=pod.available, container='postgres') as shell:
            cluster = PostgresCluster(shell)

        instance_values = cluster.instances
        if not instance_values:
            raise IndexError('No valid Postgres instances data retrieved')

        body = []

        def _get(i):
            body.append([i.pod, str(i.pg_data_dir.size),
                         str(i.pg_wal_dir.size),
                         str(i.pg_mount.size), str(i.pg_mount.available),
                         str(i.pg_mount.used), i.pg_mount.available_perc,
                         i.pg_mount.used_perc])

        pool = ThreadPool()
        for c, instance in enumerate(instance_values):
            pool.add_named(_get, 'instance_%s' % c, instance)
        pool.start()
        pool.wait()
        header = ['Pod', 'Data Dir', 'Wal Dir', 'Mnt Size', 'Mnt Avail',
                  'Mnt Used', 'Avail %', 'Used %']
        return [header] + body
