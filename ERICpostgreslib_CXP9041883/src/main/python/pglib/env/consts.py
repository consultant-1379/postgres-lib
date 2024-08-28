"""
Common constants for Postgres
"""
from os.path import join

from pyu.decor.cache import cached_property


class PgCommonConstants(object):

    def __init__(self, shell):
        self._shell = shell
        self.pg_data_dir = join(self.pg_mount, self.pg_data_dir_name)
        self.pg_wal_dir = join(self.pg_data_dir, 'pg_wal')
        self.psql = join(self.pg_bin, 'psql')
        self.pg_isready = join(self.pg_bin, 'pg_isready')

    @cached_property()
    def pg_host(self):
        raise NotImplementedError

    @cached_property()
    def pg_bin(self):
        raise NotImplementedError

    @cached_property()
    def pg_data_dir_name(self):
        raise NotImplementedError

    @cached_property()
    def pg_mount(self):
        raise NotImplementedError

    @cached_property()
    def pg_two_phase_dir(self):
        raise NotImplementedError
