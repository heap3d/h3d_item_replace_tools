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
import sys
import lx

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
import h3d_utils as h3du
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_kit_constants import *


def main():
    print('item_rotate.py: start...')
    # get current selection
    selected = modo.scene.current().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    # get rotation axis
    rotation_axis = h3du.get_user_value(USER_VAL_NAME_ANGLE_AXIS)
    # get rotation angle
    rotation_angle = h3du.get_user_value(USER_VAL_NAME_ANGLE_STEP)
    # construct degrees triple
    angle = {'X': 0, 'Y': 0, 'Z': 0}
    angle[rotation_axis] = rotation_angle
    for item in selected:
        h3du.item_rotate(item, mmu.Vector3(angle['X'], angle['Y'], angle['Z']))
    print('item_rotate.py: done.')


if __name__ == '__main__':
    main()
