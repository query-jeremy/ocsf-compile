
from dataclasses import dataclass

from ocsf.repository.definitions import ObjectDefn, EventDefn

@dataclass
class ProtoSchema:
    objects: dict[str, ObjectDefn]
    events: dict[str, EventDefn]

