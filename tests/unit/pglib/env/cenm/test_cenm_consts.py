import unittest2 as unittest
from mock import Mock


class TestCenmConsts(unittest.TestCase):

    def test_cenm_constants_are_set(self):
        from pglib.env.cenm.consts import PgConstantsCenm
        shell = Mock()
        consts = PgConstantsCenm(shell)
        self.assertEqual('postgres', consts.pg_host)
        self.assertEqual('/usr/bin', consts.pg_bin)
        self.assertEqual('pgdata', consts.pg_data_dir_name)
        self.assertEqual('/var/lib/postgresql/data', consts.pg_mount)
        self.assertEqual('/var/lib/postgresql/data/pgdata', consts.pg_data_dir)
        self.assertEqual('/var/lib/postgresql/data/pgdata/pg_wal',
                         consts.pg_wal_dir)
        self.assertEqual('/usr/bin/pg_isready', consts.pg_isready)
        self.assertEqual('/var/lib/postgresql/data/pgdata/pg_twophase', consts.pg_two_phase_dir)


if __name__ == '__main__':
    unittest.main(verbosity=2)
