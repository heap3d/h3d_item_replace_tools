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

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
from h3d_debug import H3dDebug
import h3d_utils as h3du
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from replace_items_tools import Constraints, item_align
from h3d_kit_constants import *


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
    constraints = Constraints(
        mode=h3du.get_user_value(USER_VAL_NAME_LOCK_XYZ),
        order=h3du.get_user_value(USER_VAL_NAME_LOCK_XYZ_ORDER),
        use_x=h3du.get_user_value(USER_VAL_NAME_SCALE_X),
        use_y=h3du.get_user_value(USER_VAL_NAME_SCALE_Y),
        use_z=h3du.get_user_value(USER_VAL_NAME_SCALE_Z)
    )
    # source are last selected item
    source = selected[-1]
    # targets are previous to last
    targets = selected[-2:-1]
    for target in targets:
        item_align(source=source, target=target, do_instance=False, constraints=constraints)

    source_mesh = h3du.get_source_of_instance(source)
    if source_mesh:
        source_mesh.select(replace=True)

    print('done.')
    h3dd.print_fn_out()


save_log = h3du.get_user_value(USER_VAL_NAME_SAVE_LOG)
log_name = h3du.replace_file_ext(modo.scene.current().name)
h3dd = H3dDebug(enable=save_log, file=log_name)

if __name__ == '__main__':
    main()
