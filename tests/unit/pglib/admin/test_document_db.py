import runpy

import unittest2 as unittest
from mock import patch, Mock

from pyu.os.fs.units import Size
from pyu.meta.compatibility import IS_PYTHON3

from pyu4t.stdoutmock import mock_stdout
from pyu4t.sysargs import SysArgsBlock

if IS_PYTHON3:
    from importlib import reload
else:
    from imp import reload

DB_DATA = {'16401': {'id': '16401', 'name': 'flsdb', 'size': '8256647'},
           '18274': {'id': '18274', 'name': 'idenmgmt', 'size': '10280071'},
           '21683': {'id': '21683', 'name': 'kpiservdb', 'size': '8281223'},
           '21720': {'id': '21720', 'name': 'openidm', 'size': '12532871'},
           '21210': {'id': '21210', 'name': 'pkicdpsdb', 'size': '8061443'}}

EXPECTED = [['id', 'name', 'size'],
            ['16401', 'flsdb', Size('8256647')],
            ['18274', 'idenmgmt', Size('10280071')],
            ['21683', 'kpiservdb', Size('8281223')],
            ['21720', 'openidm', Size('12532871')],
            ['21210', 'pkicdpsdb', Size('8061443')]]

OVERVIEW = u"""
+ Cluster: postgres (6992537990930645040) ----+---------+----+-----------+
| Member     | Host            | Role         | State   | TL | Lag in MB |
+------------+-----------------+--------------+---------+----+-----------+
| postgres-0 | 192.168.159.166 | Sync Standby | running |  7 |         0 |
| postgres-1 | 192.168.253.231 | Leader       | running |  7 |           |
+------------+-----------------+--------------+---------+----+-----------+"""


class TestDocumentDbAdmin(unittest.TestCase):

    @patch('pyu.os.system.OperatingSystem.env')
    def setUp(self, env):
        from pglib.admin.lib import cli, ui
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        self.shell = Mock()
        env.type = 'cENM'
        self.shell.os.env = env
        reload(cli)
        reload(ui)
        self.shell.os.sg.pg.credentials_class = \
            PgServiceGroupCenm.credentials_class
        credentials.setup(self.shell.os.sg.pg.credentials_class)

    def tearDown(self):
        self.shell = None

    @patch('pyu.enm.kube.EnmKubeSession')
    @patch('pglib.ha.pod.Role')
    @patch('pyu.os.system.OperatingSystem.env')
    @patch('pglib.admin.document_db_admin.LocalShellClient')
    @mock_stdout
    def test_document_db_admin_cli_help(self, out, err, lshell, env, role,
                                        eks):
        env.type = 'cENM'
        lshell.os.env = env
        role.available.return_value = 'postgres-0'

        with SysArgsBlock("document_db_admin.py", "--help"):
            exception = True
            try:
                runpy._run_module_as_main("pglib.admin.document_db_admin")
            except BaseException as exec:
                exception = exec
            self.assertTrue(isinstance(exception, SystemExit), str(exception))
            self.assertEqual(exception.code, 0)
        out.neutral_colour = True
        self.assertTrue('Document DB - ADMIN TOOL cENM\n\npositional '
                        'arguments:' in out)

    @patch('pyu.os.system.OperatingSystem.env')
    @patch('pglib.admin.controllers.cluster_overview.Role')
    @patch('pglib.admin.controllers.cluster_overview.EnmKubeSession')
    @patch('pglib.admin.document_db_admin.LocalShellClient')
    @mock_stdout
    def test_document_db_admin_cli_cluster_overview(self, out, err, lshell,
                                                    eks, role, env):
        from pglib.admin.controllers.cluster_overview import \
            ClusterOverviewController
        env.type = 'cENM'
        lshell.os.env = env
        role.available.return_value = 'postgres-0'
        eks.return_value.__enter__.return_value.rune.return_value = OVERVIEW

        cluster_overview = ClusterOverviewController(self.shell)
        cluster_overview.execute()

        with SysArgsBlock("document_db_admin.py", "cluster_overview"):
            runpy._run_module_as_main("pglib.admin.document_db_admin")
        out.neutral_colour = True
        lines = [line for line in out.lines
                 if line.strip().startswith("| ")]
        self.assertTrue(any("postgres-0" in line.split("|")[1]
                            for line in lines if line))
        self.assertTrue(any("postgres-1" in line.split("|")[1]
                            for line in lines if line))

    @patch('pglib.db.database.PgStore._get_databases_data')
    @patch('pyu.os.system.OperatingSystem.env')
    @patch('pglib.admin.controllers.db_sizes.LocalShellClient')
    @mock_stdout
    def test_document_db_admin_cli_db_sizes(self, out, err, lshell, env,
                                            db_data):
        from pglib.admin.controllers.db_sizes import DbSizeController
        env.type = 'cENM'
        lshell.os.env = env
        db_data.return_value = DB_DATA

        db_sizes = DbSizeController(self.shell)
        db_sizes.execute()

        with SysArgsBlock("document_db_admin.py", "db_sizes"):
            runpy._run_module_as_main("pglib.admin.document_db_admin")
        out.neutral_colour = True
        lines = [line for line in out.lines
                 if line.strip().startswith("|")]

        self.assertTrue(any("flsdb" in line.split("|")[2]
                            for line in lines if line))
        self.assertTrue(any("kpiservdb" in line.split("|")[2]
                            for line in lines if line))
        self.assertTrue(any("pkicdpsdb" in line.split("|")[2]
                            for line in lines if line))

    @patch('pyu.os.system.OperatingSystem.env')
    @patch('pglib.admin.document_db_admin.LocalShellClient')
    @mock_stdout
    def test_document_db_admin_exits_on_non_cenm(self, out, err, lshell, env):
        env.type = 'pENM'
        lshell.os.env = env

        with SysArgsBlock("document_db_admin.py", "--help"):
            exception = True
            try:
                runpy._run_module_as_main("pglib.admin.document_db_admin")
            except BaseException as exec:
                exception = exec
            self.assertTrue(isinstance(exception, SystemExit), str(exception))
            self.assertEqual(exception.code, 1)


if __name__ == '__main__':
    unittest.main()
