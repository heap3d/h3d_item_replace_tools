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
from h3d_kit_constants import *
from h3d_debug import h3dd
from h3d_utils import h3du


def get_selected_mesh():
    h3dd.print_fn_in()
    selected = scene.selectedByType(itype=c.MESH_TYPE)
    h3dd.print_fn_out()
    return selected[:1]


def main():
    h3dd.print_debug('\n\n----- get_mesh_template_stats.py -----\n')
    h3dd.print_fn_in()
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
        lx.eval('@{scripts/set_center_by_selected_polys.py}')

    print('done.')
    h3dd.print_fn_out()


if __name__ == '__main__':
    scene = modo.scene.current()
    main()
