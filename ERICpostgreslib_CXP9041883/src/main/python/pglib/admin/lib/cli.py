from six import with_metaclass

from pglib.admin.lib.menu import MENU_ITEMS

from pyu.ui.cli import GlobalArg
from pyu.ui.menuapp.ui.cli import MenuAppCliBase
from pyu.ui.menuapp.ui.meta import AutomaticCliMetaBase

VERBOSE = GlobalArg('verbose', 'Show stuff verbosely', atype=bool)


# pylint: disable=W0223
class MenuAppCli(with_metaclass(AutomaticCliMetaBase, MenuAppCliBase)):
    description = "Document DB - ADMIN TOOL\ncENM"
    general_arguments = MenuAppCliBase.general_arguments + [VERBOSE]
    display_header = True

    static_menu = MENU_ITEMS
