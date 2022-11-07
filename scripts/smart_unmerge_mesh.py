#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# smart unmerge mesh command
# unmerging mesh islands to separate mesh items
# merging meshes within merge threshold
# aligning item center to the geometric center
# grouping similar meshes
# grouping equal meshes
# ================================

import sys
import lx
import modo
import modo.constants as c

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from kit_constants import *
from h3d_utils import h3du
from h3d_debug import h3dd, is_print_fn_debug
from mesh_islands_to_items import get_tmp_name, smart_unmerge, group_similar_items, group_equal_meshes, DetectOptions


def main():
    h3dd.print_debug('\n\n----- smart_unmerge_mesh.py -----\n', is_print_fn_debug)
    h3dd.print_fn_in(is_print_fn_debug)
    print('')
    print('start...')

    scene = modo.scene.current()
    largest_rot = h3du.get_user_value(USER_VAL_NAME_LARGEST_ROT)
    largest_pos = h3du.get_user_value(USER_VAL_NAME_LARGEST_POS)
    do_group_similar = h3du.get_user_value(USER_VAL_NAME_GROUP_SIMILAR)
    do_group_equal = h3du.get_user_value(USER_VAL_NAME_GROUP_EQUAL)
    merge_closest = h3du.get_user_value(USER_VAL_NAME_MERGE_CLOSEST)
    search_dist = h3du.get_user_value(USER_VAL_NAME_SEARCH_DIST)

    do_bb = modo.mathutils.Vector3()
    do_bb.x = h3du.get_user_value(USER_VAL_NAME_DO_BOUNDING_BOX_X)
    do_bb.y = h3du.get_user_value(USER_VAL_NAME_DO_BOUNDING_BOX_Y)
    do_bb.z = h3du.get_user_value(USER_VAL_NAME_DO_BOUNDING_BOX_Z)
    bb_thld = modo.mathutils.Vector3()
    bb_thld.x = h3du.get_user_value(USER_VAL_NAME_BB_THRESHOLD_X)
    bb_thld.y = h3du.get_user_value(USER_VAL_NAME_BB_THRESHOLD_Y)
    bb_thld.z = h3du.get_user_value(USER_VAL_NAME_BB_THRESHOLD_Z)

    do_ctr = modo.mathutils.Vector3()
    do_ctr.x = h3du.get_user_value(USER_VAL_NAME_DO_CENTER_POS_X)
    do_ctr.y = h3du.get_user_value(USER_VAL_NAME_DO_CENTER_POS_Y)
    do_ctr.z = h3du.get_user_value(USER_VAL_NAME_DO_CENTER_POS_Z)
    ctr_thld = modo.mathutils.Vector3()
    ctr_thld.x = h3du.get_user_value(USER_VAL_NAME_CENTER_THRESHOLD_X)
    ctr_thld.y = h3du.get_user_value(USER_VAL_NAME_CENTER_THRESHOLD_Y)
    ctr_thld.z = h3du.get_user_value(USER_VAL_NAME_CENTER_THRESHOLD_Z)

    do_com = modo.mathutils.Vector3()
    do_com.x = h3du.get_user_value(USER_VAL_NAME_DO_COM_POS_X)
    do_com.y = h3du.get_user_value(USER_VAL_NAME_DO_COM_POS_Y)
    do_com.z = h3du.get_user_value(USER_VAL_NAME_DO_COM_POS_Z)
    com_thld = modo.mathutils.Vector3()
    com_thld.x = h3du.get_user_value(USER_VAL_NAME_COM_THRESHOLD_X)
    com_thld.y = h3du.get_user_value(USER_VAL_NAME_COM_THRESHOLD_Y)
    com_thld.z = h3du.get_user_value(USER_VAL_NAME_COM_THRESHOLD_Z)

    do_vol = h3du.get_user_value(USER_VAL_NAME_DO_MESH_VOL)
    vol_thld = h3du.get_user_value(USER_VAL_NAME_VOL_THRESHOLD)

    detect_options = DetectOptions(do_bounding_box=do_bb,
                                   do_center_pos=do_ctr,
                                   do_com_pos=do_com,
                                   do_mesh_vol=do_vol,
                                   bb_threshold=bb_thld,
                                   center_threshold=ctr_thld,
                                   com_threshold=com_thld,
                                   vol_threshold=vol_thld)

    selected_meshes = scene.selectedByType(itype=c.MESH_TYPE)
    if not selected_meshes:
        h3dd.print_fn_out(is_print_fn_debug)
        return
    # create temp group folder
    tmp_grp = scene.addItem(itype=c.GROUPLOCATOR_TYPE, name=get_tmp_name(selected_meshes[0].name))
    h3dd.print_debug('selected_meshes <{}>; tmp_grp <{}>'.format(list(i.name for i in selected_meshes), tmp_grp.name),
                     is_print_fn_debug)
    h3du.parent_items_to(selected_meshes, tmp_grp)

    area_thld = h3du.get_user_value(USER_VAL_NAME_AREA_THRESHOLD)
    todo_meshes = smart_unmerge(
        meshes=selected_meshes,
        largest_rot=largest_rot,
        largest_pos=largest_pos,
        merge_closest=merge_closest,
        search_dist=search_dist,
        area_threshold=area_thld)

    # group similar meshes
    if do_group_similar:
        group_similar_items(todo_meshes, detect_options)
    # group equal meshes
    if do_group_equal:
        group_equal_meshes(todo_meshes, detect_options)

    # select processed meshes
    scene.deselect()
    for item in todo_meshes:
        item.select()

    print('done.')
    h3dd.print_fn_out(is_print_fn_debug)


if __name__ == '__main__':
    main()
