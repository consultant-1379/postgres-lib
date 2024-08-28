from pyu.os.shell.local import LocalShellClient
from pyu.ui.menuapp.controller import TabulatedController

from pglib.db.database import PgStore


class DbSizeController(TabulatedController):
    name = 'db_sizes'
    title = 'Databases Size'
    rows_border = False

    def execute(self):
        pg_store = PgStore(LocalShellClient())
        db_list = pg_store.databases

        body = [[d.id, d.name, d.size] for d in db_list]
        header = ['id', 'name', 'size']
        return [header] + body
