#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Replace Selected Item by Last Selected
# ================================

import sys
import modo
import modo.constants as c
import lx

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_debug import h3dd
from h3d_utils import h3du
from replace_items_tools import Constraints, item_align


def main():
    h3dd.print_debug('\n\n----- replace_by_item.py -----\n')
    h3dd.print_fn_in()
    print('')
    print('start...')

    scene = modo.scene.current()
    selected = scene.selectedByType(c.LOCATOR_TYPE, superType=True)
    if not selected:
        print('None selected')
        return
    constraints = Constraints()
    # source are last selected item
    source = selected[-1]
    # targets are previous to last
    targets = selected[-2:-1]
    for target in targets:
        item_align(source=source, target=target, do_instance=True, constraints=constraints)

    source_mesh = h3du.get_source_of_instance(source)
    if source_mesh:
        source_mesh.select(replace=True)

    print('done.')
    h3dd.print_fn_out()


if __name__ == '__main__':
    main()
