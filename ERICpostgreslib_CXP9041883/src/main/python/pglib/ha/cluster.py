from pyu.log import log
from pyu.os.shell.errors import CommandFailed

from pglib.ha.instance import PostgresInstance
from pglib.utils.parser import BorderedTitleTableParser


class PostgresCluster(object):

    def __init__(self, shell):
        self.shell = shell

    @property
    def overview(self):
        try:
            out = self.shell.rune('patronictl list')
        except CommandFailed as err:
            log.debug('Failed to get DocumentDB cluster overview: %s' %
                      err.msg, stdout=True)
            return []
        parser = BorderedTitleTableParser(out)
        return parser.parse()

    @property
    def instances(self):
        overview = self.overview
        if not overview:
            return []
        return [PostgresInstance(self.shell, i) for i in overview]

    @property
    def leader(self):
        return next((i for i in self.instances if i.role == 'Leader'), None)

    @property
    def syncstandby(self):
        return next((i for i in self.instances if i.role == 'Sync Standby'),
                    None)

    @property
    def replica(self):
        return next((i for i in self.instances if i.role == 'Replica'),
                    None)

    @property
    def followers(self):
        return [i for i in self.instances if i.role != 'Leader'] if \
            self.instances else None
