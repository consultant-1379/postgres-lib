from pyu.ui.menuapp.controller import PrintedController

from pglib.env.version import PostgresVersion


class PGVersionController(PrintedController):
    name = 'pg_version'
    title = 'Postgres Version'

    def execute(self):
        self.template = '%s'
        pgv = PostgresVersion(self.shell)

        output = '  PostgreSQL Server Version:\n  ' + pgv.version
        output += '\n\n  DocumentDB Version:\n  ' + pgv.docdb_version
        output += '\n\n  PostgreSQL Data Directory:\n  ' + \
                  pgv.data_directory
        output += '\n\n  PostgreSQL Config File:\n  ' + pgv.config_file

        return output
