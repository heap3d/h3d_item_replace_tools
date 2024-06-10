#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# set item center by largest polygon
# ================================

import modo
import modo.constants as c
import lx
import uuid

from h3d_utilites.scripts.h3d_debug import H3dDebug
import h3d_utilites.scripts.h3d_utils as h3du

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc
from h3d_item_replace_tools.scripts.find_matching_meshes import place_center_at_polygons
from h3d_item_replace_tools.scripts.get_polygons_operations import (
    get_polygons_find_by_largest,
    remove_item_selection_set,
)


def main():
    h3dd.print_debug('\n\n----- set_center_by_largest_poly.py -----\n')
    h3dd.print_fn_in()
    print('')
    print('start...')

    scene = modo.Scene()
    do_poly_triple = h3du.get_user_value(h3dc.USER_VAL_NAME_POLY_TRIPLE)
    selected_meshes = scene.selectedByType(itype=c.MESH_TYPE)
    set_uuid = str(uuid.uuid4())
    selection_set_name = '{} - {}'.format(h3dc.SELECTION_SET_BASE_NAME, set_uuid)

    for mesh in selected_meshes:
        center_polys = get_polygons_find_by_largest(mesh)
        # skip if mesh doesn't matches to template (returned index is -1)
        if not center_polys:
            continue
        # enter item mode and add matched mesh to selection set
        lx.eval('select.type item')
        lx.eval('select.editSet {{{}}} add item:{}'.format(selection_set_name, mesh.id))

        place_center_at_polygons(mesh, center_polys, do_poly_triple)

    # select processed meshes
    try:
        lx.eval('!select.useSet "{}" replace'.format(selection_set_name))
        remove_item_selection_set(selection_set_name)
    except RuntimeError:
        print('No meshes were processed.')
        print('Try to update template mesh info')

    print('done.')
    h3dd.print_fn_out()


save_log = h3du.get_user_value(h3dc.USER_VAL_NAME_SAVE_LOG)
log_name = h3du.replace_file_ext(modo.Scene().name)
h3dd = H3dDebug(enable=save_log, file=log_name)

if __name__ == '__main__':
    main()
