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

from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import (
    get_source_of_instance,
    get_user_value,
    replace_file_ext,
    get_vertex_zero,
    )

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc


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


def set_item_scale(item, scale):
    item.select(replace=True)
    lx.eval('transform.channel scl.X {}'.format(scale[0]))
    lx.eval('transform.channel scl.Y {}'.format(scale[1]))
    lx.eval('transform.channel scl.Z {}'.format(scale[2]))


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
    lx.eval(f'replicator.particle {point_source.id}')
    lx.eval(f'replicator.source {prototype.id}')
    return replicator


def get_source_size(source: modo.Item) -> list[float]:
    source_base = get_source_of_instance(source)
    source_scl_x, source_scl_y, source_scl_z = get_item_scale(source)
    base_scl_x, base_scl_y, base_scl_z = get_size(source_base)
    source_size = [base_scl_x * source_scl_x, base_scl_y * source_scl_y, base_scl_z * source_scl_z]  # type: ignore

    return source_size


def match_pos_rot(item: modo.Item, itemTo: modo.Item):
    lx.eval(f'item.match item pos average:false item:{item.id} itemTo:{itemTo.id}')
    lx.eval(f'item.match item rot average:false item:{item.id} itemTo:{itemTo.id}')


def get_ratios(source_size: list[float], target_size: list[float], constraints: Constraints) -> list[float]:
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


def item_replicate(source: modo.Item, target: modo.Item, constraints: Constraints):
    source_size = get_source_size(source)
    target_size = get_size(target)

    source_replicator = get_replicator_source(source)
    point_source = get_vertex_zero()
    source_align = make_replicator(source_replicator, point_source)
    source_align.setParent()

    match_pos_rot(source_align, target)

    # initiate visibility on instance
    source_align.select(replace=True)
    lx.eval('item.channel locator$visible default')
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

    # set scale
    set_scale_factor(source_align, [ratio_x, ratio_y, ratio_z])

    replace_item(item_to_insert=source_align,
                 item_to_remove=target,
                 item_to_remove_new_parent=get_tmp_folder(h3dc.TMP_FOLDER_NAME))


def item_align(source: modo.Item, target: modo.Item, do_instance: bool, constraints: Constraints):
    source_base = get_source_of_instance(source)

    # get source scale
    sx, sy, sz = get_item_scale(source)
    # base size
    bx, by, bz = get_size(source_base)
    source_size = [bx * sx, by * sy, bz * sz]  # type: ignore
    # get target size
    target_size = get_size(target)

    if do_instance:
        source_item = modo.Scene().duplicateItem(item=source_base, instance=True)
    else:
        source_item = source
    source_item.setParent()  # type: ignore

    modo.Scene().deselect()
    source_item.select()  # type: ignore
    target.select()
    lx.eval('item.match item pos average:false item:{} itemTo:{}'.format(source_item.id, target.id))  # type: ignore
    lx.eval('item.match item rot average:false item:{} itemTo:{}'.format(source_item.id, target.id))  # type: ignore
    if do_instance:
        # initiate scale on instance
        source_item.select(replace=True)  # type: ignore
        source_base.select()  # type: ignore
        lx.eval('item.match item scl')
    # initiate visibility on instance
    source_item.select(replace=True)  # type: ignore
    lx.eval('item.channel locator$visible default')
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

    # set scale
    set_scale_factor(source_item, [ratio_x, ratio_y, ratio_z])

    replace_item(item_to_insert=source_item,
                 item_to_remove=target,
                 item_to_remove_new_parent=get_tmp_folder(h3dc.TMP_FOLDER_NAME))


save_log = get_user_value(h3dc.USER_VAL_NAME_SAVE_LOG)
log_name = replace_file_ext(modo.Scene().name)
h3dd = H3dDebug(enable=save_log, file=log_name)
