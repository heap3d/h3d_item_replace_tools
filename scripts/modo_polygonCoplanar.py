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
import sys
import math

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_kit_constants import *
from h3d_utils import h3du


def main():
    poly_coplanar_angle = math.degrees(h3du.get_user_value(USER_VAL_NAME_COPLANAR_ANGLE))
    poly_coplanar_range = h3du.get_user_value(USER_VAL_NAME_COPLANAR_RANGE)

    lx.eval('tool.set select.polygonCoplanar on')
    # get previous tool values
    prev_angle = math.degrees(lx.eval('tool.attr tool:select.polygonCoplanar attr:angle value:?'))
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


if __name__ == '__main__':
    main()
