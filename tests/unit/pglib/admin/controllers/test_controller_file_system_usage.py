import unittest2 as unittest
from mock import Mock, patch, PropertyMock

from pyu.os.fs.units import Size


class DummyFile:
    def __init__(self, s):
        self._size = s

    @property
    def size(self):
        return Size(self._size)

    @property
    def available(self):
        return Size('80g') if self.size > Size('101g') else \
            Size('60g')

    @property
    def used(self):
        return self.size - self.available

    @property
    def available_perc(self):
        return str(int((self.available / self.size) * 100)) + '%'

    @property
    def used_perc(self):
        return str(int((self.used / self.size) * 100)) + '%'


class DummyInst:
    def __init__(self, pod, pg_data_dir, pg_wal_dir, pg_mount):
        self._pod = pod
        self._pg_data_dir = pg_data_dir
        self._pg_wal_dir = pg_wal_dir
        self._pg_mount = pg_mount

    @property
    def pod(self):
        return self._pod

    @property
    def pg_data_dir(self):
        return DummyFile(self._pg_data_dir)

    @property
    def pg_wal_dir(self):
        return DummyFile(self._pg_wal_dir)

    @property
    def pg_mount(self):
        return DummyFile(self._pg_mount)


class TestControllerFileSystemUsage(unittest.TestCase):

    def setUp(self):
        from pglib.admin.controllers.file_system_usage import \
            FileSystemUsageController
        from pglib.ha.cluster import PostgresCluster
        self.shell = Mock()
        self.fsc = FileSystemUsageController(shell=self.shell)
        self.cluster = PostgresCluster(self.shell)

    def tearDown(self):
        self.shell = None
        self.fsc = None
        self.cluster = None

    @patch('pglib.ha.cluster.PostgresCluster.instances',
           new_callable=PropertyMock)
    @patch('pglib.admin.controllers.file_system_usage.Role')
    @patch('pglib.admin.controllers.file_system_usage.EnmKubeSession')
    def test_tabulated_file_system_usage_returns_data(self, eks, pod, pg_inst):
        inst1 = DummyInst('postgres-0', '40g', '5g', '100g')
        inst2 = DummyInst('postgres-1', '120g', '50g', '200g')

        pg_inst.return_value = [inst1, inst2]

        self.assertEqual([['Pod', 'Data Dir', 'Wal Dir', 'Mnt Size',
                           'Mnt Avail',
                           'Mnt Used', 'Avail %', 'Used %'],
                          ['postgres-0', '40G', '5G', '100G', '60G', '40G',
                           '60%', '40%'],
                          ['postgres-1', '120G', '50G', '200G', '80G', '120G',
                           '40%', '60%']], self.fsc.execute())

    @patch('pyu.log.log.error')
    @patch('pglib.ha.cluster.PostgresCluster.instances',
           new_callable=PropertyMock)
    @patch('pglib.admin.controllers.file_system_usage.Role')
    @patch('pglib.admin.controllers.file_system_usage.EnmKubeSession')
    def test_file_system_usage_when_no_instance_data(self, eks, pod, pg_inst,
                                                     elog):
        pg_inst.return_value = []
        with self.assertRaises(IndexError):
            self.fsc.execute()

    @patch('pyu.log.log.error')
    @patch('pyu.parallel.threads.ThreadPool.wait')
    @patch('pglib.ha.cluster.PostgresCluster.instances',
           new_callable=PropertyMock)
    @patch('pglib.admin.controllers.file_system_usage.Role')
    @patch('pglib.admin.controllers.file_system_usage.EnmKubeSession')
    def test_file_system_usage_when_threads_fail(self, eks, pod, pg_inst,
                                                 tpool, elog):
        from pyu.parallel.threads import ThreadPoolException
        inst1 = DummyInst('postgres-0', '40g', '5g', '100g')
        inst2 = DummyInst('postgres-1', '120g', '50g', '200g')
        pg_inst.return_value = [inst1, inst2]

        tpool.side_effect = ThreadPoolException('Thread timed out')

        with self.assertRaises(ThreadPoolException):
            self.fsc.execute()

    def test_class_attributes_are_set(self):
        self.assertEqual(self.fsc.name, 'fs_usage')
        self.assertEqual(self.fsc.title, 'Filesystem Usage')
        self.assertEqual(self.fsc.rows_border, False)


if __name__ == '__main__':
    unittest.main(verbosity=2)
