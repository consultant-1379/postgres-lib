import re

from pyu.enm.kube import EnmKubeSession
from pyu.log import log
from pyu.os.shell.errors import CommandFailed
from pyu.os.shell.local import LocalShellClient
# pylint: disable=E0611
from pyu.ui.visual.colour import Yellow, Green, Blue, Grey
from pyu.ui.visual.format.grid import Table
from pyu.ui.visual.format.shortcuts import box, br, span
from pyu.ui.visual.spinner import Spinner

from pglib.db.database import PgStore
from pglib.env.credentials import credentials
from pglib.ha.cluster import PostgresCluster
from pglib.ha.pod import Role
from pglib.postgres import PsqlClient, PostgresSession


def main():
    shell = LocalShellClient()
    # Very important to setup the logger in all main scripts
    log.setup_syslog('pglib_demo', verbose=True)
    credentials.setup(shell.os.sg.pg.credentials_class)
    demo_pgstore(shell)

    demo_local_psql_client(shell)

    demo_local_psycopg_psql_session(shell)

    demo_shell_client(shell)

    demo_credentials(shell)

    demo_enm_kube_session()

    demo_wal_recovery()


def demo_pgstore(shell):
    store = PgStore(shell)
    span(Blue('Databases: %s' % store.databases))


def demo_local_psql_client(shell):
    box('Get a Local PSQL connection on Troubleshooting POD')
    span(Yellow("psql = PsqlClient(LocalShellClient(), credentials.postgres)"
                "\nrs = psql.run('SELECT 1', headers=False)"))
    psql = PsqlClient(LocalShellClient(), credentials.postgres)
    rs = psql.run('SELECT 1', headers=False)
    log.debug('result: %s' % rs, stdout=True)
    span(Green('Connect to a Database flsdb'))
    span(Blue("psql2 = PsqlClient(LocalShellClient(), database='flsdb')\n "
              "query = 'SELECT filename FROM databasechangelog ORDER BY "
              "filename DESC LIMIT 1;'\nrs2 = psql2.run(query, headers=True)"))
    psql2 = PsqlClient(shell, database='flsdb')
    query = 'SELECT filename FROM databasechangelog ORDER BY filename ' \
            'DESC LIMIT 1;'
    rs2 = psql2.run(query, headers=True)
    log.debug('result with header: \n%s' % rs2, stdout=True)
    rs3 = psql2.runq(query)
    log.debug('result without headers: \n%s' % rs3, stdout=True)


