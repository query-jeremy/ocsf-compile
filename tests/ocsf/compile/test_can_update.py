from dataclasses import dataclass
from typing import Optional

from ocsf.repository import DefinitionPart
from ocsf.compile.merge import _can_update, MergeOptions  # type: ignore


@dataclass
class Defn(DefinitionPart):
    prop: Optional[int] = None


def _perform_tests(options: MergeOptions) -> tuple[bool, bool, bool, bool]:
    r1 = _can_update(("prop",), None, None, options)
    r2 = _can_update(("prop",), 1, None, options)
    r3 = _can_update(("prop",), None, 1, options)
    r4 = _can_update(("prop",), 1, 2, options)
    return (r1, r2, r3, r4)


def test_can_update():
    assert _perform_tests(MergeOptions(overwrite=False)) == (False, False, True, False)


def test_can_update_overwrite():
    assert _perform_tests(MergeOptions(overwrite=True)) == (True, True, True, True)


def test_can_update_allowed_field():
    assert _perform_tests(MergeOptions(overwrite=False, allowed_fields=["prop"])) == (False, False, True, False)


def test_can_update_allowed_field_overwrite():
    assert _perform_tests(MergeOptions(overwrite=True, allowed_fields=["prop"])) == (True, True, True, True)


def test_can_update_not_allowed_field_overwrite():
    assert _perform_tests(MergeOptions(overwrite=True, allowed_fields=["nope"])) == (False, False, False, False)


def test_can_update_not_allowed_field():
    assert _perform_tests(MergeOptions(overwrite=False, allowed_fields=["nope"])) == (False, False, False, False)


def test_update_ignored_field():
    assert _perform_tests(MergeOptions(overwrite=False, ignored_fields=["prop"])) == (False, False, False, False)


def test_update_ignored_field_overwrite():
    assert _perform_tests(MergeOptions(overwrite=True, ignored_fields=["prop"])) == (False, False, False, False)


def test_deep_allowed():
    assert _can_update(("attrs", "a"), None, 1, MergeOptions(allowed_fields=[("attrs", "a")]))
    assert not _can_update(("attrs",), None, 1, MergeOptions(allowed_fields=[("attrs", "a")]))
    assert _can_update(("attrs", "a"), None, 1, MergeOptions(allowed_fields=[("attrs",)]))


def test_deep_attributes():
    assert _can_update(("attrs", "a", "type"), None, 1, MergeOptions(allowed_fields=[("attrs")]))
