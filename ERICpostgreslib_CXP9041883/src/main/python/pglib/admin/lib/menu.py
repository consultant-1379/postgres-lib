from pyu.os.shell.local import LocalShellClient
from pyu.ui.menuapp.menu import MenuItem

from pglib.admin.controllers.bloat_info import BloatController
from pglib.admin.controllers.cluster_overview import ClusterOverviewController
from pglib.admin.controllers.db_sizes import DbSizeController
from pglib.admin.controllers.file_system_usage import FileSystemUsageController
from pglib.admin.controllers.pg_version import PGVersionController
from pglib.admin.controllers.replication_lag import ReplicationLagController
from pglib.admin.controllers.table_size import TableSizeController
from pglib.admin.controllers.uptime import UptimeController
from pglib.admin.controllers.vacuum import VacuumController
from pglib.admin.controllers.remove_prepared_transaction import \
    PreparedTransactionController
from pglib.db.database import PgStore

pg_store = PgStore(LocalShellClient())

MENU_ITEMS = MenuItem(title='Main Menu', children=[
    MenuItem(PGVersionController),
    MenuItem(UptimeController),
    MenuItem(DbSizeController),
    MenuItem(FileSystemUsageController),
    MenuItem(ClusterOverviewController),
    MenuItem(ReplicationLagController),
    MenuItem(TableSizeController),
    MenuItem(BloatController),
    MenuItem(VacuumController),
    MenuItem(PreparedTransactionController),
])
