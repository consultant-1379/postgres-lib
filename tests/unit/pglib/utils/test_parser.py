import unittest2 as unittest

from pglib.utils.parser import BorderedTitleTableParser

PATRONI_OUT = '''
+ Cluster: postgres (7020762932214296660) ----+---------+----+-----------+
| Member     | Host            | Role         | State   | TL | Lag in MB |
+------------+-----------------+--------------+---------+----+-----------+
| postgres-0 | 192.168.59.81   | Leader       | running |  9 |           |
| postgres-1 | 192.168.156.181 | Sync Standby | running |  9 |         0 |
+------------+-----------------+--------------+---------+----+-----------+
'''


class TestBorderedTitleTableParser(unittest.TestCase):

    def test_patronictl_list_parses(self):
        parser = BorderedTitleTableParser(PATRONI_OUT)
        self.assertEqual([{'Member': 'postgres-0', 'Host': '192.168.59.81',
                           'Role': 'Leader', 'State': 'running', 'TL': '9',
                           'Lag in MB': ''},
                          {'Member': 'postgres-1', 'Host': '192.168.156.181',
                           'Role': 'Sync Standby', 'State': 'running',
                           'TL': '9', 'Lag in MB': '0'}], parser.parse())


if __name__ == '__main__':
    unittest.main(verbosity=2)
