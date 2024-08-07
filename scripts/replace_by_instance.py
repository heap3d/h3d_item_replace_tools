#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Replace Selected Items by an Instance with the Last Selected
# ================================

import modo
import modo.constants as c
import lx

from h3d_utilites.scripts.h3d_debug import H3dDebug
import h3d_utilites.scripts.h3d_utils as h3du

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc
from h3d_item_replace_tools.scripts.replace_items_tools import Constraints, item_instance_and_align


def main():
    h3dd.print_debug('\n\n----- replace_by_instance.py -----\n')
    h3dd.print_fn_in()
    print('')
    print('start...')

    scene = modo.Scene()
    selected = scene.selectedByType(c.LOCATOR_TYPE, superType=True)
    if not selected:
        print('None selected')
        return
    constraints = Constraints(
        mode=h3du.get_user_value(h3dc.USER_VAL_NAME_LOCK_XYZ),
        order=h3du.get_user_value(h3dc.USER_VAL_NAME_LOCK_XYZ_ORDER),
        use_x=h3du.get_user_value(h3dc.USER_VAL_NAME_SCALE_X),
        use_y=h3du.get_user_value(h3dc.USER_VAL_NAME_SCALE_Y),
        use_z=h3du.get_user_value(h3dc.USER_VAL_NAME_SCALE_Z)
    )
    # source are last selected item
    source = selected[-1]
    # targets are all but last
    target_candidates = selected[:-1]
    # skip selected group locators
    targets = filter(lambda i: i.type != h3du.itype_str(c.GROUPLOCATOR_TYPE), target_candidates)
    new_items: list[modo.Item] = []
    for target in targets:
        new_items.append(
            item_instance_and_align(source=source, target=target, do_instance=True, constraints=constraints)
            )

    lx.eval('select.type item')
    modo.Scene().deselect()
    for item in new_items:
        item.select()

    print('done.')
    h3dd.print_fn_out()


save_log = h3du.get_user_value(h3dc.USER_VAL_NAME_SAVE_LOG)
log_name = h3du.replace_file_ext(modo.Scene().name)
h3dd = H3dDebug(enable=save_log, file=log_name)

if __name__ == '__main__':
    main()
