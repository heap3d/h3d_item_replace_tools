#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# h3d utilites
# v1.0

import lx
import modo


def debug_exit(message):
    print('debug exit')
    print(message)
    exit()


def print_items(items, message=None):
    if message:
        print(message)
    if not items:
        print(items)
        return
    for i in items:
        if 'modo.item.' in str(type(i)):
            print('  <{}>'.format(i.name))
        else:
            print('  <{}>'.format(i))


def get_user_value(name):
    value = lx.eval('user.value {} ?'.format(name))
    return value


def parent_items_to(items, parent):
    # clear selection
    modo.Scene().deselect()
    # select items
    for item in items:
        item.select()
    # select parent item
    parent.select()
    # parent items to parent item
    lx.eval('item.parent inPlace:1')


def set_mesh_debug_info(mesh, info_str):
    if not mesh:
        return

    mesh.select(replace=True)
    lx.eval('item.tagAdd DESC')
    lx.eval('item.tag string DESC "{}"'.format(info_str))


def get_mesh_debug_info(mesh):
    if not mesh:
        return None

    mesh.select(replace=True)
    return lx.eval('item.tag string DESC ?')


def get_full_mesh_area(mesh):
    if not mesh:
        return None

    full_area = sum([poly.area for poly in mesh.geometry.polygons])
    return full_area


def debug_print(*args, **kwargs):
    enable = True
    sep = ' '
    if 'enable' in kwargs:
        enable = kwargs['enable']
    if 'sep' in kwargs:
        sep = kwargs['sep']
    if not enable:
        return

    print(sep.join(map(str, args)))


