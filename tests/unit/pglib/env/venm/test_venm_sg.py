import unittest2 as unittest
from mock import Mock


class TestPgServiceGroupVenm(unittest.TestCase):

    def test_credential_class_is_set_for_venm(self):
        from pglib.env import PgServiceGroupVenm
        from pglib.env.venm.credentials import \
            PostgresUserEncryptedPasswordVenm
        self.assertEqual(PostgresUserEncryptedPasswordVenm,
                         PgServiceGroupVenm.credentials_class)

    def test_service_is_set_for_venm(self):
        from pglib.env import PgServiceGroupVenm
        shell = Mock()
        pg_sg = PgServiceGroupVenm(shell)
        self.assertEqual('postgresql01', pg_sg.service)

    def test_constants_class_is_set_for_venm(self):
        from pglib.env import PgServiceGroupVenm
        from pglib.env.venm.consts import PgConstantsVenm
        self.assertEqual(PgConstantsVenm,
                         PgServiceGroupVenm.constants_class)

    def test_files_are_set_for_venm(self):
        from pglib.env import PgServiceGroupVenm
        shell = Mock()
        pg_sg = PgServiceGroupVenm(shell)
        shell.os.sg.pg = pg_sg
        self.assertEqual('/ericsson/postgres', pg_sg.files.pg_mount.path)
        self.assertEqual('/opt/postgresql/bin/psql', pg_sg.files.psql.path)

    def test_members(self):
        from pglib.env import PgServiceGroupVenm
        shell = Mock()
        pg_sg = PgServiceGroupVenm(shell)
        self.assertEqual(['postgres-0', 'postgres-1'], pg_sg.members)


if __name__ == '__main__':
    unittest.main(verbosity=2)
