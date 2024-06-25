from dataclasses import dataclass
from typing import get_type_hints, cast, Optional, Any

from ocsf.repository.definitions import DefinitionPart


@dataclass
class MergeOptions:
    overwrite: Optional[bool] = None
    allowed_fields: Optional[list[str | tuple[str, ...]]] = None
    ignored_fields: Optional[list[str | tuple[str, ...]]] = None


def _can_update(path: tuple[str, ...], left_value: Any, right_value: Any, options: MergeOptions) -> bool:
    """Helper function to decide if a value should be updated.

    Below are truth tables showing the logic of this function.

    # Overwrite is False
    |               | R is None | R is not None |
    | L is None     | False     | True          |
    | L is not None | False     | False         |

    # Overwrite is True
    |               | R is None | R is not None |
    | L is None     | True      | True          |
    | L is not None | True      | True          |

    # Field is in allowed_fields, overwrite is True
    |               | R is None | R is not None |
    | L is None     | True      | True          |
    | L is not None | True      | True          |

    # Field is in allowed_fields, overwrite is False
    |               | R is None | R is not None |
    | L is None     | False     | True          |
    | L is not None | False     | False         |

    # Field is in ignore list
    |               | R is None | R is not None |
    | L is None     | False     | False         |
    | L is not None | False     | False         | 
    
    """
    
    update: Optional[bool] = None

    def change_field():
        # If overwrite is True, we'll always update the left value.
        if options.overwrite:
            return True

        # Otherwise, we'll only update the left value if it's None.
        else:
            return left_value is None and right_value is not None

    # Narrow the update to specific white-listed fields if
    # allowed_fields is set.
    if options.allowed_fields is not None:
        update = False

        for allow in options.allowed_fields:
            if isinstance(allow, tuple):
                if path[: len(allow)] == allow:
                    update = change_field()
                    break
            else:
                if path[-1] == allow:
                    update = change_field()
                    break

    # Skip black-listed fields if ignored_fields is set.
    elif options.ignored_fields is not None:
        for deny in options.ignored_fields:
            if isinstance(deny, tuple):
                if path[: len(deny)] == deny:
                    update = False
                    break
            else:
                if path[-1] == deny:
                    update = False
                    break

    if update is None:
        update = change_field()

    return update

MergeResult = list[tuple[str, ...]]

def merge(
    left: DefinitionPart,
    right: DefinitionPart,
    overwrite: Optional[bool] = None,
    *,
    allowed_fields: Optional[list[str | tuple[str, ...]]] = None,
    ignored_fields: Optional[list[str | tuple[str, ...]]] = None,
    options: Optional[MergeOptions] = None,
    trail: tuple[str, ...] = tuple(),
) -> MergeResult:
    """Merge the right definition into the left definition."""

    # This will be a list of all paths of properties that were updated.
    results: MergeResult = []

    if options is None:
        options = MergeOptions()

    # Convert named parameters to options object
    if overwrite is not None:
        options.overwrite = overwrite
    if allowed_fields is not None:
        options.allowed_fields = allowed_fields
    if ignored_fields is not None:
        options.ignored_fields = ignored_fields


    # Now for the money: iterate over all attributes in the left definition and
    # update where necessary.
    for attr, _ in get_type_hints(left).items():
        # If the attribute isn't in the right, there's nothing to do.
        if hasattr(right, attr):
            path = trail + (attr,)

            left_value = getattr(left, attr)
            right_value = getattr(right, attr)
            simple = True

            # Recursively merge dictionaries of str => DefinitionPart
            #########################################################
            # The next 10 lines or so are all to confirm, at runtime, that we're working with 
            # hydrated dictionaries of dict[str, DefinitionPart]. When this is true, we will
            # recursively merge each item in the dictionary.
            #
            # When it isn't, we'll treat both values as if they were scalar values below.
            #
            if isinstance(left_value, dict) and isinstance(right_value, dict):
                left_value = cast(dict[Any, Any], left_value)
                right_value = cast(dict[Any, Any], right_value)

                if len(left_value) > 0 and len(right_value) > 0:
                    k1 = next(iter(left_value.keys()))
                    v1 = left_value[k1]
                    k2 = next(iter(right_value.keys()))
                    v2 = right_value[k2]

                    if isinstance(v1, DefinitionPart) and isinstance(v2, DefinitionPart) and isinstance(k1, str) and isinstance(k2, str):
                        # We've confirmed that these dictionaries are dict[str, DefinitionPart].
                        # Now we can recursively merge each item in the dictionary.
                        simple = False
                        left_value = cast(dict[str, DefinitionPart], left_value)
                        right_value = cast(dict[str, DefinitionPart], right_value)
                    
                        for key, value in right_value.items(): 
                            if _can_update(path + (key,), left_value.get(key, None), value, options):
                                if key not in left_value:
                                    left_value[key] = value
                                    results.append(path + (key,))
                                else:
                                    results += merge(left_value[key], value, options=options, trail=(path + (key,)))
                
            # Merge DefinitionPart objects (OCSF complex types)
            ###################################################
            # If both values are DefinitionPart objects, we'll recursively merge
            # them using the same options this was invoked with.
            #
            elif isinstance(left_value, DefinitionPart) and isinstance(right_value, DefinitionPart):
                simple = False
                results += merge(left_value, right_value, options=options, trail=path)

            # Merge everything else
            #######################
            # For scalar values, lists, non-DefinitionPart dictionaries and
            # objects (OCSF complex types), or cases where one side is a
            # DefinitionPart and the other is None, merge the values according
            # to the options.
            # 
            if simple and _can_update(path, left_value, right_value, options):
                setattr(left, attr, right_value)
                results.append(path)

    return results