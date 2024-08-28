from pglib.env.cenm.sg import PgServiceGroupCenm
from pglib.env.penm.sg import PgServiceGroupPenm
from pglib.env.venm.sg import PgServiceGroupVenm

from pyu.enm import EnmEnvMapper as Mapper


Mapper.penm.add_custom_service_group(PgServiceGroupPenm)
Mapper.venm.add_custom_service_group(PgServiceGroupVenm)
Mapper.cenm.add_custom_service_group(PgServiceGroupCenm)
