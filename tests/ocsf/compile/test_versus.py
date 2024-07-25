import os
from typing import Any

from ocsf.util import get_schema
from ocsf.compare import (
    compare,
    ChangedSchema,
    Change,
    NoChange,
    ChangedEvent,
    ChangedAttr,
    ChangedObject,
    Removal,
    Addition,
    Difference,
)
from ocsf.repository import read_repo
from ocsf.compile.compiler import Compilation


def get_diff():
    s1 = get_schema(os.environ["SCHEMA_PATH"])
    s2 = Compilation(read_repo(os.environ["REPO_PATH"])).build()

    return compare(s1, s2)


def check_attr(thing: Difference[Any], attr: str):
    assert isinstance(getattr(thing, attr), NoChange), f"Expected {attr} to be NoChange, got {getattr(thing, attr)}"


def test_versus():
    diff = get_diff()

    assert isinstance(diff, ChangedSchema)

    for name in sorted(diff.classes.keys()):
        event = diff.classes[name]
        print("Testing event:", name)

        if not isinstance(event, NoChange):
            assert not isinstance(event, Removal), f"Event {name} was removed"
            assert not isinstance(event, Addition), f"Event {name} was added"
            assert isinstance(event, ChangedEvent)

            check_attr(event, "caption")
            check_attr(event, "description")
            check_attr(event, "uid")
            check_attr(event, "category")
            check_attr(event, "profiles")
            check_attr(event, "associations")
            check_attr(event, "constraints")
            check_attr(event, "deprecated")

            for attr in sorted(event.attributes.keys()):
                change = event.attributes[attr]
                print("  Testing attribute:", ".".join([name, attr]))

                if isinstance(change, NoChange):
                    continue

                assert isinstance(change, ChangedAttr)

                for attr in [
                    "caption",
                    "description",
                    "observable",
                    "requirement",
                    "type",
                    "sibling",
                    "is_array",
                    "group",
                ]:
                    check_attr(change, attr)

                # Suspected bug in OCSF server not always assigning profiles
                assert isinstance(change.profile, NoChange) or (
                    isinstance(change.profile, Change) and change.profile.before is None
                )

                if name not in ("ntp_activity", "tunnel_activity") and attr != "type_uid":
                    if isinstance(change.enum, dict):
                        for k, value in change.enum.items():
                            assert isinstance(
                                value, NoChange
                            ), f"Expected enum value {k} to be NoChange, got {value}"
                    else:
                        assert isinstance(change.enum, NoChange), f"Expected enum to be NoChange, got {change.enum}"

    for name in sorted(diff.objects.keys()):
        obj = diff.objects[name]
        print("Testing object:", name)

        if not isinstance(obj, NoChange):
            assert not isinstance(obj, Removal), f"obj {name} was removed"
            assert not isinstance(obj, Addition), f"obj {name} was added"
            assert isinstance(obj, ChangedObject)
            ...
