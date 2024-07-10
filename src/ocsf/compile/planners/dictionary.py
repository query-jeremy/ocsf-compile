from dataclasses import dataclass

from ..protoschema import ProtoSchema
from ..merge import merge, MergeResult, MergeOptions

from .planner import Operation, Planner, Analysis
from ocsf.repository import DefinitionFile, EventDefn, ObjectDefn, SpecialFiles, DictionaryDefn


@dataclass(eq=True, frozen=True)
class DictionaryOp(Operation):
    def __str__(self):
        return f"Dictionary {self.target} <- {self.prerequisite}"

    def apply(self, schema: ProtoSchema) -> MergeResult:
        target = schema[self.target]
        assert target.data is not None

        assert self.prerequisite is not None
        prereq = schema[self.prerequisite]
        assert prereq.data is not None
        assert isinstance(prereq.data, DictionaryDefn)

        return merge(
            target.data, prereq.data, options=MergeOptions(allowed_fields=["attributes"], add_dict_items=False)
        )


class DictionaryPlanner(Planner):
    def analyze(self, input: DefinitionFile) -> Analysis:
        if input.data is not None:
            if isinstance(input.data, EventDefn) or isinstance(input.data, ObjectDefn):
                return DictionaryOp(input.path, SpecialFiles.DICTIONARY.value)
