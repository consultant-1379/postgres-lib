import unittest2 as unittest
from mock import Mock


class TestPenmConsts(unittest.TestCase):

    def test_venm_constants_are_set(self):
        from pglib.env.penm.consts import PgConstantsPenm
        shell = Mock()
        consts = PgConstantsPenm(shell)
        self.assertEqual('postgresql01', consts.pg_host)
        self.assertEqual('/opt/postgresql/bin', consts.pg_bin)
        self.assertEqual('data', consts.pg_data_dir_name)
        self.assertEqual('/ericsson/postgres', consts.pg_mount)
        self.assertEqual('/ericsson/postgres/data', consts.pg_data_dir)
        self.assertEqual('/ericsson/postgres/data/pg_wal', consts.pg_wal_dir)
        self.assertEqual('/opt/postgresql/bin/psql', consts.psql)
        self.assertEqual('/opt/postgresql/bin/pg_isready', consts.pg_isready)
        self.assertEqual('/ericsson/postgres/data/pg_twophase', consts.pg_two_phase_dir)


if __name__ == '__main__':
    unittest.main(verbosity=2)
