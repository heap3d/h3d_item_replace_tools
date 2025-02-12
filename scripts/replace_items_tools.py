#!/usr/bin/python
# ================================
# (C)2022-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# replace selected by specific item instances
# ================================

import modo
import lx
import modo.constants as c
import math

from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import (
    get_source_of_instance,
    get_user_value,
    replace_file_ext,
    get_vertex_zero,
    match_pos_rot,
    match_scl,
    get_parent_index,
    parent_items_to,
    )

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc


MULTIPOINT_SOURCE_SUFFIX = 'multipoint_source'


class Constraints:
    def __init__(self, mode, order, use_x, use_y, use_z):
        self.mode = mode
        self.order = order
        self.use_x = use_x
        self.use_y = use_y
        self.use_z = use_z


def get_size(item):
    if item.type != 'mesh' and item.type != 'meshInst':
        return [0.0, 0.0, 0.0]

    s_x, s_y, s_z = get_item_scale(item)
    if item.type == 'meshInst':
        corners = get_source_of_instance(item).geometry.boundingBox  # type: ignore
    else:
        corners = item.geometry.boundingBox
    size_x = abs(corners[1][0] - corners[0][0]) * s_x
    size_y = abs(corners[1][1] - corners[0][1]) * s_y
    size_z = abs(corners[1][2] - corners[0][2]) * s_z

    return [size_x, size_y, size_z]


def set_scale_factor(item, factor):
    # get current scale
    s_x, s_y, s_z = get_item_scale(item)
    # set new scale
    set_item_scale(item, [s_x * factor[0], s_y * factor[1], s_z * factor[2]])


def replace_item(item_to_insert, item_to_remove, item_to_remove_new_parent):
    parent = item_to_remove.parent
    children = item_to_remove.children()
    if parent is not None:
        item_to_insert.select(replace=True)
        # print('parent:<{}>,  children:<{}>,  item_to_insert:<{}>'.format(parent, children, item_to_insert))
        parent.select()
        lx.eval('item.parent inPlace:1')
    for item in children:
        item.select(replace=True)
        item_to_insert.select()
        lx.eval('item.parent inPlace:1')

    item_to_remove.select(replace=True)
    item_to_remove_new_parent.select()
    lx.eval('item.parent inPlace:1')


def get_tmp_folder(name):
    try:
        tmp_folder = modo.Scene().item(name)
    except LookupError:
        tmp_folder = modo.Scene().addItem(itype='groupLocator', name=name)
        tmp_folder.channel('visible').set('allOff')  # type: ignore
        tmp_folder.select(replace=True)
        lx.eval('item.editorColor magenta')

    return tmp_folder


def get_item_scale(item):
    item.select(replace=True)
    x = lx.eval('transform.channel scl.X ?')
    y = lx.eval('transform.channel scl.Y ?')
    z = lx.eval('transform.channel scl.Z ?')

    return [x, y, z]


def set_item_scale(item: modo.Item, scale: list[float]):
    lx.eval(f'transform.channel scl.X {scale[0]} item:{{{item.id}}}')
    lx.eval(f'transform.channel scl.Y {scale[1]} item:{{{item.id}}}')
    lx.eval(f'transform.channel scl.Z {scale[2]} item:{{{item.id}}}')


def get_replicator_source(item: modo.Item) -> modo.Item:
    if not item:
        raise ValueError('None item provided for replicator source')
    if item.type == 'replicator':
        source = item.itemGraph('particle').forward(0)
    elif item.type == 'mesh':
        source = item
    else:
        raise ValueError(f'Invalid  item type for <{item.name=}>: <{item=}>')
    if not source:
        raise ValueError(f'Failed to get replicator sources for <{item.name=}>')

    return source  # type: ignore


def make_replicator(prototype: modo.Item, point_source: modo.Item) -> modo.Item:
    # lx.eval('item.create replicator')
    replicator = modo.Scene().addItem(itype=c.REPLICATOR_TYPE)
    replicator.select(replace=True)
    lx.eval(f'replicator.particle {{{point_source.id}}}')
    lx.eval(f'replicator.source {{{prototype.id}}}')

    return replicator


