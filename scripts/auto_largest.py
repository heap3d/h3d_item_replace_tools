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
    selected = scene.selectedByType(itype=c.MESH_TYPE)
    if not selected:
        print('No mesh items selected')
        return
    # Select the Largest Polygon
    lx.eval('@{scripts/select_largest_poly.py}')
    # Expand Selection by Angle
    lx.eval('!@scripts/selectByAngle.py false')
    # Set Item Center to the Polygon Selection
    lx.eval('@{scripts/set_center_by_selected_polys.py}')
    # Replace Selected Items by an Instance with the Last Selected
    lx.eval('@{scripts/replace_by_instance.py}')


if __name__ == '__main__':
    scene = modo.scene.current()
    main()
