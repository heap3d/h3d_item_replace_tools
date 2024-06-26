#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# replace selected by specific item instances
# ================================

import modo
import lx

from h3d_utilites.scripts.h3d_debug import H3dDebug
import h3d_utilites.scripts.h3d_utils as h3du

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc


def get_size(item):
    if item.type != 'mesh' and item.type != 'meshInst':
        return [0.0, 0.0, 0.0]
    s_x, s_y, s_z = get_item_scale(item)
    if item.type == 'meshInst':
        corners = h3du.get_source_of_instance(item).geometry.boundingBox  # type: ignore
    else:
        corners = item.geometry.boundingBox
    size_x = abs(corners[1][0] - corners[0][0]) * s_x
    size_y = abs(corners[1][1] - corners[0][1]) * s_y
    size_z = abs(corners[1][2] - corners[0][2]) * s_z

    return [size_x, size_y, size_z]


def scale_factor(item, factor):
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


def item_align(source, target, do_instance, constraints):
    # get source size
    source_base = h3du.get_source_of_instance(source)
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
    scale_factor(source_item, [ratio_x, ratio_y, ratio_z])

    replace_item(item_to_insert=source_item,
                 item_to_remove=target,
                 item_to_remove_new_parent=get_tmp_folder(h3dc.TMP_FOLDER_NAME))


class Constraints:
    def __init__(self, mode, order, use_x, use_y, use_z):
        self.mode = mode
        self.order = order
        self.use_x = use_x
        self.use_y = use_y
        self.use_z = use_z


save_log = h3du.get_user_value(h3dc.USER_VAL_NAME_SAVE_LOG)
log_name = h3du.replace_file_ext(modo.Scene().name)
h3dd = H3dDebug(enable=save_log, file=log_name)
