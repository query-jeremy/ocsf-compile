"""This module contains the dataclasses that represent the OCSF schema."""

from abc import ABC
from dataclasses import dataclass
from typing import Any, Optional, TypeVar

# TODO verify modeling of $include

IncludeTarget = str | list[str]

class DefinitionData(ABC): ...


@dataclass
class VersionDefn(DefinitionData):
    version: Optional[str] = None


@dataclass
class EnumMemberDefn:
    """An enum member. Enums are dictionaries of str: EnumMemberDefn."""

    caption: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class DeprecationInfoDefn:
    """Deprecation information for an object, event, or attribute."""

    message: Optional[str] = None
    since: Optional[str] = None


@dataclass
class TypeDefn:
    """A data type definition."""

    caption: Optional[str] = None
    description: Optional[str] = None
    is_array: Optional[bool] = None
    deprecated: Optional[DeprecationInfoDefn] = None
    max_len: Optional[int] = None
    observable: Optional[int] = None
    range: Optional[list[int]] = None
    regex: Optional[str] = None
    type: Optional[str] = None
    type_name: Optional[str] = None
    values: Optional[list[Any]] = None

@dataclass
class DictionaryTypesDefn:
    attributes: Optional[dict[str, TypeDefn]] = None
    caption: Optional[str] = None
    description: Optional[str] = None

@dataclass
class AttrDefn:
    """An attribute definition."""

    caption: Optional[str] = None
    requirement: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    is_array: Optional[bool] = None
    deprecated: Optional[DeprecationInfoDefn] = None
    enum: Optional[dict[str, EnumMemberDefn]] = None
    group: Optional[str] = None
    observable: Optional[int] = None
    profile: Optional[str | list[str]] = None
    sibling: Optional[str] = None

@dataclass
class DictionaryDefn(DefinitionData):
    """A dictionary definition."""

    name: Optional[str] = None
    caption: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[dict[str, AttrDefn]] = None
    types: Optional[DictionaryTypesDefn] = None


@dataclass
class ObjectDefn(DefinitionData):
    """An object definition."""

    caption: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[dict[str, AttrDefn | IncludeTarget]] = None
    extends: Optional[str] = None
    observable: Optional[int] = None
    profiles: Optional[list[str]] = None
    constraints: Optional[dict[str, list[str]]] = None
    deprecated: Optional[DeprecationInfoDefn] = None
    include: Optional[IncludeTarget] = None


@dataclass
class EventDefn(DefinitionData):
    """An event definition."""

    caption: Optional[str] = None
    name: Optional[str] = None
    attributes: Optional[dict[str, AttrDefn | IncludeTarget]] = None
    description: Optional[str] = None
    uid: Optional[int] = None
    category: Optional[str] = None
    extends: Optional[str] = None
    profiles: Optional[list[str]] = None
    associations: Optional[dict[str, list[str]]] = None
    constraints: Optional[dict[str, list[str]]] = None
    deprecated: Optional[DeprecationInfoDefn] = None
    include: Optional[IncludeTarget] = None


@dataclass
class IncludeDefn(DefinitionData):
    """An include definition."""

    caption: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[dict[str, AttrDefn | IncludeTarget]] = None
    annotations: Optional[dict[str, str]] = None


@dataclass
class ProfileDefn(DefinitionData):
    """A profile definition."""

    caption: Optional[str] = None
    name: Optional[str] = None
    meta: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[dict[str, AttrDefn | IncludeTarget]] = None
    deprecated: Optional[DeprecationInfoDefn] = None
    annotations: Optional[dict[str, str]] = None


@dataclass
class ExtensionDefn(DefinitionData):
    """An extension definition."""

    name: Optional[str] = None
    uid: Optional[int] = None
    caption: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    deprecated: Optional[DeprecationInfoDefn] = None

@dataclass
class CategoryDefn:
    """A category definition."""

    caption: Optional[str] = None
    description: Optional[str] = None
    uid: Optional[int] = None
    type: Optional[str] = None


@dataclass
class CategoriesDefn(DefinitionData):
    """A list of categories."""

    attributes: Optional[dict[str, CategoryDefn]] = None
    caption: Optional[str] = None
    description: Optional[str] = None
    name: Optional[str] = None


DefinitionT = TypeVar("DefinitionT", bound=DefinitionData, covariant=True)
AnyDefinition = ObjectDefn | EventDefn | ProfileDefn | ExtensionDefn | DictionaryDefn | IncludeDefn | CategoriesDefn | VersionDefn