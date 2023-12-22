#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select polygons for selected meshes by matching to template
# ================================

import modo
import modo.constants as c
import lx
import uuid

from h3d_utilites.scripts.h3d_debug import H3dDebug
import h3d_utilites.scripts.h3d_utils as h3du

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc
from h3d_item_replace_tools.scripts.find_matching_meshes import get_similar_mesh_center_polys_Y_axis
from h3d_item_replace_tools.scripts.get_polygons_operations import get_polygons_find_by_percentage


def main():
    h3dd.print_debug('\n\n----- select_poly_by_template.py -----\n')
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
    matched_polys = []

    for mesh in selected_meshes:
        cmp_mesh = scene.item(h3du.get_user_value(h3dc.USER_VAL_NAME_TEMPLATE_MESH))
        h3dd.print_debug('cmp_mesh <{}>'.format(cmp_mesh.name))
        poly_candidates = get_polygons_find_by_percentage(mesh, area_percentage, area_threshold)
        h3dd.print_items(list(p.index for p in poly_candidates), message='poly_candidates:')

        # get polygons for modified detect options list using Y axis only
        center_polys = get_similar_mesh_center_polys_Y_axis(mesh, cmp_mesh, poly_candidates, do_poly_triple)

        h3dd.print_items(list(p.index for p in center_polys), message='center_polys:')
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


save_log = h3du.get_user_value(h3dc.USER_VAL_NAME_SAVE_LOG)
log_name = h3du.replace_file_ext(modo.scene.current().name)
h3dd = H3dDebug(enable=save_log, file=log_name)

if __name__ == '__main__':
    main()
