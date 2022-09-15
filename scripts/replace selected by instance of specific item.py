#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# replace selected by specific item instances
# how to use: select items to replace, add to selection source item to duplicate. Last selected item will be instanced
# over other selected items
# ================================

import modo
import modo.constants as c
import lx

USER_VAL_NAME_SCALE_X = 'h3d_pt_scale_x'
USER_VAL_NAME_SCALE_Y = 'h3d_pt_scale_y'
USER_VAL_NAME_SCALE_Z = 'h3d_pt_scale_z'
USER_VAL_NAME_LOCK_XYZ = 'h3d_pt_lock_xyz'
USER_VAL_NAME_LOCK_XYZ_ORDER = 'h3d_pt_lock_xyz_order'
TMP_FOLDER_NAME = 'h3d_pt_replaced_items_to_delete'

scene = modo.scene.current()


def get_size(item):
    if item.type != 'mesh' and item.type != 'meshInst':
        return [0.0, 0.0, 0.0]
    s_x, s_y, s_z = get_item_scale(item)
    if item.type == 'meshInst':
        corners = get_source_of_instance(item).geometry.boundingBox
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


def get_source_of_instance(item):
    if item is None:
        return None
    if not item.isAnInstance:
        return item

    item_source = item.itemGraph('source').forward(0)
    if item_source.isAnInstance:
        return get_source_of_instance(item_source)
    else:
        return item_source


def get_user_value(name):
    value = lx.eval('user.value {} ?'.format(name))
    return value


def replace_item(item_to_insert, item_to_remove, item_to_remove_new_parent):
    parent = item_to_remove.parent
    children = item_to_remove.children()
    if parent is not None:
        item_to_insert.select(replace=True)
        print('parent:<{}>,  children:<{}>,  item_to_insert:<{}>'.format(parent, children, item_to_insert))
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
        tmp_folder = scene.item(name)
    except LookupError:
        tmp_folder = scene.addItem(itype='groupLocator', name=name)
        tmp_folder.channel('visible').set('allOff')
        tmp_folder.select(replace=True)
        lx.eval('item.editorColor magenta')
    return tmp_folder


def get_item_scale(item):
    item.select(replace=True)
    x = lx.eval('transform.channel scl.X ?')
    y = lx.eval('transform.channel scl.Y ?')
    z = lx.eval('transform.channel scl.Z ?')
    return[x, y, z]


def set_item_scale(item, scale):
    item.select(replace=True)
    lx.eval('transform.channel scl.X {}'.format(scale[0]))
    lx.eval('transform.channel scl.Y {}'.format(scale[1]))
    lx.eval('transform.channel scl.Z {}'.format(scale[2]))


def item_align(source, target, do_instance, constraints):
    parent = target.parent
    print('target parent:<{}>'.format(parent))
    # get source size
    source_base = get_source_of_instance(source)
    print('source base:<{}>'.format(source_base))
    # get source scale
    sx, sy, sz = get_item_scale(source)
    print('source scale:<{}>'.format([sx, sy, sz]))
    # base size
    bx, by, bz = get_size(source_base)
    print('base scale:<{}>'.format([bx, by, bz]))
    # source_size = base_size * source.scale
    source_size = [bx * sx, by * sy, bz * sz]
    print('source scale:<{}>'.format(source_size))
    # get target size
    target_size = get_size(target)
    print('target size:<{}>'.format(target_size))
    if do_instance:
        print('make instance: do_instance<{}>'.format(do_instance))
        source_item = scene.duplicateItem(item=source_base, instance=True)
    else:
        print('do not make instance: do_instance<{}>'.format(do_instance))
        source_item = source
    source_item.setParent()
    scene.deselect()
    source_item.select()
    target.select()
    lx.eval('item.match item pos average:false item:{} itemTo:{}'.format(source_item.id, target.id))
    lx.eval('item.match item rot average:false item:{} itemTo:{}'.format(source_item.id, target.id))
    if do_instance:
        # initiate scale on instance
        source_item.select(replace=True)
        source_base.select()
        lx.eval('item.match item scl')
    # initiate visibility on instance
    source_item.select(replace=True)
    lx.eval('item.channel locator$visible default')
    # check if there any 0.0 in source_size or target_size
    if any([f == 0.0 for f in (source_size + target_size)]):
        ratio_x = 1
        ratio_y = 1
        ratio_z = 1
    else:
        ratio_x = target_size[0] / source_size[0]
        ratio_y = target_size[1] / source_size[1]
        ratio_z = target_size[2] / source_size[2]

    # determine which constraints is on
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
                 item_to_remove_new_parent=get_tmp_folder(TMP_FOLDER_NAME)
                 )


class Constraints:
    mode = get_user_value(USER_VAL_NAME_LOCK_XYZ)
    order = get_user_value(USER_VAL_NAME_LOCK_XYZ_ORDER)
    use_x = get_user_value(USER_VAL_NAME_SCALE_X)
    use_y = get_user_value(USER_VAL_NAME_SCALE_Y)
    use_z = get_user_value(USER_VAL_NAME_SCALE_Z)


def main():
    # todo replace void instances issue
    print('')
    print('start...')

    selected = scene.selectedByType(c.LOCATOR_TYPE, superType=True)
    if not selected:
        print('None selected')
        return

    do_instance = True
    if lx.args():
        for arg in lx.args():
            if arg == '-noinstance':
                do_instance = False

    constraints = Constraints()
    # source is last selected item
    source = selected[-1]
    if do_instance:
        # targets is all but last
        targets = selected[:-1]
    else:
        # targets is previous to last
        targets = selected[-2:-1]
    for target in targets:
        item_align(source, target, do_instance, constraints)

    source_mesh = get_source_of_instance(source)
    if source_mesh:
        source_mesh.select(replace=True)

    print('done.')


if __name__ == '__main__':
    main()
