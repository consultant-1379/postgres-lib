import unittest
from unittest.mock import Mock, patch

from pglib.admin.controllers.cluster_overview import ClusterOverviewController
from pglib.admin.controllers.db_sizes import DbSizeController
from pglib.admin.controllers.file_system_usage import FileSystemUsageController
from pglib.admin.controllers.replication_lag import ReplicationLagController
from pglib.admin.controllers.remove_prepared_transaction import \
    PreparedTransactionController
from pglib.db.database import DatabaseInstance

from pyu.os.fs.units import Size
from pyu.ui.menuapp.menu import MenuItem


class TestMenu(unittest.TestCase):

    def setUp(self):
        self.shell = Mock()
        self.menu_items = MenuItem(title='Main Menu', children=[
            MenuItem(DbSizeController, shell=self.shell),
            MenuItem(FileSystemUsageController, shell=self.shell),
            MenuItem(ClusterOverviewController, shell=self.shell),
            MenuItem(ReplicationLagController, shell=self.shell),
            MenuItem(PreparedTransactionController, shell=self.shell),
        ])

    def tearDown(self):
        self.menu_items = None

    @patch('pglib.db.database.PgStore')
    def test_menu_items(self, pgstore):
        from pglib.admin.lib.menu import MENU_ITEMS
        pgstore.return_value.databases = [
            DatabaseInstance(name='flowautomationdb', id='456',
                             size=Size('1024M'))]
        self.assertEqual(type(MENU_ITEMS), type(self.menu_items))

    def test_menu_items_title(self):
        self.assertEqual(self.menu_items.title, 'Main Menu')

    def test_menu_items_title_using_controller(self):
        menu = MenuItem(DbSizeController)
        self.assertEqual(menu.title, 'Databases Size')

    def test_menu_items_leaves(self):
        actual = self.menu_items.leaves
        self.assertEqual(len(actual), 5)

    def test_menu_items_all_children(self):
        actual = self.menu_items.all_children

        self.assertEqual(len(actual), 5)

    def test_menu_items_children(self):
        actual = self.menu_items.children
        self.assertEqual(len(actual), 5)

    def test_menu_items_get_child(self):
        actual = self.menu_items.get_child(0)
        self.assertEqual(actual.title, 'Remove Prepared Transactions')

    def test_menu_items_children_none(self):
        actual = MenuItem(title='Main Menu', children=[
            MenuItem(DbSizeController),
            MenuItem(FileSystemUsageController),
            MenuItem(ClusterOverviewController),
            MenuItem(ReplicationLagController),
            MenuItem(PreparedTransactionController),
        ]).children
        self.assertEqual(actual, [])

    def test_menu_items_get_child_raises_index_error(self):
        actual = MenuItem(title='Main Menu', children=[
            MenuItem(DbSizeController),
            MenuItem(FileSystemUsageController),
            MenuItem(ClusterOverviewController),
            MenuItem(ReplicationLagController),
            MenuItem(PreparedTransactionController),
        ])
        with self.assertRaises(MenuItem.DoesNotExist):
            actual.get_child(0)


if __name__ == '__main__':
    unittest.main()
