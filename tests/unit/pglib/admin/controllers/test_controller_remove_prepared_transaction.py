from mock import patch, Mock
import time
import unittest2 as unittest

from pglib.postgres import PostgresClient


class TestControllerRemovePreparedTransaction(unittest.TestCase):
    def setUp(self):
        from pglib.admin.controllers.remove_prepared_transaction import PreparedTransactionController
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        self.shell = Mock()
        self.shell.os.sg.pg.credentials_class = \
            PgServiceGroupCenm.credentials_class
        credentials.setup(self.shell.os.sg.pg.credentials_class)
        self.controller = PreparedTransactionController(self.shell)

    @patch.object(PostgresClient, 'rollback_prepared_transaction')
    @patch.object(PostgresClient, 'get_prepared_transactions')
    @patch('pglib.admin.controllers.remove_prepared_transaction.EnmKubeSession')
    @patch('pglib.admin.controllers.remove_prepared_transaction.Role')
    @patch('psycopg2.connect')
    def test_remove_zero_prepared_transaction(self, conn, role, kube,
                                            get_prepared_transactions,
                                            rollback_prepared_transaction):
        get_prepared_transactions.return_value = []
        out = self.controller.execute()
        self.assertIn("No prepared transactions to be removed", next(out))
        self.assertFalse(rollback_prepared_transaction.called,
                         "rollback_prepared_transaction called by error")

    @patch.object(PostgresClient, 'rollback_prepared_transaction')
    @patch.object(PostgresClient, 'get_prepared_transactions')
    @patch('pglib.admin.controllers.remove_prepared_transaction.EnmKubeSession')
    @patch('pglib.admin.controllers.remove_prepared_transaction.Role')
    @patch('psycopg2.connect')
    def test_remove_one_prepared_transaction(self, conn, role, kube,
                                            get_prepared_transactions,
                                            rollback_prepared_transaction):
        get_prepared_transactions.return_value = [
            {
                'owner': 'postgres',
                'gid': 'foo_insert',
                'prepared': 1674580827.224359,
                'database': 'postgres'
            },
            {
                'owner': 'postgres',
                'gid': 'bar_insert',
                'prepared': time.time(),
                'database': 'postgres'
            }
        ]
        out = self.controller.execute()
        self.assertIn("Attempting to remove it", next(out))
        self.assertIn("Rolled back transaction", next(out))
        rollback_prepared_transaction.assert_called_once_with('foo_insert')

    @patch.object(PostgresClient, 'rollback_prepared_transaction')
    @patch.object(PostgresClient, 'get_prepared_transactions')
    @patch('pglib.admin.controllers.remove_prepared_transaction.EnmKubeSession')
    @patch('pglib.admin.controllers.remove_prepared_transaction.Role')
    @patch('psycopg2.connect')
    def test_no_orphaned_prepared_transaction(self, conn, role, kube, 
                                            get_prepared_transactions,
                                            rollback_prepared_transaction):
        get_prepared_transactions.return_value = [
            {
                'owner': 'postgres',
                'gid': 'foo_insert',
                'prepared': time.time(),
                'database': 'postgres'
            },
            {
                'owner': 'postgres',
                'gid': 'bar_insert',
                'prepared': time.time() - 5,
                'database': 'postgres'
            }
        ]
        out = self.controller.execute()
        self.assertIn("older than 10 seconds", next(out))

    @patch('pglib.admin.controllers.remove_prepared_transaction.EnmKubeSession')
    @patch('pglib.admin.controllers.remove_prepared_transaction.Role')
    @patch('psycopg2.connect')
    def test_check_two_phase_dir(self, conn, role, kube):
        out = self.controller.execute()
        next(out)  # discard first line of output
        self.assertIn("Prepared transactions files still exist", next(out))

    @patch('pglib.admin.controllers.remove_prepared_transaction.EnmKubeSession')
    @patch('pglib.admin.controllers.remove_prepared_transaction.Role')
    @patch('psycopg2.connect')
    def test_check_two_phase_dir_non_exist(self, conn, role, kube):
        kube.return_value.__enter__.return_value.os.fs.exists.return_value = False
        out = self.controller.execute()
        self.assertIn("No prepared transactions to be removed", next(out))
        with self.assertRaises(StopIteration):
            next(out)

    @patch('pglib.admin.controllers.remove_prepared_transaction.EnmKubeSession')
    @patch('pglib.admin.controllers.remove_prepared_transaction.Role')
    @patch('psycopg2.connect')
    def test_check_two_phase_dir_non_dir(self, conn, role, kube):
        kube.return_value.__enter__.return_value.os.fs.is_dir.return_value = False
        out = self.controller.execute()
        self.assertIn("No prepared transactions to be removed", next(out))
        with self.assertRaises(StopIteration):
            next(out)

    @patch('pglib.admin.controllers.remove_prepared_transaction.EnmKubeSession')
    @patch('pglib.admin.controllers.remove_prepared_transaction.Role')
    @patch('psycopg2.connect')
    def test_check_two_phase_dir_empty_dir(self, conn, role, kube):
        kube.return_value.__enter__.return_value.os.fs.list.return_value = []
        out = self.controller.execute()
        self.assertIn("No prepared transactions to be removed", next(out))
        with self.assertRaises(StopIteration):
            next(out)

if __name__ == '__main__':
    unittest.main()