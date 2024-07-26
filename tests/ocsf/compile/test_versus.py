import os
from typing import Any

from ocsf.util import get_schema
from ocsf.compare import (
    compare,
    ChangedSchema,
    ChangedProfile,
    ChangedExtension,
    Change,
    NoChange,
    ChangedEvent,
    ChangedDeprecationInfo,
    ChangedAttr,
    ChangedObject,
    Removal,
    Addition,
    Difference,
)
from ocsf.repository import read_repo
from ocsf.compile.compiler import Compilation


def get_diff():
    # s1: Reading a schema from a JSON file compiled by the OCSF server
    s1 = get_schema(os.environ["SCHEMA_PATH"])
    
    # s2: Reading a schema from the same repository
    s2 = Compilation(read_repo(os.environ["REPO_PATH"])).build()

    return compare(s1, s2)


def check_prop(thing: Difference[Any], attr: str):
    assert isinstance(getattr(thing, attr), NoChange), f"Expected {attr} to be NoChange, got {getattr(thing, attr)}"

def check_dict(thing: dict[Any, Any] | NoChange, attr: str):
    if isinstance(thing, NoChange):
        return
    for k, v in thing.items():
        assert isinstance(v, NoChange), f"Expected {attr}.{k} to be NoChange, got {v}"


def test_versus():
    diff = get_diff()

    if isinstance(diff, NoChange):
        # Not currently possible with the mechanics of compare, but logically permissible
        assert True
        return

    assert isinstance(diff, ChangedSchema)

    assert isinstance(diff.version, NoChange)

    for name in sorted(diff.classes.keys()):
        event = diff.classes[name]
        print("Testing event:", name)

        if not isinstance(event, NoChange):
            assert not isinstance(event, Removal), f"Event {name} was removed"
            assert not isinstance(event, Addition), f"Event {name} was added"
            assert isinstance(event, ChangedEvent)

            check_prop(event, "caption")
            check_prop(event, "description")
            check_prop(event, "uid")
            check_prop(event, "category")
            check_prop(event, "extends")

            # TODO I have yet to reason out how the OCSF server builds this list
            # of profiles or what it uses them for
            #check_prop(event, "profiles")

            check_dict(event.associations, "associations")
            check_dict(event.constraints, "constraints")

            if not isinstance(event.deprecated, NoChange):
                assert isinstance(event.deprecated, ChangedDeprecationInfo)
                check_prop(event.deprecated, "message")
                check_prop(event.deprecated, "since")

            for attr in sorted(event.attributes.keys()):
                change = event.attributes[attr]
                print("  Testing attribute:", ".".join([name, attr]))

                if isinstance(change, NoChange):
                    continue

                assert not isinstance(change, Removal), f"Attribute {name}.{attr} was removed"
                assert not isinstance(change, Addition), f"Attribute {name}.{attr} was added"
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
                    check_prop(change, attr)

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
            assert not isinstance(obj, Removal), f"Object {name} was removed"
            assert not isinstance(obj, Addition), f"Object {name} was added"
            assert isinstance(obj, ChangedObject)

            check_prop(obj, "caption")
            check_prop(obj, "description")
            check_prop(obj, "observable")
            check_prop(obj, "name")
            check_prop(obj, "extends")
            # TODO See comment above about profiles
            #check_prop(obj, "profiles")

            # TODO It appears the OCSF server is not correctly inheriting
            # constraints from _entity; make this exception more specific.
            #check_dict(obj.constraints, "constraints")

            if not isinstance(obj.deprecated, NoChange):
                assert isinstance(obj.deprecated, ChangedDeprecationInfo)
                check_prop(obj.deprecated, "message")
                check_prop(obj.deprecated, "since")

            for attr in sorted(obj.attributes.keys()):
                change = obj.attributes[attr]
                print("  Testing attribute:", ".".join([name, attr]))

                if isinstance(change, NoChange):
                    continue

                assert not isinstance(change, Removal), f"Attribute {name}.{attr} was removed"
                assert not isinstance(change, Addition), f"Attribute {name}.{attr} was added"
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
                    check_prop(change, attr)


    for name in sorted(diff.profiles.keys()):
        print("Testing profile:", name)
        profile = diff.profiles[name]

        if not isinstance(profile, NoChange):
            assert not isinstance(profile, Removal), f"Profile {name} was removed"
            assert not isinstance(profile, Addition), f"Profile {name} was added"
            assert isinstance(profile, ChangedProfile)

            check_prop(profile, "caption")
            check_prop(profile, "description")
            check_prop(profile, "name")

            if not isinstance(obj.deprecated, NoChange):
                assert isinstance(obj.deprecated, ChangedDeprecationInfo)
                check_prop(obj.deprecated, "message")
                check_prop(obj.deprecated, "since")

            for attr in sorted(obj.attributes.keys()):
                change = obj.attributes[attr]
                print("  Testing attribute:", ".".join([name, attr]))

                if isinstance(change, NoChange):
                    continue

                assert not isinstance(change, Removal), f"Attribute {name}.{attr} was removed"
                assert not isinstance(change, Addition), f"Attribute {name}.{attr} was added"
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
                    check_prop(change, attr)

    for name in sorted(diff.extensions.keys()):
        extn = diff.extensions[name]
        print("Testing extension:", name)

        if not isinstance(extn, NoChange):
            assert not isinstance(extn, Removal), f"Extension {name} was removed"
            assert not isinstance(extn, Addition), f"Extension {name} was added"
            assert isinstance(extn, ChangedExtension)

            check_prop(extn, "caption")
            check_prop(extn, "description")
            check_prop(extn, "name")
            check_prop(extn, "version")

            if not isinstance(extn.deprecated, NoChange):
                assert isinstance(extn.deprecated, ChangedDeprecationInfo)
                check_prop(extn.deprecated, "message")
                check_prop(extn.deprecated, "since")



