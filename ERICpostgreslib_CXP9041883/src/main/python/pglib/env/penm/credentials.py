from pyu.decor.cache import cached_property
from pyu.enm.globalproperties import GlobalProperties
from pyu.tools.credentials import EnmUserEncryptedPasswordBase


class PostgresUserEncryptedPasswordPenm(EnmUserEncryptedPasswordBase):
    passkey_path = '/ericsson/tor/data/idenmgmt/postgresql01_passkey'

    @cached_property()
    def key(self):
        base_key = 'postgresql01_%s_password'
        key = base_key % ('admin' if self.user == 'postgres' else self.user)
        return key

    @cached_property()
    def passkey(self):  # pylint: disable=W0236
        with self.shell.os.fs.open(self.passkey_path) as passkey_file:
            return passkey_file.read().strip()

    @cached_property()
    def encrypted_password(self):   # pylint: disable=W0236
        gp = GlobalProperties(self.shell)
        return gp.get(self.key)

    def re_encrypt_password(self, new_passkey):
        pass

    def change_password(self, password):
        pass
