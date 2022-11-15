#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select largest polygon in selected mesh
# ================================

import sys
import modo
import modo.constants as c
import lx
import uuid

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
from h3d_debug import H3dDebug
from h3d_utils import H3dUtils
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_kit_constants import *
from get_polygons_operations import get_polygons_find_by_largest


def main():
    h3dd.print_debug('\n\n----- select_largest_poly.py -----\n')
    h3dd.print_fn_in()
    print('')
    print('start...')

    scene = modo.scene.current()

    selected_meshes = scene.selectedByType(itype=c.MESH_TYPE)
    set_uuid = str(uuid.uuid4())
    selection_set_name = '{} - {}'.format(SELECTION_SET_BASE_NAME, set_uuid)

    matched_polys = []

    for mesh in selected_meshes:
        center_polys = get_polygons_find_by_largest(mesh)
        # skip if mesh doesn't matches to template (returned index is -1)
        if not center_polys:
            continue
        # add matched polygons to collection
        matched_polys += center_polys
        # enter item mode and add matched mesh to selection set
        lx.eval('select.type item')
        lx.eval('select.editSet {{{}}} add item:{}'.format(selection_set_name, mesh.id))

    # select processed meshes
    try:
        lx.eval('!select.useSet "{}" replace'.format(selection_set_name))
    except RuntimeError:
        print('No meshes were processed.')
        print('Try to update template mesh info')
    # select matched polygons
    lx.eval('select.type polygon')
    lx.eval('select.drop polygon')
    for polygon in matched_polys:
        polygon.select()

    print('done.')
    h3dd.print_fn_out()


h3du = H3dUtils()
save_log = h3du.get_user_value(USER_VAL_NAME_SAVE_LOG)
log_name = h3du.replace_file_ext(modo.scene.current().name)
h3dd = H3dDebug(enable=save_log, file=log_name)

if __name__ == '__main__':
    main()
