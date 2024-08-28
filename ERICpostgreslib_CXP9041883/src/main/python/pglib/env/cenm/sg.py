from pglib.env.cenm.consts import PgConstantsCenm
from pglib.env.cenm.credentials import PostgresUserEncryptedPasswordCenm
from pglib.env.sg import PgServiceGroupBase

from pyu.decor.cache import cached_property


class PgServiceGroupCenm(PgServiceGroupBase):
    credentials_class = PostgresUserEncryptedPasswordCenm
    constants_class = PgConstantsCenm

    @property
    def members(self):
        pods = self.shell.os.clustered.k8s.pods
        return [p.name for p in pods if p.name.startswith('postgres')
                and 'bragent' not in p.name]

    @cached_property()
    def service(self):
        return 'postgres'
