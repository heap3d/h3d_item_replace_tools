#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Replace Selected Items by an Instance with the Last Selected
# ================================

import sys
import modo
import modo.constants as c
import lx

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_debug import h3dd, is_print_fn_debug
from h3d_utils import h3du
from replace_items_tools import Constraints, item_align


def main():
    h3dd.print_debug('\n\n----- replace_by_instance.py -----\n', is_print_fn_debug)
    h3dd.print_fn_in(is_print_fn_debug)
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
    # targets are all but last
    targets = selected[:-1]
    for target in targets:
        item_align(source=source, target=target, do_instance=True, constraints=constraints)

    source_mesh = h3du.get_source_of_instance(source)
    if source_mesh:
        source_mesh.select(replace=True)

    print('done.')
    h3dd.print_fn_out(is_print_fn_debug)


if __name__ == '__main__':
    main()
