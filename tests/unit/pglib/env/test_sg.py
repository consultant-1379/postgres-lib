import unittest2 as unittest
from mock import Mock

from pglib.env.sg import PgServiceGroupBase


class MockSg(PgServiceGroupBase):
    def __init__(self, shell):
        super(MockSg, self).__init__(shell)


class TestPgServiceGroupBase(unittest.TestCase):

    def test_sg_name_is_set(self):
        from pglib.env import PgServiceGroupPenm
        shell = Mock()
        pg_sg = PgServiceGroupPenm(shell=shell)
        self.assertEqual('pg', pg_sg.name)

    def test_constants_class_is_set(self):
        from pglib.env.consts import PgCommonConstants
        self.assertEqual(PgCommonConstants,
                         PgServiceGroupBase.constants_class)

    def test_pg_service_raises_not_implemented_from_base(self):
        shell = Mock()
        mock_sg = MockSg(shell)
        with self.assertRaises(NotImplementedError):
            mock_sg.service

    def test_consts_are_set_for_penm(self):
        from pglib.env import PgServiceGroupPenm
        from pglib.env.penm.consts import PgConstantsPenm
        shell = Mock()
        pg_sg = PgServiceGroupPenm(shell=shell)
        shell.os.sg.pg = pg_sg
        self.assertEqual(type(shell.os.sg.pg.consts), PgConstantsPenm)

    def test_files_are_set_for_penm(self):
        from pglib.env import PgServiceGroupPenm
        shell = Mock()
        pg_sg = PgServiceGroupPenm(shell=shell)
        shell.os.sg.pg = pg_sg
        self.assertEqual('/ericsson/postgres', pg_sg.files.pg_mount.path)
        self.assertEqual('/opt/postgresql/bin/psql', pg_sg.files.psql.path)

    def test_pg_members_raises_not_implemented_from_base(self):
        shell = Mock()
        mock_sg = MockSg(shell)
        with self.assertRaises(NotImplementedError):
            mock_sg.members


if __name__ == '__main__':
    unittest.main(verbosity=2)
