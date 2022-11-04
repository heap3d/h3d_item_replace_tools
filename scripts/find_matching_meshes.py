#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# find a match between template and target meshes
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
from mesh_islands_to_items import is_mesh_similar, DetectOptions


def get_margin_low(percentage, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
    margin_low = percentage - threshold / 2.0
    if margin_low < 0.0:
        margin_low = 0.0
    h3dd.print_fn_out(is_print_fn_debug)
    return margin_low


def get_margin_high(percentage, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
    margin_high = percentage + threshold / 2.0
    if margin_high > 1.0:
        margin_high = 1.0
    h3dd.print_fn_out(is_print_fn_debug)
    return margin_high


def get_polygons_find_by_percentage(mesh, percentage, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
    # return matched polygon or [] if none
    if percentage <= 0.0:
        h3dd.print_fn_out(is_print_fn_debug)
        return []
    if threshold < 0.0:
        h3dd.print_fn_out(is_print_fn_debug)
        return []

    margin_low = get_margin_low(percentage, threshold)
    margin_high = get_margin_high(percentage, threshold)
    polys = get_polygons_find_by_margins(mesh, threshold, margin_low, margin_high, do_multipoly=True)
    h3dd.print_fn_out(is_print_fn_debug)
    return polys


def get_polygons_find_by_largest(mesh):
    h3dd.print_fn_in(is_print_fn_debug)
    # return matched polygon or [] if none
    if not mesh:
        h3dd.print_fn_out(is_print_fn_debug)
        return []
    polys = get_polygons_find_by_margins(mesh=mesh, percentage=1.0, margin_low=0.0, margin_high=1.0)
    h3dd.print_fn_out(is_print_fn_debug)
    return polys


def get_polygons_find_by_margins(mesh, percentage, margin_low, margin_high, do_multipoly=False):
    h3dd.print_fn_in(is_print_fn_debug)
    if not mesh:
        h3dd.print_fn_out(is_print_fn_debug)
        return []
    min_difference = 1
    polys = []
    full_area = h3du.get_full_mesh_area(mesh)
    for polygon in mesh.geometry.polygons:
        poly_percentage = polygon.area / full_area
        if margin_low < poly_percentage < margin_high:
            if do_multipoly:
                polys.append(polygon)
            else:
                difference = abs(percentage - poly_percentage)
                if difference < min_difference:
                    min_difference = difference
                    polys = [polygon]
    h3dd.print_fn_out(is_print_fn_debug)
    return polys


def get_polygons_find_by_selected(mesh, selected_polys):
    h3dd.print_fn_in(is_print_fn_debug)
    if not mesh:
        h3dd.print_fn_out(is_print_fn_debug)
        return []
    if not selected_polys:
        print('<{}>: No polygons selected'.format(mesh.name))
        h3dd.print_fn_out(is_print_fn_debug)
        return []
    h3dd.print_fn_out(is_print_fn_debug)
    return selected_polys


def place_center_at_polygons(mesh, polys):
    h3dd.print_fn_in(is_print_fn_debug)
    if not mesh:
        h3dd.print_fn_out(is_print_fn_debug)
        return
    if not polys:
        h3dd.print_fn_out(is_print_fn_debug)
        return

    parent = mesh.parent
    mesh.select(replace=True)
    lx.eval('item.editorColor darkgrey')
    # select center polygons
    lx.eval('select.type polygon')
    lx.eval('select.drop polygon')
    for poly in polys:
        poly.select()
    # create temporary polygons to correctly determine the center of the selection
    # copy
    lx.eval('copy')
    # paste
    lx.eval('paste')
    # triple
    lx.eval('poly.triple')
    # work plane fit to selected polygon
    lx.eval('workPlane.fitSelect')
    # delete temporary polygons
    lx.eval('delete')
    # create locator and align it to work plane grid
    lx.eval('select.type item')
    tmp_loc = scene.addItem(itype=c.LOCATOR_TYPE)
    tmp_loc.select(replace=True)
    lx.eval('item.matchWorkplane pos')
    lx.eval('item.matchWorkplane rot')
    # rotate locator 180 degrees around Z axis
    rot_x, rot_y, rot_z = tmp_loc.rotation.get(degrees=True)
    tmp_loc.rotation.set((rot_x, rot_y, rot_z + 180.0), degrees=True)
    # parent mesh to locator in place
    mesh.select(replace=True)
    tmp_loc.select()
    lx.eval('item.parent inPlace:1')
    # freeze transforms to reset center of the selected mesh
    mesh.select(replace=True)
    lx.eval('transform.freeze')
    # unparent in place
    lx.eval('item.parent parent:{{}} inPlace:1')
    # restore parenting
    if parent is not None:
        parent.select()
        lx.eval('item.parent inPlace:1')
    # delete locator
    tmp_loc.select(replace=True)
    lx.eval('item.delete')
    # reset work plane
    lx.eval('workPlane.reset')
    h3dd.print_fn_out(is_print_fn_debug)


def get_similar_mesh_center_polys(cur_mesh, cmp_mesh, center_polys):
    h3dd.print_fn_in(is_print_fn_debug)
    if not cur_mesh:
        h3dd.print_fn_out(is_print_fn_debug)
        return None
    if not center_polys:
        h3dd.print_fn_out(is_print_fn_debug)
        return None
    if cur_mesh.name == cmp_mesh.name:
        h3dd.print_fn_out(is_print_fn_debug)
        return [cur_mesh.geometry.polygons[h3du.get_user_value(USER_VAL_NAME_CENTER_IDX)]]
    for poly in center_polys:
        # duplicate mesh
        test_mesh = scene.duplicateItem(cur_mesh)
        test_mesh.name = '{} [{}]'.format(cur_mesh.name, poly.index)
        # select poly
        lx.eval('select.type polygon')
        lx.eval('select.drop polygon')
        test_polys = [(test_mesh.geometry.polygons[poly.index])]
        # set center to selected poly
        place_center_at_polygons(test_mesh, test_polys)
        # test if duplicated mesh similar to template mesh
        if is_mesh_similar(test_mesh, cmp_mesh, detect_options):
            scene.removeItems(test_mesh)
            h3dd.print_fn_out(is_print_fn_debug)
            return [poly]
        scene.removeItems(test_mesh)
    h3dd.print_fn_out(is_print_fn_debug)
    return []


def main():
    h3dd.print_debug('\n\n----- find_matching_meshes.py -----\n', is_print_fn_debug)
    h3dd.print_fn_in(is_print_fn_debug)
    print('')
    print('start...')

    # get user values from UI
    use_largest_poly_mode = h3du.get_user_value(USER_VAL_NAME_USE_LARGEST_POLY)
    area_percentage = h3du.get_user_value(USER_VAL_NAME_CENTER_AREA_PERC)
    area_threshold = h3du.get_user_value(USER_VAL_NAME_AREA_THRESHOLD)

    use_selected_polys_mode = False
    polygon_select_mode = False
    select_largest_polygon_mode = False

    print('lx.args:<{}>'.format(lx.args()))
    if lx.args():
        for arg in lx.args():
            print('command line argument: <{}>'.format(arg))
            if arg == '-largest':
                use_largest_poly_mode = True
                print('use_largest_poly:<{}>'.format(use_largest_poly_mode))
            if arg == '-selected':
                use_selected_polys_mode = True
                print('use_selected_poly:<{}>'.format(use_selected_polys_mode))
            if arg == '-polygon':
                polygon_select_mode = True
                print('polygon_select:<{}>'.format(polygon_select_mode))
            if arg == '-selectlargest':
                select_largest_polygon_mode = True
                print('select_largest_polygon:<{}>'.format(select_largest_polygon_mode))

    selected_meshes = scene.selectedByType(itype=c.MESH_TYPE)
    set_uuid = str(uuid.uuid4())
    selection_set_name = '{} - {}'.format(SELECTION_SET_BASE_NAME, set_uuid)
    selected_polys = {mesh.id: mesh.geometry.polygons.selected for mesh in selected_meshes}
    matched_polys = []
    for mesh in selected_meshes:
        if use_selected_polys_mode:
            center_polys = get_polygons_find_by_selected(mesh, selected_polys[mesh.id])
        elif use_largest_poly_mode:
            center_polys = get_polygons_find_by_largest(mesh)
        elif polygon_select_mode:
            cmp_mesh = scene.item(h3du.get_user_value(USER_VAL_NAME_TEMPLATE_MESH))
            h3dd.print_debug('cmp_mesh <{}>'.format(cmp_mesh.name), is_print_fn_debug)
            poly_candidates = get_polygons_find_by_percentage(mesh, area_percentage, area_threshold)
            h3dd.print_items(list(p.index for p in poly_candidates), message='poly_candidates:', enable=is_print_fn_debug)
            center_polys = get_similar_mesh_center_polys(mesh, cmp_mesh, poly_candidates)
            h3dd.print_items(list(p.index for p in center_polys), message='center_polys:', enable=is_print_fn_debug)
        elif select_largest_polygon_mode:
            center_polys = get_polygons_find_by_largest(mesh)
        else:
            center_polys = get_polygons_find_by_percentage(mesh, area_percentage, area_threshold)

        # skip if mesh doesn't matches to template (returned index is -1)
        if not center_polys:
            continue

        matched_polys += center_polys

        # enter item mode and add matched mesh to selection set
        lx.eval('select.type item')
        lx.eval('select.editSet {{{}}} add item:{}'.format(selection_set_name, mesh.id))

        if not (polygon_select_mode or select_largest_polygon_mode):
            filtered_polys = list(center_polys)
            if not (use_largest_poly_mode or use_selected_polys_mode):
                # check every for boundary box, center position, center of mass, mesh volume
                cmp_mesh = scene.item(h3du.get_user_value(USER_VAL_NAME_TEMPLATE_MESH))
                filtered_polys = get_similar_mesh_center_polys(mesh, cmp_mesh, center_polys)
            place_center_at_polygons(mesh, filtered_polys)

    # select processed meshes
    if not use_selected_polys_mode or any(selected_polys.values()):
        try:
            lx.eval('!select.useSet "{}" replace'.format(selection_set_name))
        except RuntimeError:
            print('No selection set found: <{}>'.format(selection_set_name))
            print('Try to update template mesh info')
            h3dd.exit('Action skipped.')
        if polygon_select_mode or select_largest_polygon_mode:
            lx.eval('select.type polygon')
            lx.eval('select.drop polygon')
            for polygon in matched_polys:
                polygon.select()

    print('done.')
    h3dd.print_fn_out(is_print_fn_debug)


if __name__ == '__main__':
    do_bb = modo.mathutils.Vector3()
    do_bb.x = h3du.get_user_value(USER_VAL_NAME_DO_BOUNDING_BOX_X)
    do_bb.y = h3du.get_user_value(USER_VAL_NAME_DO_BOUNDING_BOX_Y)
    do_bb.z = h3du.get_user_value(USER_VAL_NAME_DO_BOUNDING_BOX_Z)
    bb_thld = modo.mathutils.Vector3()
    bb_thld.x = h3du.get_user_value(USER_VAL_NAME_BB_THRESHOLD_X)
    bb_thld.y = h3du.get_user_value(USER_VAL_NAME_BB_THRESHOLD_Y)
    bb_thld.z = h3du.get_user_value(USER_VAL_NAME_BB_THRESHOLD_Z)

    do_ctr = modo.mathutils.Vector3()
    do_ctr.x = h3du.get_user_value(USER_VAL_NAME_DO_CENTER_POS_X)
    do_ctr.y = h3du.get_user_value(USER_VAL_NAME_DO_CENTER_POS_Y)
    do_ctr.z = h3du.get_user_value(USER_VAL_NAME_DO_CENTER_POS_Z)
    ctr_thld = modo.mathutils.Vector3()
    ctr_thld.x = h3du.get_user_value(USER_VAL_NAME_CENTER_THRESHOLD_X)
    ctr_thld.y = h3du.get_user_value(USER_VAL_NAME_CENTER_THRESHOLD_Y)
    ctr_thld.z = h3du.get_user_value(USER_VAL_NAME_CENTER_THRESHOLD_Z)

    do_com = modo.mathutils.Vector3()
    do_com.x = h3du.get_user_value(USER_VAL_NAME_DO_COM_POS_X)
    do_com.y = h3du.get_user_value(USER_VAL_NAME_DO_COM_POS_Y)
    do_com.z = h3du.get_user_value(USER_VAL_NAME_DO_COM_POS_Z)
    com_thld = modo.mathutils.Vector3()
    com_thld.x = h3du.get_user_value(USER_VAL_NAME_COM_THRESHOLD_X)
    com_thld.y = h3du.get_user_value(USER_VAL_NAME_COM_THRESHOLD_Y)
    com_thld.z = h3du.get_user_value(USER_VAL_NAME_COM_THRESHOLD_Z)

    do_vol = h3du.get_user_value(USER_VAL_NAME_DO_MESH_VOL)
    vol_thld = h3du.get_user_value(USER_VAL_NAME_VOL_THRESHOLD)

    detect_options = DetectOptions(do_bounding_box=do_bb,
                                   do_center_pos=do_ctr,
                                   do_com_pos=do_com,
                                   do_mesh_vol=do_vol,
                                   bb_threshold=bb_thld,
                                   center_threshold=ctr_thld,
                                   com_threshold=com_thld,
                                   vol_threshold=vol_thld)

    scene = modo.scene.current()

    main()
