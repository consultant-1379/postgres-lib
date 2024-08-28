from unittest.mock import Mock, patch

import unittest2 as unittest

from pyu.os.shell.local import LocalShellClient
from pyu.ui.cli import GlobalArg
from pyu.ui.menuapp.ui.cli import MenuAppCliBase

VERBOSE = GlobalArg('verbose', 'Show stuff verbosely', atype=bool)


class TestCli(unittest.TestCase):

    @patch('pglib.db.database.PgStore')
    @patch('pyu.os.system.OperatingSystem.env')
    def setUp(self, env, pgstore):
        from pglib.admin.lib.cli import MenuAppCli
        from pglib.env import PgServiceGroupCenm
        from pglib.env.credentials import credentials
        self.shell = Mock()
        self.shell.os.sg.pg.credentials_class = \
            PgServiceGroupCenm.credentials_class
        credentials.setup(self.shell.os.sg.pg.credentials_class)
        self.cli = MenuAppCli

    def test_menu_app_cli_class_variable_description(self):
        self.assertEqual(self.cli.description,
                         'Document DB - ADMIN TOOL\ncENM')

    def test_menu_app_cli_class_variable_general_arguments(self):
        expected = MenuAppCliBase.general_arguments + [VERBOSE]
        self.assertEqual(type(self.cli.general_arguments), type(expected))

    def test_menu_app_cli_class_variable_display_header(self):
        self.assertEqual(self.cli.display_header, True)

    def test_menu_app_cli_class_variable_static_menu(self):
        from pglib.admin.lib.menu import MENU_ITEMS
        self.assertEqual(self.cli.static_menu, MENU_ITEMS)

    def test_menu_app_cli_base_class_variable_allow_main(self):
        self.assertEqual(self.cli.allow_main, True)

    def test_menu_app_cli_base_class_variable_shell_class(self):
        self.assertEqual(self.cli.shell_class, LocalShellClient)

    def test_menu_app_cli_base_class_variable_valid_host_choices(self):
        self.assertEqual(self.cli.valid_host_choices, [])

    def test_menu_app_cli_base_get_static_menu(self):
        from pglib.admin.lib.menu import MENU_ITEMS
        self.cli.get_static_menu(self.shell)
        expected = MENU_ITEMS.title
        actual = str(self.cli.get_static_menu(self.shell))
        print(self.cli.get_static_menu(self.shell),
              type(self.cli.get_static_menu(self.shell)))
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