def demo_local_psycopg_psql_session(shell):
    box('Postgres Session - Pysycopg2 - on Troubleshooting Pod')
    span(Grey('Ensure credentials are setup:'
              '\ncredentials.setup(shell.os.sg.pg.credentials_class)'))
    # P0stgreSQL11
    with PostgresSession(credential=('postgres', 'P0stgreSQL11'),
                         database='flsdb') as psql:
        query = 'SELECT filename FROM databasechangelog LIMIT 5;'
        span(Green('Query Executed %s: ' % query))
        rs = psql.fetchone(query)
        log.debug('Fetchone: %s\n' % rs, stdout=True)
        rs2 = psql.fetchall(query)
        log.debug('Fetchall: %s\n' % rs2, stdout=True)

    span(Yellow("Connect as a different user: \nwith PostgresSession"
                "(credential=('fls', 'fls123'), shell=shell, database='flsdb')"
                " as psql:"))
    with PostgresSession(credential=('fls', 'fls123'),
                         database='flsdb') as psql:
        query = 'SELECT COUNT(*) FROM databasechangelog;'
        span(Green('Query Executed %s: ' % query))
        rs = psql.fetchone(query)
        log.debug('Fetchone as fls user: %s\n' % rs, stdout=True)

    with PostgresSession(database='flowautomationdb') as psql:
        query = 'SELECT pg_stat_user_tables.relname AS table, pg_stat_user_tables.n_live_tup AS rowcount, pg_stat_user_tables.n_tup_ins AS inserts, pg_stat_user_tables.n_tup_upd AS updates, pg_stat_user_tables.n_tup_del AS deletes, pg_stat_user_tables.n_dead_tup AS bloat, pg_stat_user_tables.autovacuum_count, pg_stat_user_tables.last_autovacuum, pg_stat_user_tables.analyze_count, pg_stat_user_tables.last_autoanalyze FROM pg_stat_user_tables INNER JOIN pg_class ON pg_stat_user_tables.relname = pg_class.relname ORDER BY pg_stat_user_tables.n_dead_tup DESC LIMIT 2;'
        span(Green('Query Executed %s: ' % query))
        rs = psql.fetchall(query)
        log.debug('****** Bloat \n%s\n' % rs, stdout=True)

    span(Yellow("In order to obtain the credential password/user we have to "
                "instantiate the credentials with a Local shell client\nwith "
                "PostgresSession(credential=credentials(shell).postgres, "
                "shell=shell, database='flsdb') as psql:"))
    with PostgresSession(database='flsdb') as psql:
        query = 'SELECT oid AS id, datname AS name, ' \
                'pg_database_size(datname) AS size FROM pg_database ' \
                'WHERE datistemplate = false ORDER BY name;'
        span(Green('Query Executed %s: ' % query))
        rs = psql.fetchall(query)
        log.debug('Result Set: %s\n' % rs, stdout=True)

        span(Green('Get all dbs: => psql.get_dbs()'))
        rs = psql.get_dbs()
        log.debug('psql.get_dbs(): %s\n' % rs, stdout=True)

        span(Green('Get all dbs: => psql.get_dbs(ignore_dbs=["template0", '
                   '"template1", "postgres"])'))
        rs = psql.get_dbs(ignore_dbs=['template0', 'template1', 'postgres'])
        log.debug('psql.get_dbs(): %s\n' % rs, stdout=True)

        query2 = 'SELECT version();'
        span(Green('Version - fetchone: => SELECT version();'))
        rs = psql.fetchone(query2)
        log.debug('Version:\n %s' % rs, stdout=True)
        log.debug(repr(rs), stdout=True)
        log.debug(str(rs[0]), stdout=True)

        query3 = 'show config_file;'
        span(Green('Config File - fetchone: => %s;' % query3))
        rs = psql.fetchone(query3)
        log.debug('Conf file:\n %s' % rs, stdout=True)
        log.debug(repr(rs), stdout=True)
        log.debug(str(rs[0]), stdout=True)

        query4 = 'show data_directory;'
        span(Green('Data Dir - fetchone: => %s;' % query4))
        rs = psql.fetchone(query4)
        log.debug('Data Dir:\n %s' % rs, stdout=True)
        log.debug(repr(rs), stdout=True)
        log.debug(str(rs[0]), stdout=True)


def demo_shell_client(shell):
    box('Shell Demo')
    span(Yellow("Shell Environment => shell.os.env.type"))
    log.debug('Deployment Environment: %s' % shell.os.env.type,
              stdout=True)
    span(Yellow("Does a file exist => shell.os.fs.exists('/var/tmp')"))
    log.debug('Does /var/tmp exist: %s ' % shell.os.fs.exists('/var/tmp'),
              stdout=True)
    span(Yellow("is a dir? => shell.os.fs.is_dir('/var/tmp/test1')"))
    log.debug('is /var/tmp/test1 a dir: %s ' %
              shell.os.fs.is_dir('/var/tmp/test1'), stdout=True)
    span(Yellow("make a dir => shell.os.fs.make_dirs('/var/tmp/test1')"))
    shell.os.fs.make_dirs('/var/tmp/test1')
    span(Yellow("is a dir? => shell.os.fs.is_dir('/var/tmp/test1')"))
    log.debug('is /var/tmp/test1 a dir: %s ' %
              shell.os.fs.is_dir('/var/tmp/test1'), stdout=True)
    span(Yellow("Remove a dir => shell.os.fs.remove_dir('/var/tmp/test1')"))
    shell.os.fs.remove_dir('/var/tmp/test1')
    span(Yellow("is a dir? => shell.os.fs.is_dir('/var/tmp/test1')"))
    log.debug('is /var/tmp/test1 a dir: %s ' %
              shell.os.fs.is_dir('/var/tmp/test1'), stdout=True)
    span(Yellow("Get the Size => shell.os.fs.get('/var/tmp/').size"))
    log.debug('Size of /var/tmp/ dir: %s ' %
              shell.os.fs.get('/var/tmp/').size, stdout=True)
    span(Blue("\nHeaps more functionality - check "
              "ERICdbpyu_CXP9039964/src/pyu/os/fs/filesystem.py"))

    span(Yellow("Doc DB Version => kubectl get pod"))
    cmd = r"kubectl get pods --selector=app=postgres -o jsonpath=" \
          r"'{.items[*].metadata.labels.app\.kubernetes\.io/version}'" \
          r"| xargs -n 1 | uniq"
    span(Grey('Running Command: \n%s' % cmd))
    docdb_v = shell.rune(cmd).replace("_", "-")
    log.debug(docdb_v, stdout=True)
    log.debug(repr(docdb_v), stdout=True)


