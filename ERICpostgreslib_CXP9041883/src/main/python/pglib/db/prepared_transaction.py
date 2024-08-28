from datetime import datetime


class PreparedTransaction(object):

    def __init__(self, gid, owner, database, prepared):
        self._gid = gid
        self._owner = owner
        self._database = database
        self._created = datetime.fromtimestamp(prepared)

    @property
    def gid(self):
        return self._gid

    @property
    def owner(self):
        return self._owner

    @property
    def database(self):
        return self._database

    @property
    def created(self):
        return self._created

    def is_older_than_seconds(self, seconds, log=None):
        delta = datetime.today() - self.created
        # This does not work for a time in the future - which should never
        # happen
        if log is not None:
            log.debug('Delta: %s' % delta)
        return delta.seconds >= seconds

    def is_older_than_days(self, days):
        delta = datetime.today() - self.created
        return delta.days >= days

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.gid == other.gid \
            and self.created == other.created

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '{"gid": %s, "owner": %s, "database": %s, "created": %s}' % \
            (self.gid, self.owner, self.database, self.created)
