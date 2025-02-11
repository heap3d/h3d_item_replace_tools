#!/usr/bin/python
# ================================
# (C)2022-2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Rotate selected items by predefined angle using local center
# ================================

import modo.constants as c
from modo import Vector3, Scene

from h3d_utilites.scripts.h3d_utils import item_rotate, get_user_value

from h3d_item_replace_tools.scripts.h3d_kit_constants import USER_VAL_NAME_ANGLE_AXIS, USER_VAL_NAME_ANGLE_STEP


def main():
    selected = Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    rotation_axis = get_user_value(USER_VAL_NAME_ANGLE_AXIS)
    rotation_angle = get_user_value(USER_VAL_NAME_ANGLE_STEP)

    angle = {'X': 0, 'Y': 0, 'Z': 0}
    angle[rotation_axis] = rotation_angle
    for item in selected:
        item_rotate(item, Vector3(angle['X'], angle['Y'], angle['Z']))


if __name__ == '__main__':
    main()
