#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# resetting log file with current modo scene name
import sys
import lx
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_debug import h3dd


def main():
    h3dd.reset_log()


if __name__ == '__main__':
    main()
