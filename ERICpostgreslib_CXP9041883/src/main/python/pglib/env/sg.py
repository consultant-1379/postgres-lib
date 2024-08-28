from pglib.env.consts import PgCommonConstants
from pglib.env.files import PgFiles

from pyu.decor.cache import cached_property
from pyu.enm.sg import EnmServiceGroupBase


class PgServiceGroupBase(EnmServiceGroupBase):
    name = 'pg'
    constants_class = PgCommonConstants

    @cached_property()
    def service(self):  # pylint: disable=W0236
        raise NotImplementedError

    @cached_property()
    def consts(self):  # pylint: disable=W0236
        return self.constants_class(self.shell)

    @cached_property()
    def files(self):  # pylint: disable=W0236
        return PgFiles(self.shell)

    @property
    def members(self):
        raise NotImplementedError
