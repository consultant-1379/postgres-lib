from pglib.postgres import PostgresSession
from pyu.ui.menuapp.validation import Abort
# pylint: disable=E0611
from pyu.ui.visual.colour import White
from pyu.ui.visual.format.grid import Table
from pyu.ui.visual.format.style import Style


def limit_connections(db):
    with PostgresSession(database=db.name) as psql:
        psql.limit_connections()


def vaccum(psql):
    status = psql.vacuumdb(full=True, analyze=True)
    if status != 0:
        raise Abort


def reindex(psql):
    status = psql.reindexdb()
    if status != 0:
        raise Abort


def reset_connections(db):
    with PostgresSession(database=db.name) as psql:
        psql.reset_connections()


def show_bloat_reduction(pre, post):
    header = [['Pre Vacuum', 'Post Vacuum', 'Total Reduction']]
    body = [[pre, post, (pre - post)]]
    table = Table(header + body, cel_style=Style(White))
    table.show()
