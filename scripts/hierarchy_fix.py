#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# hierarchy fix
# fixing hierarchy for all items in the scene
# ================================

import modo
import modo.constants as c


def main():
    print('start...')

    items = modo.scene.current().items(itype=c.LOCATOR_TYPE, superType=True)
    for item in items:
        parent = item.parent
        if parent:
            children = parent.children()
            if item not in children:
                item.setParent(None)
                item.setParent(parent)

    print('done.')


if __name__ == '__main__':
    main()
