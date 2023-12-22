#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Replace Selected Item by Source Item
# ================================

import lx
import modo
import modo.constants as c

import h3d_utilites.scripts.h3d_utils as h3du

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc


def main():
    print('')
    print('replace_by_source.py start...')

    selection = modo.scene.current().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    if not selection:
        modo.dialogs.alert('Replace with Source error:', 'No items selected.')
        return
    # add source to selection
    try:
        source_item = modo.scene.current().item(h3du.get_user_value(h3dc.USER_VAL_NAME_SOURCE_NAME))
    except LookupError:
        modo.dialogs.alert('Replace with Source error:',
                           '<{}> source item not found.'.format(h3du.get_user_value(h3dc.USER_VAL_NAME_SOURCE_NAME)))
        return
    # add source item to selection
    source_item.select()

    # run replace by last selected
    lx.eval('@{scripts/replace_by_item.py}')

    print('replace_by_source.py done.')


if __name__ == '__main__':
    main()
