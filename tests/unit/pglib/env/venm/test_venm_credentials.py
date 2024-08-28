from io import StringIO

import unittest2 as unittest
from mock import Mock, patch

PASSKEY = u"""fake_pass_key"""
GP_FILE = u"""
pmserv=pmserv
postgres=postgres
postgresql01_admin_password=fake_encrypted_pass
"""


class TestPostgresUserEncryptedPasswordVenm(unittest.TestCase):

    @patch('pyu.security.cryptor.OpenSsl128CbcCryptorBash.decrypt',
           return_value='test_password')
    @patch('pyu.enm.globalproperties.GlobalProperties.get')
    def test_postgres_venm_user_password_is_set(self, _gp, _pass):
        from pglib.env import PgServiceGroupVenm
        from pglib.env import credentials
        from imp import reload
        reload(credentials)
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupVenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        mock_file = Mock(__enter__=Mock(), __exit__=Mock())
        mock_file.__enter__.return_value = StringIO(PASSKEY)
        shell.os.fs.open.return_value = mock_file
        shell.os.fs.get.return_value = StringIO(PASSKEY)
        shell.environ.get.return_value = ""
        self.assertEqual('fake_pass_key', credentials(shell).postgres.passkey)
        self.assertEqual('test_password', credentials(shell).postgres.password)

    def test_passkey_is_set(self):
        from pglib.env.venm.credentials import \
            PostgresUserEncryptedPasswordVenm
        self.assertEqual('/ericsson/tor/data/idenmgmt/postgresql01_passkey',
                         PostgresUserEncryptedPasswordVenm.passkey_path)

    def test_admin_key_is_returned(self):
        from pglib.env import PgServiceGroupVenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupVenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        # Transforming the credential obj to have a shell => __call__(shell)
        # credentials = credentials(shell=shell)
        self.assertEqual('postgresql01_admin_password',
                         credentials(shell).postgres.key)

    def test_other_key_is_returned(self):
        from pglib.env.venm.credentials import \
            PostgresUserEncryptedPasswordVenm
        pg_encrypt_pass = PostgresUserEncryptedPasswordVenm('other')
        self.assertEqual('postgresql01_other_password', pg_encrypt_pass.key)

    def test_postgres_passkey_is_returned(self):
        from pglib.env import PgServiceGroupVenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupVenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        mock_file = Mock(__enter__=Mock(), __exit__=Mock())
        mock_file.__enter__.return_value = StringIO(PASSKEY)
        shell.os.fs.open.return_value = mock_file
        self.assertEqual('fake_pass_key', credentials(shell).postgres.passkey)

    def test_postgres_encrypted_password_is_returned(self):
        from pglib.env import PgServiceGroupVenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupVenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        mock_file = Mock(__enter__=Mock(), __exit__=Mock())
        mock_file.__enter__.return_value = StringIO(GP_FILE)
        shell.os.fs.open.return_value = mock_file
        shell.os.fs.get.return_value = StringIO(GP_FILE)
        self.assertEqual('fake_encrypted_pass',
                         credentials(shell).postgres.encrypted_password)


if __name__ == '__main__':
    unittest.main(verbosity=2)
