from six import with_metaclass

from pglib.admin.lib.cli import MenuAppCli

from pyu.ui.menuapp.ui.base import MenuAppUiBase
from pyu.ui.menuapp.ui.meta import MenuAppUiMeta


class MenuAppUi(with_metaclass(MenuAppUiMeta, MenuAppUiBase)):
    cli_class = MenuAppCli
