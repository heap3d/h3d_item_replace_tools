#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# Leonard
# move item center position by component selection
# ================================

from typing import Iterable

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import (
    itype_str,
    duplicate_item_with_hierarchy,
)

from h3d_item_replace_tools.scripts.center_utilites import (
    update_instance,
    place_center_at_locator,
    get_instances,
    numparents,
    select_if_exists,
)


def main():
    selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    selected.sort(key=numparents, reverse=True)
    if len(selected) < 2:
        return

    target_item = selected[-1]
    source_items = [item for item in selected[:-1] if item.type == itype_str(c.MESH_TYPE)]

    if not source_items:
        return

    updated_items = align_center_to_item(source_items, target_item)

    select_if_exists(updated_items)


def align_center_to_item(source_items: Iterable[modo.Mesh], target_item: modo.Item) -> list[modo.Item]:
    updated_items = []
    for source_item in source_items:
        instances = get_instances(source_item)
        if not instances:
            item = place_center_at_locator(source_item, target_item)
            updated_items.append(item)
        else:
            items = place_center_at_locator_for_instance_source(source_item, target_item)
            updated_items.extend(items)

    return updated_items


def place_center_at_locator_for_instance_source(source_item: modo.Mesh, target_item: modo.Item) -> list[modo.Item]:
    if not source_item:
        raise TypeError('Source item is not valid.')

    if not target_item:
        raise TypeError('Target item is not valid.')

    updated_items = []

    item_copy = duplicate_item_with_hierarchy(source_item)
    if not isinstance(item_copy, modo.Mesh):
        raise TypeError('Failed to duplicate source mesh.')

    updated_items.append(place_center_at_locator(item_copy, target_item))
    updated_items.extend(update_instance(item_copy, source_item))

    return updated_items


if __name__ == '__main__':
    main()
