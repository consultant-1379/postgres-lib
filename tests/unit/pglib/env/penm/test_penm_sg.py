import unittest2 as unittest
from mock import Mock


class TestPgServiceGroupPenm(unittest.TestCase):

    def test_credential_class_is_set_for_penm(self):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.penm.credentials import \
            PostgresUserEncryptedPasswordPenm
        self.assertEqual(PostgresUserEncryptedPasswordPenm,
                         PgServiceGroupPenm.credentials_class)

    def test_service_is_set_for_penm(self):
        from pglib.env import PgServiceGroupPenm
        shell = Mock()
        pg_sg = PgServiceGroupPenm(shell=shell)
        self.assertEqual('postgresql01', pg_sg.service)

    def test_constants_class_is_set_for_penm(self):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.penm.consts import PgConstantsPenm
        self.assertEqual(PgConstantsPenm,
                         PgServiceGroupPenm.constants_class)

    def test_files_are_set_for_penm(self):
        from pglib.env import PgServiceGroupPenm
        shell = Mock()
        pg_sg = PgServiceGroupPenm(shell=shell)
        shell.os.sg.pg = pg_sg
        self.assertEqual('/ericsson/postgres', pg_sg.files.pg_mount.path)
        self.assertEqual('/opt/postgresql/bin/psql', pg_sg.files.psql.path)

    def test_members(self):
        from pglib.env import PgServiceGroupPenm
        shell = Mock()
        pg_sg = PgServiceGroupPenm(shell=shell)
        self.assertEqual(['postgresql01'], pg_sg.members)


if __name__ == '__main__':
    unittest.main(verbosity=2)
