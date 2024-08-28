from datetime import datetime
import time
from unittest2 import TestCase

from pglib.db.prepared_transaction import PreparedTransaction


class TestPreparedTransaction(TestCase):

    def test_older_than_seconds(self):
        pt1 = PreparedTransaction("foo", "postgres", "postgre", time.time())
        print(pt1)
        self.assertFalse(pt1.is_older_than_seconds(10))

        pt2 = PreparedTransaction("foo", "postgres", "postgre", time.time() - 15)
        print(pt2)
        self.assertTrue(pt2.is_older_than_seconds(10))

    def test_older_than_days(self):
        pt1 = PreparedTransaction("foo", "postgres", "postgre", time.time())
        self.assertFalse(pt1.is_older_than_days(1))

        pt2 = PreparedTransaction("foo", "postgres", "postgre", time.time() - 3 * 24 * 60 * 60)
        self.assertTrue(pt2.is_older_than_days(3))

    def test_equal(self):
        created = time.time()
        pt1 = PreparedTransaction("foo", "postgres", "postgre", created)
        pt2 = PreparedTransaction("foo", "postgres", "postgre", created - 1)
        pt3 = PreparedTransaction("bar", "postgres", "postgre", created)
        pt4 = PreparedTransaction("foo", "postgres", "postgre", created)
        self.assertFalse(pt1 == pt2)
        self.assertFalse(pt1 == pt3)
        self.assertTrue(pt1 == pt4)
        self.assertFalse(pt2 == pt3)

    def test_not_equal(self):
        created = time.time()
        pt1 = PreparedTransaction("foo", "postgres", "postgre", created)
        pt2 = PreparedTransaction("foo", "postgres", "postgre", created - 1)
        pt3 = PreparedTransaction("bar", "postgres", "postgre", created)
        pt4 = PreparedTransaction("foo", "postgres", "postgre", created)
        self.assertTrue(pt1 != pt2)
        self.assertTrue(pt1 != pt3)
        self.assertFalse(pt1 != pt4)
        self.assertTrue(pt2 != pt3)

    def test_repr(self):
        created = time.time()
        pt = PreparedTransaction("foo", "postgres", "postgre", created)
        self.assertTrue(
            str(pt) == '{"gid": foo, "owner": postgres, ' \
            '"database": postgre, "created": %s}' \
            % datetime.fromtimestamp(created))