#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# select polygons for selected meshes by matching to template
# ================================

import sys
import modo
import modo.constants as c
import lx
import uuid

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from kit_constants import *
from h3d_utils import h3du
from h3d_debug import h3dd, is_print_fn_debug
from find_matching_meshes import get_similar_mesh_center_polys
from get_polygons_operations import get_polygons_find_by_percentage


def main():
    h3dd.print_debug('\n\n----- select_poly_by_template.py -----\n', is_print_fn_debug)
    h3dd.print_fn_in(is_print_fn_debug)
    print('')
    print('start...')

    scene = modo.scene.current()
    # get user values from UI
    area_percentage = h3du.get_user_value(USER_VAL_NAME_CENTER_AREA_PERC)
    area_threshold = h3du.get_user_value(USER_VAL_NAME_AREA_THRESHOLD)

    selected_meshes = scene.selectedByType(itype=c.MESH_TYPE)
    set_uuid = str(uuid.uuid4())
    selection_set_name = '{} - {}'.format(SELECTION_SET_BASE_NAME, set_uuid)
    matched_polys = []

    for mesh in selected_meshes:
        cmp_mesh = scene.item(h3du.get_user_value(USER_VAL_NAME_TEMPLATE_MESH))
        h3dd.print_debug('cmp_mesh <{}>'.format(cmp_mesh.name), is_print_fn_debug)
        poly_candidates = get_polygons_find_by_percentage(mesh, area_percentage, area_threshold)
        h3dd.print_items(list(p.index for p in poly_candidates), message='poly_candidates:', enable=is_print_fn_debug)

        # get polygons for full detect options list
        center_polys = get_similar_mesh_center_polys(mesh, cmp_mesh, poly_candidates)

        h3dd.print_items(list(p.index for p in center_polys), message='center_polys:', enable=is_print_fn_debug)
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
    h3dd.print_fn_out(is_print_fn_debug)


if __name__ == '__main__':
    main()
