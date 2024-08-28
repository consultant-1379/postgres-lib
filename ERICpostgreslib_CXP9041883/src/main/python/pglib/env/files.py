from pyu.os.fs.filesystem import File


class PgFiles(object):

    def __init__(self, shell):
        consts = shell.os.sg.pg.consts
        self.pg_mount = File(shell, consts.pg_mount)
        self.pg_data_dir = File(shell, consts.pg_data_dir)
        self.pg_bin = File(shell, consts.pg_bin)
        self.pg_wal_dir = File(shell, consts.pg_wal_dir)
        self.psql = File(shell, consts.psql)
        self.pg_isready = File(shell, consts.pg_isready)
        self.pg_two_phase_dir = File(shell, consts.pg_two_phase_dir)