def get_source_size(source: modo.Item) -> list[float]:
    source_scl_x, source_scl_y, source_scl_z = get_item_scale(source)
    base_scl_x, base_scl_y, base_scl_z = get_size(get_source_of_instance(source))
    source_size = [base_scl_x * source_scl_x, base_scl_y * source_scl_y, base_scl_z * source_scl_z]  # type: ignore

    return source_size


def get_ratios(source: modo.Item, target: modo.Item, constraints: Constraints) -> list[float]:
    source_size = get_source_size(source)
    target_size = get_size(target)

    # check if there are any 0.0 in source_size or target_size
    if any([f == 0.0 for f in (source_size + target_size)]):
        ratio_x = 1
        ratio_y = 1
        ratio_z = 1
    else:
        ratio_x = target_size[0] / source_size[0]
        ratio_y = target_size[1] / source_size[1]
        ratio_z = target_size[2] / source_size[2]

    # determine which constraints are on
    lock_mode = constraints.mode
    lock_order = constraints.order
    if lock_mode == 'XZ':
        if lock_order == 'X':
            ratio_z = ratio_x
        else:
            ratio_x = ratio_z
    elif lock_mode == 'XYZ':
        if lock_order == 'X':
            ratio_y = ratio_x
            ratio_z = ratio_x
        elif lock_order == 'Y':
            ratio_x = ratio_y
            ratio_z = ratio_y
        else:
            ratio_x = ratio_z
            ratio_y = ratio_z

    # reset scale for disabled axis
    if not constraints.use_x:
        ratio_x = 1.0
    if not constraints.use_y:
        ratio_y = 1.0
    if not constraints.use_z:
        ratio_z = 1.0

    return ratio_x, ratio_y, ratio_z  # type: ignore


def set_visible(item: modo.Item, mode: str = 'default'):
    lx.eval(f'item.channel locator$visible {mode} item:{{{item.id}}}')


def item_replicate(
        source: modo.Item,
        target: modo.Item,
        constraints: Constraints
        ) -> modo.Item:
    prototype = get_replicator_source(source)
    point_source = get_vertex_zero()

    source_align = make_replicator(prototype, point_source)
    source_align.name = prototype.name
    source_align.setParent()
    match_pos_rot(source_align, target)
    set_scale_factor(source_align, get_ratios(source, target, constraints))

    replace_item(item_to_insert=source_align,
                 item_to_remove=target,
                 item_to_remove_new_parent=get_tmp_folder(h3dc.TMP_FOLDER_NAME))
    set_visible(source_align)

    return source_align


def create_multipoint_mesh() -> modo.Item:
    mesh = modo.Scene().addMesh()
    mesh.select(replace=True)
    lx.eval('vertMap.new Transform type:xfrm')
    lx.eval('vertMap.new Size psiz true {0.78 0.78 0.78} 1.0')

    return mesh


def point_source_name(basename: str) -> str:
    return f'{basename}_{MULTIPOINT_SOURCE_SUFFIX}'


def add_vertex(mesh: modo.Item, pos: list[float], rot: list[float], scl: float):
    if not mesh:
        raise ValueError('No mesh specified')

    mesh.select(replace=True)
    lx.eval('select.type vertex')

    printd(f'position: {pos}', 1)
    lx.eval('tool.set prim.makeVertex on 0')
    lx.eval(f'tool.attr prim.makeVertex cenX {pos[0]}')
    lx.eval(f'tool.attr prim.makeVertex cenY {pos[1]}')
    lx.eval(f'tool.attr prim.makeVertex cenZ {pos[2]}')
    lx.eval('tool.apply')
    lx.eval('tool.set prim.makeVertex off 0')

    printd(f'rotation: {math.degrees(rot[0])} {math.degrees(rot[1])} {math.degrees(rot[2])}', 1)
    lx.eval('select.vertexMap Transform xfrm replace')
    lx.eval('tool.set TransformRotate on')
    lx.eval(f'tool.setAttr xfrm.transform RX {math.degrees(rot[0])}')
    lx.eval(f'tool.setAttr xfrm.transform RY {math.degrees(rot[1])}')
    lx.eval(f'tool.setAttr xfrm.transform RZ {math.degrees(rot[2])}')
    lx.eval('tool.doApply')
    lx.eval('tool.set TransformRotate off 0')

    printd(f'scale: {scl}', 1)
    lx.eval('select.vertexMap Size psiz replace')
    lx.eval('tool.set vertMap.setWeight on')
    lx.eval(f'tool.setAttr vertMap.setWeight weight {scl}')
    lx.eval('tool.doApply')
    lx.eval('tool.set vertMap.setWeight off 0')
    lx.eval('select.drop vertex')


