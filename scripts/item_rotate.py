#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Rotate selected items by predefined angle using local center
# ================================

import modo
import modo.constants as c
import modo.mathutils as mmu

import h3d_utilites.scripts.h3d_utils as h3du

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc


def main():
    print('item_rotate.py: start...')
    # get current selection
    selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    # get rotation axis
    rotation_axis = h3du.get_user_value(h3dc.USER_VAL_NAME_ANGLE_AXIS)
    # get rotation angle
    rotation_angle = h3du.get_user_value(h3dc.USER_VAL_NAME_ANGLE_STEP)
    # construct degrees triple
    angle = {'X': 0, 'Y': 0, 'Z': 0}
    angle[rotation_axis] = rotation_angle
    for item in selected:
        h3du.item_rotate(item, mmu.Vector3(angle['X'], angle['Y'], angle['Z']))
    print('item_rotate.py: done.')


if __name__ == '__main__':
    main()
