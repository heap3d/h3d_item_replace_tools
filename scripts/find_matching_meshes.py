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
from h3d_utils import get_user_value, get_full_mesh_area
from mesh_islands_to_items import is_mesh_similar, DetectOptions


def get_margin_low(percentage, threshold):
    margin_low = percentage - threshold / 2.0
    if margin_low < 0.0:
        margin_low = 0.0
    return margin_low


def get_margin_high(percentage, threshold):
    margin_high = percentage + threshold / 2.0
    if margin_high > 1.0:
        margin_high = 1.0
    return margin_high


def get_polygons_find_by_percentage(mesh, percentage, threshold):
    # return matched polygon or [] if none
    if percentage <= 0.0:
        return []
    if threshold < 0.0:
        return []

    margin_low = get_margin_low(percentage, threshold)
    margin_high = get_margin_high(percentage, threshold)
    polys = get_polygons_find_by_margins(mesh, threshold, margin_low, margin_high, do_multipoly=True)
    return polys


def get_polygons_find_by_largest(mesh):
    # return matched polygon or [] if none
    if mesh is None:
        return []
    polys = get_polygons_find_by_margins(mesh=mesh, percentage=1.0, margin_low=0.0, margin_high=1.0)
    return polys


def get_polygons_find_by_margins(mesh, percentage, margin_low, margin_high, do_multipoly=False):
    if mesh is None:
        return []
    # print('mesh<{}>  percentage<{}>  low<{}>  high<{}>'.format(mesh.name, percentage, margin_low, margin_high))
    min_difference = 1
    polys = []
    full_area = get_full_mesh_area(mesh)
    for polygon in mesh.geometry.polygons:
        poly_percentage = polygon.area / full_area
        # print('poly index<{}>  poly percentage<{}>'.format(polygon.index, poly_percentage))
        if margin_low < poly_percentage < margin_high:
            if do_multipoly:
                polys.append(polygon)
            else:
                difference = abs(percentage - poly_percentage)
                if difference < min_difference:
                    min_difference = difference
                    polys = [polygon]
    print('get_polygons_find_by_margins():<{}>'.format(list(poly.index for poly in polys)))
    return polys


def get_polygons_find_by_selected(mesh, selected_polys):
    if mesh is None:
        print('mesh is None')
        return []
    if not selected_polys:
        print('No polygons selected')
        return []
    # return first selected polygon in mesh item
    print('mesh:<{}>  polygons:<{}>'.format(mesh.name, selected_polys))
    return selected_polys


def place_center_at_polygons(mesh, polys):
    if mesh is None:
        return
    if not polys:
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


def get_similar_mesh_center_polys(mesh, center_polys):
    # print('mesh<{}>  center_polys<{}>'.format(mesh, center_polys))
    if not mesh:
        return None
    if not center_polys:
        return None
    comp_mesh = scene.item(get_user_value(USER_VAL_NAME_TEMPLATE_MESH))
    for poly in center_polys:
        # duplicate mesh
        test_mesh = scene.duplicateItem(mesh)
        test_mesh.name = 'TEST'
        # select poly
        lx.eval('select.type polygon')
        lx.eval('select.drop polygon')
        test_polys = [(test_mesh.geometry.polygons[poly.index])]
        # set center to selected poly
        place_center_at_polygons(test_mesh, test_polys)
        # test if duplicated mesh similar to template mesh
        if is_mesh_similar(test_mesh, comp_mesh, detect_options):
            scene.removeItems(test_mesh)
            return [poly]
        scene.removeItems(test_mesh)
    return []


def main():
    print('')
    print('start...')

    # get user values from UI
    use_largest_poly = get_user_value(USER_VAL_NAME_USE_LARGEST_POLY)
    area_percentage = get_user_value(USER_VAL_NAME_CENTER_AREA_PERC)
    area_threshold = get_user_value(USER_VAL_NAME_AREA_THRESHOLD)

    use_selected_polys = False
    polygon_select = False
    select_largest_polygon = False

    print('lx.args:<{}>'.format(lx.args()))
    if lx.args():
        for arg in lx.args():
            print('command line argument: <{}>'.format(arg))
            if arg == '-largest':
                use_largest_poly = True
                print('use_largest_poly:<{}>'.format(use_largest_poly))
            if arg == '-selected':
                use_selected_polys = True
                print('use_selected_poly:<{}>'.format(use_selected_polys))
            if arg == '-polygon':
                polygon_select = True
                print('polygon_select:<{}>'.format(polygon_select))
            if arg == '-selectlargest':
                select_largest_polygon = True
                print('select_largest_polygon:<{}>'.format(select_largest_polygon))

    selected_meshes = scene.selectedByType(itype=c.MESH_TYPE)
    set_uuid = str(uuid.uuid4())
    selection_set_name = '{} - {}'.format(SELECTION_SET_BASE_NAME, set_uuid)
    selected_polys = {mesh.id: mesh.geometry.polygons.selected for mesh in selected_meshes}
    matched_polys = []
    for mesh in selected_meshes:
        if use_selected_polys:
            center_polys = get_polygons_find_by_selected(mesh, selected_polys[mesh.id])
        elif use_largest_poly:
            center_polys = get_polygons_find_by_largest(mesh)
        elif polygon_select:
            center_polys = get_polygons_find_by_percentage(mesh, area_percentage, area_threshold)
        elif select_largest_polygon:
            center_polys = get_polygons_find_by_largest(mesh)
        else:
            # print('using find by percentage call')
            center_polys = get_polygons_find_by_percentage(mesh, area_percentage, area_threshold)

        # skip if mesh doesn't matches to template (returned index is -1)
        if not center_polys:
            # print('mesh doesn\'t match')
            continue

        matched_polys += center_polys

        # enter item mode and add matched mesh to selection set
        lx.eval('select.type item')
        lx.eval('select.editSet {{{}}} add item:{}'.format(selection_set_name, mesh.id))

        if not (polygon_select or select_largest_polygon):
            filtered_polys = list(center_polys)
            if not (use_largest_poly or use_selected_polys):
                # check every for boundary box, center position, center of mass, mesh volume
                filtered_polys = get_similar_mesh_center_polys(mesh, center_polys)
                print('center polys <{}>  filtered polys<{}>'.format(center_polys, filtered_polys))
            place_center_at_polygons(mesh, filtered_polys)

    # select processed meshes
    if not use_selected_polys or any(selected_polys.values()):
        lx.eval('select.useSet "{}" replace'.format(selection_set_name))
        if polygon_select or select_largest_polygon:
            lx.eval('select.type polygon')
            lx.eval('select.drop polygon')
            for polygon in matched_polys:
                polygon.select()

    print('done.')


if __name__ == '__main__':
    do_bb = get_user_value(USER_VAL_NAME_DO_BOUNDING_BOX)
    do_ctr = get_user_value(USER_VAL_NAME_DO_CENTER_POS)
    do_com = get_user_value(USER_VAL_NAME_DO_COM_POS)
    do_vol = get_user_value(USER_VAL_NAME_DO_MESH_VOL)
    bb_thld = get_user_value(USER_VAL_NAME_BB_THRESHOLD)
    ctr_thld = get_user_value(USER_VAL_NAME_CENTER_THRESHOLD)
    com_thld = get_user_value(USER_VAL_NAME_COM_THRESHOLD)
    vol_thld = get_user_value(USER_VAL_NAME_VOL_THRESHOLD)

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
