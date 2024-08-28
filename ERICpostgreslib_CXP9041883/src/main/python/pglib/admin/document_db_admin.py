import sys

from pyu.error import log_internal_error
from pyu.log import log
from pyu.os.shell.local import LocalShellClient
from pyu.ui.menuapp.main import MenuAppMain

from pglib.admin.lib.cli import MenuAppCli
from pglib.admin.lib.context import context
from pglib.admin.lib.ui import MenuAppUi
from pglib.errors import InvalidDeploymentType


def main():
    log.setup_syslog('DocDB_Admin', verbose=True)
    local_shell = LocalShellClient()
    if local_shell.os.env.type != 'cENM':
        msg = 'document_db_admin is only to be executed on cloud native ' \
              'deployments (cENM).\nFor pENM/vENM please execute:: ' \
              '/opt/ericsson/pgsql/util/postgres_admin.sh'
        log.error(msg, stdout=True)
        raise InvalidDeploymentType(msg)

    menu_app_main = MenuAppMain(local_shell)
    exit_code = menu_app_main.run(context, MenuAppCli, MenuAppUi)
    return exit_code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:  # pylint: disable=W0703
        # logs a traceback in case script unexpectedly fail
        log_internal_error(stdout=True)
        sys.exit(1)
