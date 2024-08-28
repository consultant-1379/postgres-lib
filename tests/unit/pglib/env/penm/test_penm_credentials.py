from io import StringIO

import unittest2 as unittest
from mock import Mock, patch

PASSKEY = u"""fake_pass_key"""
GP_FILE = u"""
pmserv=pmserv
postgres=postgres
postgresql01_admin_password=fake_encrypted_pass
"""


class TestPostgresUserEncryptedPasswordPenm(unittest.TestCase):

    @patch('pyu.security.cryptor.OpenSsl128CbcCryptorBash.decrypt',
           return_value='test_password')
    @patch('pyu.enm.globalproperties.GlobalProperties.get')
    def test_postgres_penm_user_password_is_set(self, _gp, _pass):
        from pglib.env import PgServiceGroupPenm
        from pglib.env import credentials
        # Need to reload credentials as they are cached due to import and
        # affect test leakage for cENM
        from imp import reload
        reload(credentials)
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        mock_file = Mock(__enter__=Mock(), __exit__=Mock())
        mock_file.__enter__.return_value = StringIO(PASSKEY)
        shell.os.fs.open.return_value = mock_file
        shell.environ.get.return_value = ""
        shell.os.fs.get.return_value = StringIO(PASSKEY)
        self.assertEqual('fake_pass_key', credentials(shell).postgres.passkey)
        self.assertEqual('test_password', credentials(shell).postgres.password)

    def test_passkey_is_set(self):
        from pglib.env.penm.credentials import \
            PostgresUserEncryptedPasswordPenm
        self.assertEqual('/ericsson/tor/data/idenmgmt/postgresql01_passkey',
                         PostgresUserEncryptedPasswordPenm.passkey_path)

    def test_admin_key_is_returned(self):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        # Transforming the credential obj to have a shell => __call__(shell)
        # credentials = credentials(shell=shell)
        self.assertEqual('postgresql01_admin_password',
                         credentials(shell).postgres.key)

    def test_other_key_is_returned(self):
        from pglib.env.penm.credentials import \
            PostgresUserEncryptedPasswordPenm
        pg_encrypt_pass = PostgresUserEncryptedPasswordPenm('other')
        self.assertEqual('postgresql01_other_password', pg_encrypt_pass.key)

    def test_postgres_passkey_is_returned(self):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        mock_file = Mock(__enter__=Mock(), __exit__=Mock())
        mock_file.__enter__.return_value = StringIO(PASSKEY)
        shell.os.fs.open.return_value = mock_file
        self.assertEqual('fake_pass_key', credentials(shell).postgres.passkey)

    def test_postgres_encrypted_password_is_returned(self):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.credentials import credentials
        shell = Mock()
        shell.os.sg.pg = PgServiceGroupPenm(shell)
        credentials.setup(shell.os.sg.pg.credentials_class)
        mock_file = Mock(__enter__=Mock(), __exit__=Mock())
        mock_file.__enter__.return_value = StringIO(GP_FILE)
        shell.os.fs.open.return_value = mock_file
        shell.os.fs.get.return_value = StringIO(GP_FILE)
        self.assertEqual('fake_encrypted_pass',
                         credentials(shell).postgres.encrypted_password)


if __name__ == '__main__':
    unittest.main(verbosity=2)
