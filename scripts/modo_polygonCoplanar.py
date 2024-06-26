#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Expand Selection by Angle using the modo's native command
# ================================

import lx
import math
import modo

from h3d_utilites.scripts.h3d_debug import H3dDebug
import h3d_utilites.scripts.h3d_utils as h3du

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc


def main():
    poly_coplanar_angle = math.degrees(h3du.get_user_value(h3dc.USER_VAL_NAME_COPLANAR_ANGLE))
    poly_coplanar_range = h3du.get_user_value(h3dc.USER_VAL_NAME_COPLANAR_RANGE)

    lx.eval('tool.set select.polygonCoplanar on')
    # get previous tool values
    prev_angle = math.degrees(lx.eval('tool.attr tool:select.polygonCoplanar attr:angle value:?'))  # type: ignore
    prev_range = lx.eval('tool.attr tool:select.polygonCoplanar attr:range value:?')
    prev_connect = lx.eval('tool.attr tool:select.polygonCoplanar attr:connect value:?')
    # expand selection
    lx.eval('tool.setAttr select.polygonCoplanar angle {}'.format(poly_coplanar_angle))
    lx.eval('tool.setAttr select.polygonCoplanar range {}'.format(poly_coplanar_range))
    lx.eval('tool.attr select.polygonCoplanar connect polygon')
    lx.eval('tool.doApply')
    lx.eval('tool.set select.polygonCoplanar off 0')
    # restore previous values
    lx.eval('tool.set select.polygonCoplanar on')
    lx.eval('tool.setAttr select.polygonCoplanar angle {}'.format(prev_angle))
    lx.eval('tool.setAttr select.polygonCoplanar range {}'.format(prev_range))
    lx.eval('tool.attr select.polygonCoplanar connect {}'.format(prev_connect))
    lx.eval('tool.set select.polygonCoplanar off 0')


save_log = h3du.get_user_value(h3dc.USER_VAL_NAME_SAVE_LOG)
log_name = h3du.replace_file_ext(modo.Scene().name)
h3dd = H3dDebug(enable=save_log, file=log_name)

if __name__ == '__main__':
    main()
