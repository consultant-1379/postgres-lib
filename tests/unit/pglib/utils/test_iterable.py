import unittest2 as unittest

from pglib.utils.iterable import flatten_list_tuples


class TestIterable(unittest.TestCase):

    def test_flatten_tuples_nums(self):
        alist = [(3, 9), (5, 4)]
        self.assertEqual([3, 9, 5, 4], flatten_list_tuples(alist))

    def test_flatten_tuples_dbs(self):
        output = [('configds',), ('flowautomationdb',), ('flsdb',)]
        self.assertEqual(['configds', 'flowautomationdb', 'flsdb'],
                         flatten_list_tuples(output))


if __name__ == '__main__':
    unittest.main(verbosity=2)
