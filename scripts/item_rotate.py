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
from modo import Scene

from h3d_utilites.scripts.h3d_utils import get_user_value, item_rotate_local, Axis

from h3d_item_replace_tools.scripts.h3d_kit_constants import USER_VAL_NAME_ANGLE_AXIS, USER_VAL_NAME_ANGLE_STEP


def main():
    selected = Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    rotation_axis = get_user_value(USER_VAL_NAME_ANGLE_AXIS)
    print(rotation_axis)
    rotation_angle = get_user_value(USER_VAL_NAME_ANGLE_STEP)
    print(rotation_angle)

    axis = {
        0: Axis.X,
        1: Axis.Y,
        2: Axis.Z,
        'X': Axis.X,
        'Y': Axis.Y,
        'Z': Axis.Z,
    }

    for item in selected:
        item_rotate_local(item, rotation_angle, axis.get(rotation_axis, Axis.Y))


if __name__ == '__main__':
    main()
