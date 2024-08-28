from pyu.meta.design import Singleton
from pyu.tools.credentials import CredentialsGroupBase, \
    EnmUserEncryptedPasswordBase, credential_based


class PostgresEnmCredentialsGroup(CredentialsGroupBase):
    """ Singleton that holds Postgres users credentials
    """

    __metaclass__ = Singleton

    @credential_based(EnmUserEncryptedPasswordBase)
    def postgres(self):
        return 'postgres'


credentials = PostgresEnmCredentialsGroup()
