import os

from ocsf.util import get_schema
from ocsf.compare import compare, ChangedSchema, NoChange, ChangedEvent, ChangedAttr, Removal, Addition
from ocsf.compare.formatter import format
from ocsf.repository import read_repo
from ocsf.compile.compiler import Compilation


def get_diff():
    s1 = get_schema(os.environ["SCHEMA_PATH"])
    s2 = Compilation(read_repo(os.environ["REPO_PATH"])).build()

    return compare(s1, s2)


def test_versus():
    from pprint import pprint

    diff = get_diff()

    assert isinstance(diff, ChangedSchema)
    #print(f"--- {os.environ['SCHEMA_PATH']}")
    #print(f"+++ {os.environ['REPO_PATH']}")
    # format(diff)

    # s2 = Compilation(read_repo(os.environ["REPO_PATH"])).build()
    # pprint(s2.objects["device"])

    ok = 0
    bad = 0
    bad_attrs = 0

    for name, event in diff.classes.items():
        fail = 0
        if not isinstance(event, NoChange):
            if isinstance(event, Removal):
                print("REMOVED", name)
                bad += 1
            elif isinstance(event, Addition):
                print("ADDED", name)
                bad += 1
            else:
                assert isinstance(event, ChangedEvent)
                for attr, change in event.attributes.items():
                    failed = False
                    if not attr.endswith("_dt") and not attr.endswith("_name"):
                        if isinstance(change, NoChange):
                            ok += 1
                            break
                        elif isinstance(change, ChangedAttr):
                            if not isinstance(change.caption, NoChange):
                                print(name, attr, "caption", change.caption)
                                failed = True
                            if not isinstance(change.description, NoChange):
                                print(name, attr, "description", change.description)
                                failed = True
                            if not isinstance(change.observable, NoChange):
                                print(name, attr, "observable", change.observable)
                                failed = True
                            if not isinstance(change.requirement, NoChange):
                                print(name, attr, "requirement", change.requirement)
                                failed = True
                            if not isinstance(change.type, NoChange):
                                print(name, attr, "type", change.type)
                                failed = True
                            if not isinstance(change.sibling, NoChange):
                                print(name, attr, "sibling", change.sibling)
                                failed = True
                            if not isinstance(change.is_array, NoChange):
                                print(name, attr, "is_array", change.is_array)
                                failed = True
                            if not isinstance(change.group, NoChange):
                                print(name, attr, "group", change.group)
                                failed = True
                            if not isinstance(change.profile, NoChange):
                                print(name, attr, "profile", change.profile)
                                failed = True
                            if isinstance(change.enum, dict):
                                for k, value in change.enum.items():
                                    if not isinstance(value, NoChange):
                                        print(name, attr, "enum", k, value)
                                        failed = True
                    if failed:
                        fail += 1
                        
            if fail > 0:
                bad += 1
                bad_attrs += fail
            else:
                ok += 1
        else:
            ok += 1
        # if not isinstance(event, NoChange):
        #    pprint(event)
        # assert isinstance(event, NoChange)
    # pprint(diff.classes)
    print("Good", ok)
    print("Bad", bad)
    print("Bad Attrs", bad_attrs)
    assert bad == 0

    # pprint(get_diff())
    # assert False
