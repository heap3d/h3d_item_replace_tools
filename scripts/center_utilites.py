#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# utilites for placing item center
# ================================

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
    make_instance,
    match_pos_rot,
    match_scl,
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


def select_components(mesh: modo.Mesh, components: list, select_type: str):
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


def create_loc_at_selection(mesh: modo.Mesh, select_type: str, orient: bool) -> modo.Item:
    if not mesh:
        raise TypeError('No mesh provided.')

    mesh.select(replace=True)
    lx.eval(f'item.editorColor {COLOR_PROCESSED}')

    drop_components_selection_if_not_component_mode(select_type)
    lx.eval('workPlane.fitSelect')
    drop_components_selection()

    lx.eval(f'select.type {ITEM}')
    locator = modo.Scene().addItem(itype=c.LOCATOR_TYPE)

    locator.select(replace=True)
    lx.eval('item.matchWorkplane pos')
    if orient:
        lx.eval('item.matchWorkplane rot')

    lx.eval('workPlane.reset')

    return locator


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


def update_instance(newmesh: modo.Mesh, oldmesh: modo.Mesh):
    targets = get_instances(oldmesh)

    parent_items_to([newmesh,], oldmesh.parent, get_parent_index(oldmesh))

    tmp_loc = modo.Scene().addItem(itype='locator')
    for target in targets:
        instance_item = make_instance(newmesh)

        match_pos_rot(tmp_loc, oldmesh)
        parent_items_to([instance_item,], tmp_loc)

        match_pos_rot(tmp_loc, target)
        match_scl(tmp_loc, target)
        parent_items_to([instance_item,], target.parent, get_parent_index(target))

    modo.Scene().removeItems(tmp_loc)
    modo.Scene().removeItems(oldmesh, children=True)
