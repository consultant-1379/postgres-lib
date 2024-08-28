from pglib.env.consts import PgCommonConstants

from pyu.decor.cache import cached_property


class PgConstantsVenm(PgCommonConstants):

    @cached_property()
    def pg_host(self):
        return 'postgresql01'

    @cached_property()
    def pg_bin(self):
        return '/opt/postgresql/bin'

    @cached_property()
    def pg_data_dir_name(self):
        return 'data'

    @cached_property()
    def pg_mount(self):
        return '/ericsson/postgres'

    @cached_property()
    def pg_two_phase_dir(self):
        return '/ericsson/postgres/data/pg_twophase'
