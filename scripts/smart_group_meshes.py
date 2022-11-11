#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# smart group meshes command
# grouping similar meshes
# grouping equal meshes

import sys
import lx
import modo
import modo.constants as c

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_kit_constants import *
from h3d_utils import h3du
from h3d_debug import h3dd
from mesh_islands_to_items import group_similar_items, group_equal_meshes, DetectOptions


def main():
    h3dd.print_debug('\n\n----- smart_group_meshes.py -----\n')
    h3dd.print_fn_in()
    print('')
    print('start...')

    scene = modo.scene.current()
    do_group_equal = h3du.get_user_value(USER_VAL_NAME_GROUP_EQUAL)

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

    # group similar meshes
    group_similar_items(selected_meshes, detect_options)
    # group equal meshes
    if do_group_equal:
        group_equal_meshes(selected_meshes, detect_options)

    # restore initial selection
    scene.deselect()
    for item in selected_meshes:
        item.select()

    print('done.')
    h3dd.print_fn_out()


if __name__ == '__main__':
    main()
