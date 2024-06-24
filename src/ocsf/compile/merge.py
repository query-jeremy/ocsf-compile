

from dataclasses import dataclass
from typing import get_type_hints, cast, Optional

from ocsf.repository.definitions import DefinitionPart

@dataclass
class MergeOptions:
    overwrite: bool = False
    allow_fields: Optional[list[str | tuple[str, ...]]] = None
    deny_fields: Optional[list[str | tuple[str, ...]]] = None


def merge(left: DefinitionPart, right: DefinitionPart, options: MergeOptions = MergeOptions(), trail: tuple[str, ...] = tuple()) -> None:
    """Merge the right definition into the left definition."""

    for attr, _ in get_type_hints(left).items():
        if hasattr(right, attr):
            path = trail + (attr, )

            left_value = getattr(left, attr)
            right_value = getattr(right, attr)

            if isinstance(left_value, dict) and isinstance(right_value, dict):
                left_value = cast(dict[str, DefinitionPart], left_value)
                right_value = cast(dict[str, DefinitionPart], right_value)

                for key, value in right_value.items():
                    if key not in left_value:
                        left_value[key] = value
                    else:
                        merge(left_value[key], value, options, path)
            else:
                if options.overwrite:
                    update = True
                else:
                    update = left_value is None and right_value is not None

                if update is True and options.allow_fields is not None:
                    update = False

                    for allow in options.allow_fields:
                        if isinstance(allow, tuple):
                            if path[: len(allow)] == allow:
                                update = True
                                break
                        else:
                            if attr == allow:
                                update = True
                                break

                if update is True and options.deny_fields is not None:
                    for deny in options.deny_fields:
                        if isinstance(deny, tuple):
                            if path[: len(deny)] == deny:
                                update = False
                                break
                        else:
                            if attr == deny:
                                update = False
                                break

                if update:
                    setattr(left, attr, right_value)
