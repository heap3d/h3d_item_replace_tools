#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# enabling or disabling log to file

import sys
import lx

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_debug import h3dd
from h3d_utils import h3du
from h3d_kit_constants import *


def main():
    h3dd.enable = h3du.get_user_value(USER_VAL_NAME_SAVE_LOG)


if __name__ == '__main__':
    main()
