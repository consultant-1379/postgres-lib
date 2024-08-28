from pyu.log import log
from pyu.os.shell.errors import CommandFailed

from pglib.env.credentials import credentials
from pglib.errors import InvalidDeploymentType, PsqlSessionException
from pglib.postgres import PostgresSession

INVALID_DEPLOYMENT_MSG = 'DocDB version is only applicable for cENM ' \
                         'deployments'


class PostgresVersion(object):

    def __init__(self, shell, credential=credentials.postgres):
        self.shell = shell
        self.credential = credential
        credentials.setup(self.shell.os.sg.pg.credentials_class)

    @property
    def version(self):
        with PostgresSession() as psql:
            try:
                query = 'SELECT version();'
                version = psql.fetchone(query)
                return str(version[0])
            except PsqlSessionException as err:
                log.error('Postgres session exception: %s' %
                          err, stdout=True)
                raise

    @property
    def config_file(self):
        with PostgresSession() as psql:
            try:
                query = 'show config_file;'
                config_file = psql.fetchone(query)
                return str(config_file[0])
            except PsqlSessionException as err:
                log.error('Postgres session exception: %s' %
                          err, stdout=True)
                raise

    @property
    def data_directory(self):
        with PostgresSession() as psql:
            try:
                query = 'show data_directory;'
                data_directory = psql.fetchone(query)
                return str(data_directory[0])
            except PsqlSessionException as err:
                log.error('Postgres session exception: %s' %
                          err, stdout=True)
                raise

    @property
    def docdb_version(self):
        try:
            if self.shell.os.env.type != 'cENM':
                log.error(INVALID_DEPLOYMENT_MSG, stdout=True)
                raise InvalidDeploymentType(INVALID_DEPLOYMENT_MSG)
            cmd = r"kubectl get pods --selector=app=postgres -o jsonpath=" \
                  r"'{.items[*].metadata.labels.app\.kubernetes\." \
                  r"io/version}' | xargs -n 1 | uniq"
            return self.shell.rune(cmd).strip().replace("_", "-")
        except CommandFailed as err:
            log.error(err.msg, stdout=True)
            raise
