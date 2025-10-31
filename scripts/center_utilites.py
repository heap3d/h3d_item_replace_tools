#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# utilites for placing item center
# ================================

from typing import Iterable, Optional

import modo
import modo.constants as c
import lx

from h3d_utilites.scripts.h3d_utils import (
    ITEM,
    VERTEX,
    EDGE,
    POLYGON,
    get_parent_index,
    get_instances,
    parent_items_to,
    make_instance_with_hierarchy,
    duplicate_item_with_hierarchy,
    match_pos_rot,
    match_pos,
    match_rot,
    match_scl,
    itype_str,
)


COLOR_PROCESSED = 'orange'


def get_selected_components(mesh: modo.Mesh, select_type: str) -> list:
    if not mesh or not isinstance(mesh, modo.Mesh):
        raise TypeError('Invalid mesh provided.')

    if not mesh.geometry:
        raise ValueError('Mesh has no geometry.')

    if select_type == VERTEX:
        if vertices := mesh.geometry.vertices:
            return vertices.selected
    elif select_type == EDGE:
        if edges := mesh.geometry.edges:
            return edges.selected
    elif select_type == POLYGON:
        if polygons := mesh.geometry.polygons:
            return polygons.selected

    return []


def select_components(mesh: modo.Mesh, select_type: str, components: list):
    if not mesh or not isinstance(mesh, modo.Mesh):
        raise TypeError('Invalid mesh provided.')

    if not mesh.geometry:
        raise ValueError('Mesh has no geometry.')

    lx.eval(f'select.type {select_type}')
    if select_type not in (VERTEX, EDGE, POLYGON):
        return

    lx.eval(f'select.drop {select_type}')

    if select_type == VERTEX:
        if mesh.geometry.vertices:
            mesh.geometry.vertices.select(vertices=components)
    if select_type == EDGE:
        if mesh.geometry.edges:
            mesh.geometry.edges.select(edges=components)
    if select_type == POLYGON:
        if mesh.geometry.polygons:
            mesh.geometry.polygons.select(polygons=components)


def create_loc_at_selection(mesh: modo.Mesh, select_type: str, name: Optional[str] = None) -> modo.Item:
    if not mesh:
        raise TypeError('No mesh provided.')

    mesh.select(replace=True)
    lx.eval(f'item.editorColor {COLOR_PROCESSED}')

    if not is_component_mode(select_type):
        drop_components_selection()
        lx.eval(f'select.type {VERTEX}')
    else:
        lx.eval(f'select.type {select_type}')

    lx.eval('workPlane.fitSelect')
    drop_components_selection()

    lx.eval(f'select.type {ITEM}')
    locator = modo.Scene().addItem(itype=c.LOCATOR_TYPE, name=name)

    locator.select(replace=True)
    lx.eval('item.matchWorkplane pos')
    lx.eval('item.matchWorkplane rot')

    lx.eval('workPlane.reset')

    return locator


def is_component_mode(select_type: str) -> bool:
    return select_type in (VERTEX, EDGE, POLYGON)


def drop_components_selection_if_not_component_mode(select_type: str):
    if select_type not in (VERTEX, EDGE, POLYGON):
        drop_components_selection()
        lx.eval(f'select.type {VERTEX}')
    else:
        lx.eval(f'select.type {select_type}')


def drop_components_selection():
    lx.eval(f'select.type {VERTEX}')
    lx.eval(f'select.drop {VERTEX}')

    lx.eval(f'select.type {EDGE}')
    lx.eval(f'select.drop {EDGE}')

    lx.eval(f'select.type {POLYGON}')
    lx.eval(f'select.drop {POLYGON}')


def place_center_at_locator(mesh: modo.Mesh, locator: modo.Item):
    if not mesh or not isinstance(mesh, modo.Mesh):
        raise TypeError('No mesh provided.')

    if not locator:
        raise TypeError('No locator provided.')

    parent = mesh.parent
    hierarchy_index = mesh.parentIndex if parent else mesh.rootIndex
    mesh.select(replace=True)
    lx.eval(f'item.editorColor {COLOR_PROCESSED}')

    mesh.select(replace=True)
    locator.select()
    lx.eval('item.parent inPlace:1')

    mesh.select(replace=True)
    lx.eval('transform.freeze')

    lx.eval(f'item.parent parent:{{}} inPlace:1 position:{hierarchy_index}')

    if parent is not None:
        parent.select()
        lx.eval(f'item.parent inPlace:1 position:{hierarchy_index}')


