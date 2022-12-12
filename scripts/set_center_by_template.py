#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# set item center for the selected meshes by matching to template
# ================================

import sys
import modo
import modo.constants as c
import lx
import uuid

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
import h3d_utils as h3du
from h3d_debug import H3dDebug
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
import h3d_kit_constants as h3dc
from find_matching_meshes import get_similar_mesh_center_polys, place_center_at_polygons
from get_polygons_operations import get_polygons_find_by_percentage


def main():
    h3dd.print_debug('\n\n----- set_center_by_template.py -----\n')
    h3dd.print_fn_in()
    print('')
    print('start...')

    scene = modo.scene.current()
    # get user values from UI
    area_percentage = h3du.get_user_value(h3dc.USER_VAL_NAME_CENTER_AREA_PERC)
    area_threshold = h3du.get_user_value(h3dc.USER_VAL_NAME_AREA_THRESHOLD)
    do_poly_triple = h3du.get_user_value(h3dc.USER_VAL_NAME_POLY_TRIPLE)

    selected_meshes = scene.selectedByType(itype=c.MESH_TYPE)
    set_uuid = str(uuid.uuid4())
    selection_set_name = '{} - {}'.format(h3dc.SELECTION_SET_BASE_NAME, set_uuid)

    for mesh in selected_meshes:
        center_polys = get_polygons_find_by_percentage(mesh, area_percentage, area_threshold)
        # skip if mesh doesn't matches to template (returned index is -1)
        if not center_polys:
            continue
        # enter item mode and add matched mesh to selection set
        lx.eval('select.type item')
        lx.eval('select.editSet {{{}}} add item:{}'.format(selection_set_name, mesh.id))
        cmp_mesh = scene.item(h3du.get_user_value(h3dc.USER_VAL_NAME_TEMPLATE_MESH))
        filtered_polys = get_similar_mesh_center_polys(mesh, cmp_mesh, center_polys, do_poly_triple)
        place_center_at_polygons(mesh, filtered_polys, do_poly_triple)

    # select processed meshes
    try:
        lx.eval('!select.useSet "{}" replace'.format(selection_set_name))
    except RuntimeError:
        print('No meshes were processed.')
        print('Try to update template mesh info')

    print('done.')
    h3dd.print_fn_out()


save_log = h3du.get_user_value(h3dc.USER_VAL_NAME_SAVE_LOG)
log_name = h3du.replace_file_ext(modo.scene.current().name)
h3dd = H3dDebug(enable=save_log, file=log_name)

if __name__ == '__main__':
    main()