def demo_credentials(shell):
    box('Credentials')
    span(Yellow("shell.os.sg.pg.credentials_class"))
    log.debug('Service Group Credentials - Deployment agnostic %s' %
              shell.os.sg.pg.credentials_class, stdout=True)
    span(Yellow("Setup the Credentials => credentials."
                "setup(shell.os.sg.pg.credentials_class)"))
    credentials.setup(shell.os.sg.pg.credentials_class)
    span(Yellow("credential = credentials.postgres\ncreds = credential("
                "LocalShellClient())\n - use the localshell of "
                "troubleshooting pod"))
    credential = credentials.postgres
    creds = credential(LocalShellClient())
    span(Blue('unpack creds tuple => user, password = creds'))
    user, password = creds
    log.debug('Postgres user: %s & password %s' % (user, password),
              stdout=True)


def demo_enm_kube_session():
    box('Cluster Information')
    role = Role(LocalShellClient())
    session = EnmKubeSession(pod=role.available, container='postgres')
    with session as shell:
        log.debug('Use an EnmKubeSession to exec onto a Postgres Pod')
        span(Green("session = EnmKubeSession(pod='postgres-0', "
                   "container='postgres'"))
        span(Green("with session as shell:"))
        span(Yellow("\tcluster = PostgresCluster()"))

        cluster = PostgresCluster(shell)
        log.debug('Cluster Overview: %s' % cluster.overview, stdout=True)
        span(Yellow("cluster.leader.pod"))
        log.debug('Leader Pod name: %s ' % cluster.leader.pod, stdout=True)
        span(Yellow("cluster.replica.pod"))
        try:
            log.debug('Replica Pod name: %s ' % cluster.replica.pod,
                      stdout=True)
        except AttributeError as err:
            log.error("Replica Pod does not exist. Try 'Sync Standby'",
                      stdout=True)
        span(Yellow("cluster.syncstandby.pod"))
        log.debug('Sync Standby Pod name: %s ' % cluster.syncstandby.pod,
                  stdout=True)
        span(Yellow("cluster.followers - List of non leader"))
        log.debug('Followers list: %s ' % cluster.followers, stdout=True)

        box('Postgres Service Group')
        span(Yellow("shell.os.sg.pg"))
        log.debug('Service Group %s' % shell.os.sg.pg, stdout=True)

        span(Yellow("Postgres SG Members => shell.os.sg.pg.members"))
        log.debug('Postgres SG Members %s' % shell.os.sg.pg.members,
                  stdout=True)

        span(Yellow("Postgres Constants: shell.os.sg.pg.consts"))
        log.debug('Postgres Host (deployment agnostic): %s' %
                  shell.os.sg.pg.consts.pg_host, stdout=True)
        log.debug('Postgres Bin (deployment agnostic): %s' %
                  shell.os.sg.pg.consts.pg_bin, stdout=True)
        log.debug('Postgres Mount (deployment agnostic): %s' %
                  shell.os.sg.pg.consts.pg_mount, stdout=True)

        span(Yellow("Postgres Files: shell.os.sg.pg.files.pg_data_dir.size"))
        log.debug('Postgres Data Dir sizes: %s'
                  % shell.os.sg.pg.files.pg_data_dir.size,
                  stdout=True)


