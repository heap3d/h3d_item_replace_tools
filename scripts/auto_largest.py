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

scene = modo.scene.current()


def main():
    selected = scene.selectedByType(itype=c.MESH_TYPE)
    if not selected:
        print('No mesh items selected')
        return
    # Select the Largest Polygon
    lx.eval('@{scripts/find matching meshes.py} -selectlargest')
    # Expand Selection by Angle
    lx.eval('@scripts/selectByAngle.py false')
    # Set Item Center to the Polygon Selection
    lx.eval('@{scripts/find matching meshes.py} -selected')
    # Replace Selected Items by an Instance with the Last Selected
    lx.eval('@{scripts/replace selected by instance of specific item.py}')


if __name__ == '__main__':
    main()
