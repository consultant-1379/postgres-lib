import subprocess

from pyu.os.shell.local import LocalShellClient
from pyu.ui.menuapp.validation import Abort
# pylint: disable=E0611
from pyu.ui.visual.colour import Yellow, White
from pyu.ui.visual.format.grid import Grid
from pyu.ui.visual.format.shortcuts import span, br
from pyu.ui.visual.inputs import query

from pglib.db.database import PgStore


class MenuDb:
    def __init__(self):
        self.shell = LocalShellClient()
        self.store = PgStore(self.shell)

    def show(self, size=False, sort_size=False):
        if sort_size:
            dbs = sorted(self.store.databases, key=lambda d: d.size,
                         reverse=True)
        else:
            dbs = self.store.databases

        if size:
            g = Grid([[Yellow(('%s.' % str(i + 1)).rjust(6)), White(s.name),
                       s.size] for i, s in enumerate(dbs)])
        else:
            g = Grid([[Yellow(('%s.' % str(i + 1)).rjust(6)), White(s.name)]
                      for i, s in enumerate(dbs)])
        g.show()
        br()
        span('     0. Exit')
        br()
        choice = query('Please select a database or 0 to Quit: ',
                       choices=list(map(str, range(0, len(dbs) + 1))),
                       choices_display=['', ])
        db = dbs[int(choice) - 1]
        if int(choice) == 0:
            raise Abort
        subprocess.call('clear')
        return db
