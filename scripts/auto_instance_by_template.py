#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Calling command sequence:
#   Smart Set Item Center by Template
#   Replace Selected Items by an Instance with the Last Selected
# ================================

import lx
import modo
import modo.constants as c


def main():
    if not modo.scene.current().selectedByType(itype=c.MESH_TYPE):
        print('No mesh items selected')
        return
    # Smart Set Item Center by Template
    lx.eval('@{scripts/smart_set_center_by_template.py}')
    # Replace Selected Items by an Instance with the Last Selected
    lx.eval('@{scripts/replace_by_instance.py}')


if __name__ == '__main__':
    main()
