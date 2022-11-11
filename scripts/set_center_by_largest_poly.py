#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# set item center by largest polygon
# ================================

import sys
import modo
import modo.constants as c
import lx
import uuid

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_kit_constants import *
from h3d_debug import h3dd
from find_matching_meshes import place_center_at_polygons
from get_polygons_operations import get_polygons_find_by_largest


def main():
    h3dd.print_debug('\n\n----- set_center_by_largest_poly.py -----\n')
    h3dd.print_fn_in()
    print('')
    print('start...')

    scene = modo.scene.current()
    selected_meshes = scene.selectedByType(itype=c.MESH_TYPE)
    set_uuid = str(uuid.uuid4())
    selection_set_name = '{} - {}'.format(SELECTION_SET_BASE_NAME, set_uuid)

    for mesh in selected_meshes:
        center_polys = get_polygons_find_by_largest(mesh)
        # skip if mesh doesn't matches to template (returned index is -1)
        if not center_polys:
            continue
        # enter item mode and add matched mesh to selection set
        lx.eval('select.type item')
        lx.eval('select.editSet {{{}}} add item:{}'.format(selection_set_name, mesh.id))

        place_center_at_polygons(mesh, center_polys)

    # select processed meshes
    try:
        lx.eval('!select.useSet "{}" replace'.format(selection_set_name))
    except RuntimeError:
        print('No meshes were processed.')
        print('Try to update template mesh info')

    print('done.')
    h3dd.print_fn_out()


if __name__ == '__main__':
    main()