def item_replicate_multipoint(
        source: modo.Item,
        targets: list[modo.Item],
        constraints: Constraints
        ) -> modo.Item:

    prototype = get_replicator_source(source)
    point_source = create_multipoint_mesh()

    rot_converter = modo.Scene().addItem(itype=c.LOCATOR_TYPE)
    lx.eval(f'transform.channel order xyz item:{{{rot_converter.id}}}')
    tmp_folder = get_tmp_folder(h3dc.TMP_FOLDER_NAME)
    for target in targets:
        pos = target.position.get()
        match_pos_rot(rot_converter, target)
        rot = rot_converter.rotation.get()
        scl = max(get_ratios(source, target, constraints))
        add_vertex(point_source, pos, rot, scl)
        lx.eval(f'item.parent item:{{{target.id}}} parent:{{{tmp_folder.id}}} inPlace:1')
    modo.Scene().removeItems(rot_converter)

    replicator = make_replicator(prototype, point_source)
    replicator.name = prototype.name
    point_source.name = point_source_name(replicator.name)
    replicator.setParent()
    if source.parent:
        lx.eval(f'item.parent item:{{{replicator.id}}} parent:{{{source.parent.id}}} inPlace:1')

    return replicator


def item_instance_and_align(
        source: modo.Item,
        target: modo.Item,
        do_instance: bool,
        constraints: Constraints
        ) -> modo.Item:

    if not source:
        raise ValueError('No source item provided')
    if do_instance:
        source_item = modo.Scene().duplicateItem(item=get_source_of_instance(source), instance=True)
        if not source_item:
            raise ValueError('Failed to duplicate item')
    else:
        source_item = source

    target_parent = target.parent
    target_index = get_parent_index(target)
    source_item.setParent()
    match_pos_rot(source_item, target)

    if do_instance:
        match_scl(source_item, get_source_of_instance(source))  # type: ignore
    set_scale_factor(source_item, get_ratios(source, target, constraints))

    replace_item(item_to_insert=source_item,
                 item_to_remove=target,
                 item_to_remove_new_parent=get_tmp_folder(h3dc.TMP_FOLDER_NAME))

    set_visible(source_item)

    parent_items_to([source_item,], target_parent, target_index)

    return source_item


def item_copy_and_align(
        source: modo.Item,
        target: modo.Item,
        constraints: Constraints
        ) -> modo.Item:
    source_item = modo.Scene().duplicateItem(item=get_source_of_instance(source))
    source_item.setParent()  # type: ignore
    match_pos_rot(source_item, target)  # type: ignore
    match_scl(source_item, get_source_of_instance(source))  # type: ignore
    set_scale_factor(source_item, get_ratios(source, target, constraints))

    replace_item(item_to_insert=source_item,
                 item_to_remove=target,
                 item_to_remove_new_parent=get_tmp_folder(h3dc.TMP_FOLDER_NAME))
    set_visible(source_item)  # type: ignore

    return source_item  # type: ignore


save_log = get_user_value(h3dc.USER_VAL_NAME_SAVE_LOG)
log_name = replace_file_ext(modo.Scene().name)
h3dd = H3dDebug(enable=save_log, file=log_name)
printd = h3dd.print_debug
printi = h3dd.print_items
