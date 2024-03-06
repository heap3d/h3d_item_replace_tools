#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Set selected item as replace tools source
# ================================

import modo
import modo.constants as c

import h3d_utilites.scripts.h3d_utils as h3du

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc


def main():
    print('')
    print('set_source_item.py start...')

    selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    if not selected:
        modo.dialogs.alert('Set as Source error:', 'No item selected.')
        return
    if len(selected) > 1:
        print('Multiply items selected. Last selected will be used.')

    h3du.set_user_value(h3dc.USER_VAL_NAME_SOURCE_NAME, selected[-1].name)
    print('Source item is set to <{}>'.format(h3du.get_user_value(h3dc.USER_VAL_NAME_SOURCE_NAME)))

    print('set_source_item.py done.')


if __name__ == '__main__':
    main()
