import unittest2 as unittest
from mock import patch, Mock

RESULT = [('act_ru_job', 6, 47623, 28466, 47623, 528, 46,
           '2021-11-25 15:21:54.551008+00', 170,
           '2021-11-25 15:03:54.494919+00'),
          ('act_ru_execution', 23, 34735, 47623, 34735, 384, 34,
           '2021-11-25 15:23:54.56314+00', 170,
           '2021-11-25 15:09:54.507483+00')]


class TestControllerVacuum(unittest.TestCase):

    def setUp(self):
        from pglib.admin.controllers.vacuum import VacuumController
        from pglib.env import PgServiceGroupCenm
        from pglib.env.cenm.consts import PgConstantsCenm
        from pglib.env.credentials import credentials
        self.shell = Mock()
        self.shell.os.sg.pg.credentials_class = \
            PgServiceGroupCenm.credentials_class
        credentials.setup(self.shell.os.sg.pg.credentials_class)
        self.shell.os.sg.pg.consts = PgConstantsCenm
        self.shell.os.sg.pg.consts.psql = 'psql'
        self.vac = VacuumController(self.shell)

    @patch('pglib.admin.controllers.vacuum.PsqlClient')
    @patch('pglib.postgres.LocalShellClient')
    @patch('pglib.admin.lib.bloat.cmds.PostgresSession')
    @patch('pglib.postgres.PostgresSession')
    @patch('pglib.db.database.DatabaseInstance')
    @patch('pglib.admin.controllers.vacuum.FsData')
    def test_vacuum_output(self, fsdata, db, ses, bses, lshell, psq):
        from pglib.admin.lib.bloat.db import get_total_db_bloat
        from pglib.db.database import Bloat
        from pyu.os.fs.units import Size
        from pglib.env import PgServiceGroupCenm
        from pglib.env.cenm.consts import PgConstantsCenm
        from pglib.env.credentials import credentials

        lshell.os.sg.pg.credentials_class = \
            PgServiceGroupCenm.credentials_class
        credentials.setup(lshell.os.sg.pg.credentials_class)
        lshell.os.sg.pg.consts = PgConstantsCenm
        lshell.os.sg.pg.consts.psql = 'psql'
        lshell.run.return_value = 0
        db.name = 'test_db'
        db.id = '1'
        db.size = Size('2G')
        pre = fsdata
        pre.name = db.name
        pre.db_size = db.size
        pre.db_id = db.id
        pre.mnt_used = '4GB'
        pre.mnt_size = '8GB'
        pre.mnt_used_perc = '50%'
        pre.mnt_avail = '4GB'
        pre_bloat = [Bloat(*bloat) for bloat in RESULT]
        db.bloat = pre_bloat
        pre_t_bloat = get_total_db_bloat(pre_bloat)
        out = self.vac.execute(db, pre, pre_t_bloat)
        self.assertIn('Limiting connections on test_db', next(out))
        self.assertIn('Vacuuming test_db.', next(out))
        self.assertIn('Resetting connections on test_db:', next(out))

    def test_class_attributes_are_set(self):
        self.assertEqual(self.vac.name, 'vacuuming')
        self.assertEqual(self.vac.title, 'Vacuum Tool')


if __name__ == '__main__':
    unittest.main()
