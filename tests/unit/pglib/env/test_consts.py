import unittest2 as unittest
from mock import Mock

from pglib.env.consts import PgCommonConstants


class MockConsts(PgCommonConstants):
    def __init__(self, s, m):
        self._pg_mount = m
        self.shell = s

    @property
    def pg_mount(self):
        return self._pg_mount


class TestConsts(unittest.TestCase):

    def setUp(self):
        self.shell = Mock()

    def tearDown(self):
        self.shell = None

    def test_pg_host_raises_not_implemented_from_base(self):
        with self.assertRaises(NotImplementedError):
            MockConsts(self.shell, m='/var/test').pg_host

    def test_pg_bin_raises_not_implemented_from_base(self):
        with self.assertRaises(NotImplementedError):
            MockConsts(self.shell, m='/var/test').pg_bin

    def test_pg_data_dir_name_raises_not_implemented_from_base(self):
        with self.assertRaises(NotImplementedError):
            MockConsts(self.shell, m='/var/test').pg_data_dir_name

    def test_pg_mount_raises_not_implemented_from_base(self):
        class MockConstsII(PgCommonConstants):
            def __init__(self, s):
                self.shell = s

        with self.assertRaises(NotImplementedError):
            MockConstsII(self.shell).pg_mount

    def test_pgcommonconstants_inheritance_works(self):
        from pglib.env.penm.consts import PgConstantsPenm
        consts = PgConstantsPenm(self.shell)
        self.assertEqual('postgresql01', consts.pg_host)
        self.assertEqual('/opt/postgresql/bin', consts.pg_bin)
        self.assertEqual('data', consts.pg_data_dir_name)
        self.assertEqual('/ericsson/postgres', consts.pg_mount)


if __name__ == '__main__':
    unittest.main(verbosity=2)
