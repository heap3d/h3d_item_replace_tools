#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Calling command sequence:
#   Select the Largest Polygon
#   Expand Selection by Angle
#   Set Item Center to the Polygon Selection
#   Replace Selected Items by an Instance with the Last Selected
# ================================

import modo
import modo.constants as c
import lx


def main():
    if not modo.Scene().selectedByType(itype=c.MESH_TYPE):
        print('No mesh items selected')
        return
    # Select the Largest Polygon
    lx.eval('@{scripts/select_largest_poly.py}')
    # Expand Selection by Angle
    # replace custom script to modo native command
    # lx.eval('!@scripts/selectByAngle.py false')
    lx.eval('!@scripts/modo_polygonCoplanar.py')
    # Set Item Center to the Polygon Selection
    lx.eval('@{scripts/set_center_by_selected_polys.py}')
    # Replace Selected Items by an Instance with the Last Selected
    lx.eval('@{scripts/replace_by_instance.py}')


if __name__ == '__main__':
    main()
