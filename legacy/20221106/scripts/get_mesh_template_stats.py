#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# get statistics from selected CAD mesh template
# to use with place center by template tool
# ================================
import sys
import modo
import modo.constants as c
import lx
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from kit_constants import *
from h3d_debug import h3dd, is_print_fn_debug
from h3d_utils import h3du


def get_selected_mesh():
    h3dd.print_fn_in(is_print_fn_debug)
    selected = scene.selectedByType(itype=c.MESH_TYPE)
    h3dd.print_fn_out(is_print_fn_debug)
    return selected[:1]


def main():
    h3dd.print_debug('\n\n----- get_mesh_template_stats.py -----\n', is_print_fn_debug)
    h3dd.print_fn_in(is_print_fn_debug)
    print('')
    print('start...')

    selected_mesh = get_selected_mesh()
    for test_mesh in selected_mesh[:1]:
        h3du.set_user_value(USER_VAL_NAME_TEMPLATE_MESH, test_mesh.name)
        selected_polys = test_mesh.geometry.polygons.selected

        if not selected_polys:
            print('mesh:<{}>  has no selected polygons'.format(test_mesh.name))
            continue

        center_poly = selected_polys[0]
        h3du.set_user_value(USER_VAL_NAME_CENTER_IDX, center_poly.index)
        full_area = h3du.get_full_mesh_area(test_mesh)
        percentage = center_poly.area / full_area
        h3du.set_user_value(USER_VAL_NAME_CENTER_AREA_PERC, percentage)
        lx.eval('@{scripts/find_matching_meshes.py} -selected')

    print('done.')
    h3dd.print_fn_out(is_print_fn_debug)


if __name__ == '__main__':
    scene = modo.scene.current()
    main()
