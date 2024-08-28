from pyu.os.fs.units import Size

from pglib.env.credentials import credentials
from pglib.postgres import PostgresSession
from pglib.postgres import PsqlClient


class PgStore(object):

    def __init__(self, shell):
        self.shell = shell
        credentials.setup(self.shell.os.sg.pg.credentials_class)
        self.psql = PsqlClient(shell)

    def _get_databases_data(self):
        """
        Fetching names and ids of Postgres managed databases
        :return: list
        """
        query = 'SELECT oid AS id, datname AS name, ' \
                'pg_database_size(datname) AS size FROM pg_database ' \
                'WHERE datistemplate = false ORDER BY name;'

        out = self.psql.run(query)
        if not out:
            return []

        # pylint: disable=R1721
        lines = [line for line in out.split('\n')]
        body = list(line.split('|') for line in lines[:-2])
        headers = body.pop(0)
        items = [dict(zip(headers, sublist)) for sublist in body]
        return dict([(d['id'], d) for d in items])

    @property
    def databases(self):
        dbs = self._get_databases_data()
        if not dbs:
            return []
        for key in dbs:
            dbs[key]['size'] = Size(dbs[key]['size'])
        return [DatabaseInstance(**db) for db in dbs.values()]


class DatabaseInstance(object):
    def __init__(self, name, id, size=None):
        self._name = name
        self._id = id
        self._size = size

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def size(self):
        return self._size

    def _tables_data(self):
        qry = 'SELECT Table_Name, size, ' \
              '(xpath(\'/row/cnt/text()\', xml_count))' \
              '[1]::text::int as Row_Count ' \
              'FROM( SELECT relname as Table_Name,' \
              'pg_total_relation_size(relid) as size, schemaname, ' \
              'query_to_xml(format(\'select count(*) as cnt from %s.%s\', ' \
              'schemaname, relname), false, true, \'\') as xml_count ' \
              'FROM pg_catalog.pg_statio_user_tables ) t ' \
              'ORDER BY size DESC ' \
              'LIMIT 20; '

        with PostgresSession(database=self.name) as session:
            output = session.fetchall(qry)

        return output

    @property
    def tables(self):
        tables = self._tables_data()
        if not tables:
            return []
        return [Table(*table) for table in tables]

    def _bloat_data(self):
        qry = 'SELECT pg_stat_user_tables.relname AS table, ' \
              'pg_stat_user_tables.n_live_tup AS rowcount, ' \
              'pg_stat_user_tables.n_tup_ins AS inserts, ' \
              'pg_stat_user_tables.n_tup_upd AS updates, ' \
              'pg_stat_user_tables.n_tup_del AS deletes, ' \
              'pg_stat_user_tables.n_dead_tup AS bloat, ' \
              'pg_stat_user_tables.autovacuum_count, ' \
              'pg_stat_user_tables.last_autovacuum, ' \
              'pg_stat_user_tables.analyze_count, ' \
              'pg_stat_user_tables.last_autoanalyze ' \
              'FROM pg_stat_user_tables ' \
              'INNER JOIN pg_class ' \
              'ON pg_stat_user_tables.relname = pg_class.relname ' \
              'ORDER BY pg_stat_user_tables.n_dead_tup DESC;'

        with PostgresSession(database=self.name) as session:
            session.run('ANALYZE;')
            output = session.fetchall(qry)

        return output

    @property
    def bloat(self):
        bloat_data = self._bloat_data()
        if not bloat_data:
            return []
        return [Bloat(*bloat) for bloat in bloat_data]

    def __repr__(self):
        return "DB: %s | ID: %s | Size: %s" % (self.name, self.id, self.size)

    def __str__(self):
        return '%s | %s' % (self.name, self.size)


class Table(object):
    def __init__(self, table_name, size=None, row_count=None):
        self._table_name = table_name
        self._size = size
        self._row_count = row_count

    @property
    def table_name(self):
        return self._table_name

    @property
    def size(self):
        return Size(self._size)

    @property
    def row_count(self):
        return self._row_count

    def __repr__(self):
        return "Table: %s | Size: %s | Rows: %s" % (
            self.table_name, self.size, self.row_count)


class Bloat(object):
    def __init__(self, tname, rows, ins, upd, dels, bloat, ac, lavac, analc,
                 lanal):
        self._table = tname
        self._rows = rows
        self._inserts = ins
        self._updates = upd
        self._deletes = dels
        self._bloat = bloat
        self._autovac = ac
        self._last_autovac = lavac
        self._analayze = analc
        self._last_autoanalayze = lanal

    @property
    def table(self):
        return self._table

    @property
    def rows(self):
        return self._rows

    @property
    def inserts(self):
        return self._inserts

    @property
    def updates(self):
        return self._updates

    @property
    def deletes(self):
        return self._deletes

    @property
    def bloat(self):
        return self._bloat

    @property
    def autovac(self):
        return self._autovac

    @property
    def last_autovac(self):
        return self._last_autovac

    @property
    def analayze(self):
        return self._analayze

    @property
    def last_autoanalayze(self):
        return self._last_autoanalayze
