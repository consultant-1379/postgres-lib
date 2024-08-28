from pglib.env.venm.consts import PgConstantsVenm
from pglib.env.venm.credentials import PostgresUserEncryptedPasswordVenm
from pglib.env.sg import PgServiceGroupBase

from pyu.decor.cache import cached_property


class PgServiceGroupVenm(PgServiceGroupBase):
    credentials_class = PostgresUserEncryptedPasswordVenm
    constants_class = PgConstantsVenm

    @property
    def members(self):
        return ['postgres-0', 'postgres-1']

    @cached_property()
    def service(self):
        return 'postgresql01'
