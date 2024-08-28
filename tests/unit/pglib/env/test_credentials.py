import unittest2 as unittest
from mock import Mock

from pglib.env import PgServiceGroupCenm
from pglib.env.credentials import PostgresEnmCredentialsGroup
from pglib.env.credentials import credentials


class TestPostgresEnmCredentialsGroup(unittest.TestCase):

    def setUp(self):
        self.shell = Mock()
        self.shell.os.sg.pg = PgServiceGroupCenm
        credentials.setup(self.shell.os.sg.pg.credentials_class)

    def tearDown(self):
        self.shell = None

    def test_a_single_instance_of_postgres_creds_is_initialised(self):
        shell2 = Mock()
        cred1 = PostgresEnmCredentialsGroup(self.shell)
        cred2 = PostgresEnmCredentialsGroup(self.shell)
        cred3 = PostgresEnmCredentialsGroup(shell2)
        self.assertEqual(cred1, cred2)
        self.assertNotEqual(cred1, cred3)

    def test_credential_attribute_returns_postgres(self):
        # Transforming the credential obj to have a shell => __call__(shell)
        # credentials = credentials(shell=shell)
        # retrieve the key as the attribute is a lazy object
        self.assertEqual('postgresql01_admin_password', credentials(
            self.shell).postgres.key)


if __name__ == '__main__':
    unittest.main(verbosity=2)
