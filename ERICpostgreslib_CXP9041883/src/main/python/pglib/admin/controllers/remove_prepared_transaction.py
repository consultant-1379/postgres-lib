from pyu.enm.kube import EnmKubeSession
from pyu.os.shell.local import LocalShellClient
from pyu.ui.menuapp.controller import PrintedController
from pyu.ui.menuapp.validation import Abort
# pylint: disable=E0611
from pyu.ui.visual.colour import Red, Grey
from pyu.ui.visual.inputs import cancel

from pglib.db.prepared_transaction import PreparedTransaction
from pglib.env.cenm.consts import PgConstantsCenm
from pglib.ha.pod import Role
from pglib.postgres import PostgresSession

SECONDS_CHECK = 10


def check_two_phase_dir():
    role = Role(LocalShellClient())
    session = EnmKubeSession(pod=role.leader, container='postgres')
    with session as shell:
        const = PgConstantsCenm(shell)
        twophase_dir = const.pg_two_phase_dir
        if shell.os.fs.exists(twophase_dir) and \
            shell.os.fs.is_dir(twophase_dir) and \
            shell.os.fs.list(twophase_dir):
            msg = "  Prepared transactions files still exist: \n"
            remaining_txn = shell.os.fs.list(twophase_dir)
            for i in remaining_txn:
                msg += str(i) + '\n'
            yield Red(msg)


def remove_prepared_transactions():
    with PostgresSession() as client:
        pp_transactions = client.get_prepared_transactions()
        if len(pp_transactions) == 0:
            yield Grey('  No prepared transactions to be removed.')
            return

    is_transaction_found = False
    for txn in pp_transactions:
        pp_tx = PreparedTransaction(**txn)
        if pp_tx.is_older_than_seconds(SECONDS_CHECK):
            is_transaction_found = True
            yield Grey('  Transaction %s is older than %s seconds. Attempting '
                       'to remove it.' % (pp_tx, SECONDS_CHECK))
            with PostgresSession(database=pp_tx.database) as client:
                client.rollback_prepared_transaction(pp_tx.gid)
                yield Grey('  Rolled back transaction: %s' % pp_tx)
    if not is_transaction_found:
        yield Grey('  No prepared transactions older than 10 seconds, '
                   'nothing to be done.')


class PreparedTransactionController(PrintedController):
    name = 'prepared_transactions'
    title = 'Remove Prepared Transactions'
    note = 'This option is only to be used when advised by Ericsson support.'

    def prompt(self):
        question = ' This will remove all 2-phase commit transactions ' \
                   'that are created more than %s seconds ago. ' \
                   'Do you wish to continue?' % SECONDS_CHECK
        if cancel(question):
            raise Abort
        return []  # Must return an iterable here

    def execute(self):
        yield from remove_prepared_transactions()
        yield from check_two_phase_dir()
