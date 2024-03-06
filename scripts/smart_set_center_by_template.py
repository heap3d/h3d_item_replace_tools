#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Calling command sequence:
#   Smart Select Polygon by Template
#   Expand Selection by Angle
#   Set Item Center to the Polygon Selection
# ================================

import lx
import modo
import modo.constants as c


def main():
    if not modo.Scene().selectedByType(itype=c.MESH_TYPE):
        print('No mesh items selected')
        return
    # Smart Select Polygon by Template
    lx.eval('@{scripts/select_poly_by_template_Y_axis.py}')
    # Expand Selection by Angle
    lx.eval('!@scripts/modo_polygonCoplanar.py')
    # Set Item Center to the Polygon Selection
    lx.eval('@{scripts/set_center_by_selected_polys.py}')


if __name__ == '__main__':
    main()
