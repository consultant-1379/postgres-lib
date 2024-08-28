import time
from datetime import timedelta

from pyu.ui.menuapp.controller import PrintedController
from pyu.ui.menuapp.validation import Abort
# pylint: disable=E0611
from pyu.ui.visual.colour import Cyan, Green, Grey, Magenta, White, Yellow
from pyu.ui.visual.format.grid import Table
from pyu.ui.visual.format.shortcuts import br, span
from pyu.ui.visual.format.style import Style
from pyu.ui.visual.inputs import cancel
from pyu.ui.visual.spinner import Spinner

from pglib.admin.lib.bloat.cmds import limit_connections, vaccum, \
    reset_connections
from pglib.admin.lib.bloat.db import FsData, show_bloat_table, \
    get_total_db_bloat
from pglib.admin.lib.menu_db import MenuDb
from pglib.postgres import PsqlClient


class VacuumController(PrintedController):
    name = 'vacuuming'
    title = 'Vacuum Tool'
    note = 'This option is only to be used when advised by Ericsson support.' \
           ' This will disable all access to the database selected.'

    def prompt(self):
        db = MenuDb().show(size=True, sort_size=True)
        with Spinner('Database Filesystem Usage'):
            pre_vac = FsData(db, self.shell)
            br()
            span(White('Database: %s' % Green(pre_vac.name)))
            span(White('Database Size: %s' % pre_vac.db_size))
            span(White('Database ID: %s' % pre_vac.db_id))
            br()
            span(White('Postgres space used: %s' % pre_vac.mnt_used))
            span(White('Postgres mount size: %s' % pre_vac.mnt_size))
            span(White('Postgres %% used: %s' % pre_vac.mnt_used_perc))
            span(White('Postgres available space: %s' % pre_vac.mnt_avail))

        br()
        span(Magenta('Updating the statistics of the database. This can take '
                     'upto 1 minute per Gig.'))
        span(Grey('Please wait till completion.'))
        br()

        with Spinner('Bloat Pre-Vacuum'):
            pre_bloat = db.bloat
            pre_t_bloat = get_total_db_bloat(pre_bloat)
        br()
        span(Yellow('Total bloated rows in %s: %s' %
                    (db.name, pre_t_bloat)))
        br()
        span(Cyan('Top 5 bloated tables of %s:' % db.name))
        show_bloat_table(pre_bloat)
        br()

        question = 'This is an intrusive operations.\n Connections to the ' \
                   'Database under processing will be limited during this ' \
                   'process.\n This should only be executed when advised ' \
                   'by Ericsson Support. \n Do you wish to continue?'
        if cancel(question):
            raise Abort
        return db, pre_vac, pre_t_bloat

    def execute(self, db, pre_vac, pre_t_bloat):

        psql = PsqlClient(self.shell, database=db.name)
        start_time = time.time()

        try:
            yield Grey('  Limiting connections on %s: ' % db.name)
            yield Magenta('  Vacuuming %s.\n  This can take approx 1 minute '
                          'per Gig. Please wait till completion.' % db.name)
            limit_connections(db)
            vaccum(psql)
        finally:
            yield Grey('  Resetting connections on %s: ' % db.name)
            reset_connections(db)

        end_time = time.time()
        total_time = end_time - start_time

        post_vac = FsData(db, self.shell)
        yield ''
        yield White('  Database: %s' % Green(post_vac.name))
        yield White('  Database Size: %s' % post_vac.db_size)
        yield White('  Database ID: %s' % post_vac.db_id)
        yield ''
        yield White('  Postgres space used: %s' % post_vac.mnt_used)
        yield White('  Postgres mount size: %s' % post_vac.mnt_size)
        yield White('  Postgres %% used: %s' % post_vac.mnt_used_perc)
        yield White('  Postgres available space: %s' % post_vac.mnt_avail)
        post_bloat = db.bloat
        post_t_bloat = get_total_db_bloat(post_bloat)
        yield ''
        yield Yellow('  Bloat reduction: ') + White('Number of bloated rows')
        header = [['Pre Vac Bloated Rows', 'Post Vac Bloated Rows',
                   'Total Bloated Rows Removed']]
        body = [[pre_t_bloat, post_t_bloat, (pre_t_bloat - post_t_bloat)]]
        table = Table(header + body, cel_style=Style(White))
        yield table.str
        yield ''
        yield Yellow('  Database reduced by: %s\n' %
                     (pre_vac.db_size - post_vac.db_size))
        yield Grey('  Total Time for Vacuum Procedure on %s: %s\n' %
                   (db.name, str(timedelta(seconds=total_time))))