def update_instance(newmesh: modo.Mesh, oldmesh: modo.Mesh) -> list[modo.Mesh]:
    updated_instances = []
    targets = get_instances(oldmesh)

    parent_items_to([newmesh,], oldmesh.parent, get_parent_index(oldmesh))

    tmp_loc = modo.Scene().addItem(itype='locator')
    for target in targets:
        instance_item = make_instance_with_hierarchy(newmesh)
        if instance_item.type != itype_str(c.MESHINST_TYPE):
            raise TypeError('Failed to create mesh instance item.')

        match_pos_rot(tmp_loc, oldmesh)
        parent_items_to([instance_item,], tmp_loc)

        match_pos_rot(tmp_loc, target)
        match_scl(tmp_loc, target)
        parent_items_to([instance_item,], target.parent, get_parent_index(target))

        updated_instances.append(instance_item)

    modo.Scene().removeItems(tmp_loc)
    modo.Scene().removeItems(oldmesh, children=True)

    return updated_instances


def numparents(item: modo.Item) -> int:
    if not item.parents:
        return 0
    return len(item.parents)


def select_if_exists(items: Iterable[modo.Item]):
    if not items:
        return

    modo.Scene().deselect()
    for item in items:
        try:
            item.select()
        except LookupError:
            pass


def update_center(
        mesh: modo.Mesh,
        select_type: str,
        components: list,
        align_pos: bool = True,
        align_rot: bool = True
        ) -> modo.Mesh:
    if not mesh or not isinstance(mesh, modo.Mesh):
        raise TypeError('Invalid mesh provided.')

    if not mesh.geometry.numVertices:
        return mesh

    original_parent = mesh.parent
    original_parent_index = get_parent_index(mesh)
    select_components(mesh, select_type, components)

    # store mesh original transforms
    original_loc: modo.Item = modo.Scene().addItem(itype=c.LOCATOR_TYPE)
    if not original_loc:
        raise RuntimeError('Failed to create original transforms locator.')
    parent_items_to((original_loc,), mesh, inplace=False)
    parent_items_to((original_loc,), None, inplace=True)

    # reset mesh transforms
    parent_items_to((mesh,), None, inplace=True)
    mesh.select(replace=True)
    lx.eval('transform.reset all')

    # store mesh selection transforms
    selection_loc = create_loc_at_selection(mesh, select_type, name='tmp center')
    parent_items_to((selection_loc,), mesh, inplace=True)

    # restore mesh original transforms with stored new center transforms
    parent_items_to((mesh,), original_loc, inplace=False)

    # restore mesh parenting
    parent_items_to((mesh,), original_parent, index=original_parent_index, inplace=True)

    modo.Scene().removeItems(original_loc)

    # unparent selection locator to not duplicate with mesh
    parent_items_to((selection_loc,), None, inplace=True)

    # create new center locator
    new_center_loc = modo.Scene().addItem(itype=c.LOCATOR_TYPE)
    if not new_center_loc:
        raise RuntimeError('Failed to create new center locator.')
    parent_items_to((new_center_loc,), mesh, inplace=False)
    parent_items_to((new_center_loc,), None, inplace=True)

    if align_pos:
        match_pos(new_center_loc, selection_loc)
    if align_rot:
        match_rot(new_center_loc, selection_loc)

    # duplicate mesh with hierarchy to propagate
    new_mesh = duplicate_item_with_hierarchy(mesh)
    if not isinstance(new_mesh, modo.Mesh):
        raise TypeError('Failed to duplicate mesh.')

    place_center_at_locator(new_mesh, new_center_loc)

    modo.Scene().removeItems(selection_loc)
    modo.Scene().removeItems(new_center_loc)

    update_instance(new_mesh, mesh)

    return new_mesh
