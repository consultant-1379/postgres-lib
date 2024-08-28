from pyu.decor.cache import cached_property
from pyu.enm.kube import EnmKubeSession
from pyu.log import log
from pyu.os.fs.usage import FileSystemUsage
from pyu.tools.dummy import DummyContextManager


class PostgresInstance(object):

    def __init__(self, shell, data):
        self.shell = shell
        self.consts = self.shell.os.sg.pg.consts
        self.pod = data['Member']
        self.role = data['Role']
        self.host = data['Host']
        self.lag = data['Lag in MB']
        self.state = data['State']

    @cached_property()
    def session(self):
        if self.shell.host.short_hostname == self.pod:
            # don't need to open another session if the current shell is
            # already opened
            return DummyContextManager(self.shell)
        return EnmKubeSession(pod=self.pod, container='postgres')

    @cached_property()
    def remote_shell(self):
        session = self.session
        return session.__enter__()

    @cached_property(2)
    def _data(self):
        fs = self.remote_shell.os.fs
        data = {'pg_data': fs.get(self.consts.pg_data_dir),
                'pg_wal': fs.get(self.consts.pg_wal_dir)}
        return data

    @property
    def pg_data_dir(self):
        pg_data = self._data['pg_data']
        if pg_data:
            return pg_data
        else:
            log.error("PG data directory is not available on %s" % self.pod,
                      stdout=True)
            return

    @property
    def pg_wal_dir(self):
        pg_wal = self._data['pg_wal']
        if pg_wal:
            return pg_wal
        else:
            log.error("PG WAL directory is not available on %s" % self.pod,
                      stdout=True)

    @cached_property(2)
    def pg_mount(self):
        usage = FileSystemUsage(self.remote_shell, self.consts.pg_mount)
        if usage:
            return usage
        else:
            log.error("Could not retrieve file system usage for "
                      "pg_mount on %s" % self.pod, stdout=True)

    def __repr__(self):
        return "Pod: %s | Role: %s | Host: %s | State: %s" \
               % (self.pod, self.role, self.host, self.state)
