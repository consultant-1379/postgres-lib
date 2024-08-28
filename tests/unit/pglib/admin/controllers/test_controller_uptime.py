import unittest2 as unittest
from mock import patch, Mock

from pglib.admin.controllers.uptime import UptimeController
from pglib.errors import PsqlAuthenticationFailure

EXPECTED = [['PostgreSQL instance', 'Start-Time', 'Total Up-Time'],
            ['postgres-0', '2021-08-19 03:15:54+01', '04:12:58'],
            ['postgres-1', '2021-08-19 03:04:50+01', '04:24:02']]

EXCEPTION_MSG = 'Invalid password'
MSG = 'Postgres session exception: ' + EXCEPTION_MSG


def start_t_1(shell):
    return '2021-08-19 03:15:54+01'


def start_t_2(shell):
    return '2021-08-19 03:04:50+01'


def up_t_1(shell):
    return '04:12:58'


def up_t_2(shell, ):
    return '04:24:02'


class SideEffect:
    def __init__(self, *fns):
        self.fs = iter(fns)

    def __call__(self, *args, **kwargs):
        f = next(self.fs)
        return f(*args, **kwargs)


class TestUptime(unittest.TestCase):

    def setUp(self):
        self.shell = Mock()
        self.controller = UptimeController(self.shell)

    def tearDown(self):
        self.shell = None
        self.controller = None

    @patch('pglib.admin.controllers.uptime.Role')
    @patch('pglib.admin.controllers.uptime.EnmKubeSession')
    @patch('pglib.admin.controllers.uptime.UptimeController.get_uptime')
    @patch('pglib.admin.controllers.uptime.UptimeController.get_start_time')
    def test_uptime_controller_displays_expected_result(self, start_time,
                                                        uptime, kube_ses, pod):
        pod.return_value.leader = 'postgres-0'
        pod.return_value.follower = 'postgres-1'
        uptime.side_effect = SideEffect(up_t_1, up_t_2)
        start_time.side_effect = SideEffect(start_t_1, start_t_2)

        self.assertEqual(self.controller.execute(), EXPECTED)

    def test_class_attributes_are_set(self):
        self.assertEqual(self.controller.name, 'uptime')
        self.assertEqual(self.controller.title, 'Postgres Start and Uptime')

    @patch('pyu.log.log.error')
    @patch('pglib.admin.controllers.uptime.PsqlClient')
    def test_get_data_throws_psql_exception_rets_unavailable(self, psql, elog):
        psql.return_value.runq.side_effect = PsqlAuthenticationFailure(
            EXCEPTION_MSG)
        self.assertEqual(self.controller.get_data('query', None),
                         'Unavailable')
        elog.assert_called_with(MSG, stdout=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
