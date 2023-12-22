#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# simple unmerge mesh command
# unmerging mesh islands to separate mesh items
# aligning item center to the geometric center
# grouping similar meshes
# grouping equal meshes
# ================================

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_debug import H3dDebug
import h3d_utilites.scripts.h3d_utils as h3du

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc
from h3d_item_replace_tools.scripts.mesh_islands_to_items import (
    get_tmp_name,
    simple_unmerge,
    group_similar_items,
    group_equal_meshes,
    DetectOptions
)


def main():
    h3dd.print_debug('\n\n----- simple_unmerge_mesh.py -----\n')
    h3dd.print_fn_in()
    print('')
    print('start simple_unmerge_mesh.py...')

    scene = modo.scene.current()
    largest_rot = h3du.get_user_value(h3dc.USER_VAL_NAME_LARGEST_ROT)
    largest_pos = h3du.get_user_value(h3dc.USER_VAL_NAME_LARGEST_POS)
    do_group_similar = h3du.get_user_value(h3dc.USER_VAL_NAME_GROUP_SIMILAR)
    do_group_equal = h3du.get_user_value(h3dc.USER_VAL_NAME_GROUP_EQUAL)

    do_bb = modo.mathutils.Vector3()
    do_bb.x = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_BOUNDING_BOX_X)
    do_bb.y = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_BOUNDING_BOX_Y)
    do_bb.z = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_BOUNDING_BOX_Z)
    bb_thld = modo.mathutils.Vector3()
    bb_thld.x = h3du.get_user_value(h3dc.USER_VAL_NAME_BB_THRESHOLD_X)
    bb_thld.y = h3du.get_user_value(h3dc.USER_VAL_NAME_BB_THRESHOLD_Y)
    bb_thld.z = h3du.get_user_value(h3dc.USER_VAL_NAME_BB_THRESHOLD_Z)

    do_ctr = modo.mathutils.Vector3()
    do_ctr.x = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_CENTER_POS_X)
    do_ctr.y = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_CENTER_POS_Y)
    do_ctr.z = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_CENTER_POS_Z)
    ctr_thld = modo.mathutils.Vector3()
    ctr_thld.x = h3du.get_user_value(h3dc.USER_VAL_NAME_CENTER_THRESHOLD_X)
    ctr_thld.y = h3du.get_user_value(h3dc.USER_VAL_NAME_CENTER_THRESHOLD_Y)
    ctr_thld.z = h3du.get_user_value(h3dc.USER_VAL_NAME_CENTER_THRESHOLD_Z)

    do_com = modo.mathutils.Vector3()
    do_com.x = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_COM_POS_X)
    do_com.y = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_COM_POS_Y)
    do_com.z = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_COM_POS_Z)
    com_thld = modo.mathutils.Vector3()
    com_thld.x = h3du.get_user_value(h3dc.USER_VAL_NAME_COM_THRESHOLD_X)
    com_thld.y = h3du.get_user_value(h3dc.USER_VAL_NAME_COM_THRESHOLD_Y)
    com_thld.z = h3du.get_user_value(h3dc.USER_VAL_NAME_COM_THRESHOLD_Z)

    do_vol = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_MESH_VOL)
    vol_thld = h3du.get_user_value(h3dc.USER_VAL_NAME_VOL_THRESHOLD)

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
        print('No meshes selected.\ndone.')
        h3dd.print_fn_out()
        return
    # create temp group folder
    tmp_grp = scene.addItem(itype=c.GROUPLOCATOR_TYPE, name=get_tmp_name(selected_meshes[0].name))
    h3dd.print_debug('selected_meshes <{}>; tmp_grp <{}>'.format(list(i.name for i in selected_meshes), tmp_grp.name))
    h3du.parent_items_to(selected_meshes, tmp_grp)

    todo_meshes = simple_unmerge(meshes=selected_meshes, largest_rot=largest_rot, largest_pos=largest_pos)
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
    h3dd.print_fn_out()


save_log = h3du.get_user_value(h3dc.USER_VAL_NAME_SAVE_LOG)
log_name = h3du.replace_file_ext(modo.scene.current().name)
h3dd = H3dDebug(enable=save_log, file=log_name)

if __name__ == '__main__':
    main()
