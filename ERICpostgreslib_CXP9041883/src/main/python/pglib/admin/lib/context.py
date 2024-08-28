from pyu.ui.context import context_property_set
from pyu.ui.menuapp.ui.context import MenuAppGlobalContext


class SimpleGlobalContext(MenuAppGlobalContext):

    @context_property_set
    def verbose(self, verbose):
        return verbose


context = SimpleGlobalContext()