def demo_wal_recovery():
    span(Yellow("Postgres WAL Info"))
    role = Role(LocalShellClient())
    session = EnmKubeSession(pod=role.leader, container='postgres')
    with session as shell:
        credentials.setup(shell.os.sg.pg.credentials_class)
        cluster = PostgresCluster(shell)

        box('Step #1 - Display Cluster - Tabulated')
        tabulate_cluster(cluster)
        box('Step #2 - Display Leader Filesystem Usage')
        tabulate_fsusage(cluster.leader)
        box('Step #3 - Get Redo Wal File')
        wal_file = get_redo_wal_file(cluster.leader, shell)
        if wal_file:
            span(Yellow('Latest checkpoint\'s REDO WAL file: %s' % wal_file))
        else:
            raise RedoWalFileRetrievalFailure('Unable to match Latest '
                                              'checkpoint\'s REDO WAL file')
        box('Step #4 - Executing pg_archivecleanup')
        wal_removal(cluster.leader, wal_file, shell)
        box('Step #5 - Display Leader Filesystem Usage')
        tabulate_fsusage(cluster.leader)
        box('Step #6 - Display Cluster')
        tabulate_cluster(cluster)


class NoLeaderInCluster(Exception):
    pass


class RedoWalFileRetrievalFailure(Exception):
    pass


class PostgresClusterExec(Exception):
    pass


def get_leader_pod():
    role = Role(LocalShellClient())
    session = EnmKubeSession(pod=role.available, container='postgres')
    with session as shell:
        cluster = PostgresCluster(shell)
        if not cluster.leader:
            raise NoLeaderInCluster('Leader node not available.\nThis '
                                    'procedure needs to interact with the '
                                    'leader node.')
        return cluster.leader.pod


def tabulate_fsusage(node):
    header = ['Role', 'Pod', 'Wal Dir', 'Mnt Size', 'WAL % of Mnt',
              'Mnt Used %', 'Mnt Avail %', 'Data Dir']
    body = []
    with Spinner("Getting Leader WAL Filesystem Usage", show_time=True):
        wal_perc = (node.pg_wal_dir.size.num_bytes
                    / node.pg_mount.size.num_bytes) * 100

        body.append([node.role, node.pod, str(node.pg_wal_dir.size),
                     str(node.pg_mount.size), "%.2f%%" % wal_perc,
                     node.pg_mount.used_perc, node.pg_mount.available_perc,
                     str(node.pg_data_dir.size)])
    br()
    span(Yellow("Leader WAL status:"))
    table = Table(rows=[header] + body)
    table.show()
    br()


def get_redo_wal_file(node, shell):
    redo_wal_regex = re.compile(
        r'(Latest\scheckpoint\'s\sREDO\s+WAL\s+file:\s+)([0-9a-fA-F]*)')
    try:
        cmd = '%s/pg_controldata -D %s' % (shell.os.sg.pg.consts.pg_bin,
                                           node.pg_data_dir.path)
        span(Grey('Running %s on %s pod.' % (cmd, node.pod)))
        out = shell.rune(cmd)
    except CommandFailed:
        log.error('Failed to get the Latest checkpoint\'s REDO WAL '
                  'file', stdout=True)
        raise
    wal_search = redo_wal_regex.search(str(out))
    if wal_search:
        wal_file = wal_search.group(2)
        return wal_file


def wal_removal(node, wal, shell):
    try:
        cmd = '%s/pg_archivecleanup %s %s' % (shell.os.sg.pg.consts.pg_bin,
                                              node.pg_wal_dir.path, wal)
        span(Grey('Running %s on %s pod.' % (cmd, node.pod)))
        log.info('This is the command that would be executed: \n'
                 'shell.rune(%s)\nThis has not be executed as it is a '
                 'demo and we do not want to affect the environment.\n'
                 'Patroni reinit would be required on the follower '
                 'Postgres Nodes.\nThis has not been implemented.' %
                 cmd, stdout=True)
        # shell.rune(cmd)
        span(Yellow('Successfully executed pg_archivecleanup on %s pod.'
                    % (node.pod)))
    except CommandFailed:
        log.error('Failed to run pg_archivecleanup on %s.' % node.pod,
                  stdout=True)
        raise


def tabulate_cluster(cluster):
    try:
        overview = cluster.overview
        header = list(overview[0].keys())
        body = [list(i.values()) for i in overview]
        span(Yellow("Cluster Overview:"))
        table = Table(rows=[header] + body)
        table.show()

    except Exception as error:
        raise PostgresClusterExec(error)


if __name__ == '__main__':
    main()
