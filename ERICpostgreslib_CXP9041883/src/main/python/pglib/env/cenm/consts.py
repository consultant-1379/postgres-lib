from pglib.env.consts import PgCommonConstants

from pyu.decor.cache import cached_property


class PgConstantsCenm(PgCommonConstants):

    @cached_property()
    def pg_host(self):
        return 'postgres'

    @cached_property()
    def pg_bin(self):
        return '/usr/bin'

    @cached_property()
    def pg_data_dir_name(self):
        return 'pgdata'

    @cached_property()
    def pg_mount(self):
        return '/var/lib/postgresql/data'

    @cached_property()
    def pg_two_phase_dir(self):
        return '/var/lib/postgresql/data/pgdata/pg_twophase'
