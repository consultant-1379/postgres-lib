import unittest2 as unittest
from mock import Mock


class TestPgServiceGroupCenm(unittest.TestCase):

    def test_credential_class_is_set_for_cenm(self):
        from pglib.env.cenm.credentials import \
            PostgresUserEncryptedPasswordCenm
        from pglib.env.cenm.sg import PgServiceGroupCenm
        self.assertEqual(PostgresUserEncryptedPasswordCenm,
                         PgServiceGroupCenm.credentials_class)

    def test_service_is_set_for_cenm(self):
        from pglib.env import PgServiceGroupCenm
        shell = Mock()
        pg_sg = PgServiceGroupCenm(shell)
        self.assertEqual('postgres', pg_sg.service)

    def test_constants_class_is_set_for_cenm(self):
        from pglib.env.cenm.consts import PgConstantsCenm
        from pglib.env.cenm.sg import PgServiceGroupCenm
        self.assertEqual(PgConstantsCenm,
                         PgServiceGroupCenm.constants_class)

    def test_files_are_set_for_cenm(self):
        from pglib.env import PgServiceGroupCenm
        shell = Mock()
        pg_sg = PgServiceGroupCenm(shell)
        shell.os.sg.pg = pg_sg
        self.assertEqual('/var/lib/postgresql/data', pg_sg.files.pg_mount.path)
        self.assertEqual('/usr/bin/psql', pg_sg.files.psql.path)

    def test_members_returns_list_of_postgres_pods(self):
        from pglib.env.cenm.sg import PgServiceGroupCenm

        class Dummy:
            def __init__(self, name):
                self.name = name

        pod1 = Dummy(name='pmserv-123')
        pod2 = Dummy(name='postgres-0')
        pod3 = Dummy(name='postgres-1')
        pod4 = Dummy(name='postgres-bragent')
        pod5 = Dummy(name='rwxpvc-bragent')
        pods = [pod1, pod2, pod3, pod4, pod5]

        shell = Mock()
        shell.os.clustered.k8s.pods = pods
        pg_sg = PgServiceGroupCenm(shell=shell)
        self.assertEqual(['postgres-0', 'postgres-1'], pg_sg.members)


if __name__ == '__main__':
    unittest.main(verbosity=2)
