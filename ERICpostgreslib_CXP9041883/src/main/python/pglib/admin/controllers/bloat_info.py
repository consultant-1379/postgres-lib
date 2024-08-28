from pyu.ui.menuapp.controller import TabulatedController
# pylint: disable=E0611
from pyu.ui.visual.colour import Cyan, Green, Grey, Magenta, White, Yellow
from pyu.ui.visual.format.shortcuts import br, span
from pyu.ui.visual.spinner import Spinner

from pglib.admin.lib.bloat.db import FsData, get_bloat_table_data, \
    get_total_db_bloat
from pglib.admin.lib.menu_db import MenuDb


class BloatController(TabulatedController):
    name = 'bloat_info'
    title = 'Bloat Information'
    note = 'This option updates the statistics of a database. It may take ' \
           'approximately 1 minute per Gig.'

    def prompt(self):
        db = MenuDb().show(size=True, sort_size=True)
        db_fs = FsData(db, self.shell)
        br()
        span(White('Database: %s' % Green(db_fs.name)))
        span(White('Database Size: %s' % db_fs.db_size))
        span(White('Database ID: %s' % db_fs.db_id))
        br()
        span(White('Postgres space used: %s' % db_fs.mnt_used))
        span(White('Postgres mount size: %s' % db_fs.mnt_size))
        span(White('Postgres %% used: %s' % db_fs.mnt_used_perc))
        span(White('Postgres available space: %s' % db_fs.mnt_avail))
        br()
        span(Magenta('Updating the statistics of the database. This can take '
                     'upto 1 minute per Gig.'))
        span(Grey('Please wait till completion.'))
        br()
        with Spinner('Retrieving bloat information'):
            bloat = db.bloat
            t_bloat = get_total_db_bloat(bloat)
            br()
            span(Yellow('Total bloated rows in %s: %s' % (db.name, t_bloat)))
            br()
            span(Cyan('Top 5 bloated tables of %s:' % db.name))
        return (bloat,)

    def execute(self, data):
        return get_bloat_table_data(data)
