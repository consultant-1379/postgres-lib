from pglib.env.penm.consts import PgConstantsPenm
from pglib.env.penm.credentials import PostgresUserEncryptedPasswordPenm
from pglib.env.sg import PgServiceGroupBase

from pyu.decor.cache import cached_property


class PgServiceGroupPenm(PgServiceGroupBase):
    credentials_class = PostgresUserEncryptedPasswordPenm
    constants_class = PgConstantsPenm

    @property
    def members(self):
        return ['postgresql01']

    @cached_property()
    def service(self):
        return 'postgresql01'
