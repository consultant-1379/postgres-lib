from pyu.ui.menuapp.controller import TabulatedController

from pglib.admin.lib.menu_db import MenuDb


class TableSizeController(TabulatedController):
    name = 'table_size'
    title = 'Table Sizes'
    rows_border = False

    def prompt(self):
        db = MenuDb().show(size=False, sort_size=False)
        return (db,)

    def execute(self, db):
        body = [[t.table_name, t.size, t.row_count] for t in
                db.tables]
        header = ['Table Name', 'Table Size', 'Number of Rows']
        return [header] + body
