#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# find a match between template and target meshes
# ================================

import modo
import modo.constants as c
import lx
import uuid

USER_VAL_NAME_TEMPLATE_MESH = 'h3d_pt_template_mesh'
USER_VAL_NAME_CENTER_IDX = 'h3d_pt_template_poly_center_idx'
USER_VAL_NAME_CENTER_AREA_PERC = 'h3d_pt_center_area_percent'
USER_VAL_NAME_AREA_THRESHOLD = 'h3d_pt_center_area_threshold'
USER_VAL_NAME_USE_LARGEST_POLY = 'h3d_pt_use_largest_poly'
SELECTION_SET_BASE_NAME = '$delete$ h3d place tools'

scene = modo.scene.current()


def get_user_value(name):
    value = lx.eval('user.value {} ?'.format(name))
    return value


def get_full_area(mesh):
    full_area = sum([poly.area for poly in mesh.geometry.polygons])
    return full_area


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
    polys = get_polygons_find_by_margins(mesh, threshold, margin_low, margin_high)
    return polys


def get_polygons_find_by_largest(mesh):
    # return matched polygon or [] if none
    if mesh is None:
        return []
    polys = get_polygons_find_by_margins(mesh=mesh, percentage=1.0, margin_low=0.0, margin_high=1.0)
    return polys


def get_polygons_find_by_margins(mesh, percentage, margin_low, margin_high):
    # return matched polygon or [] if none
    if mesh is None:
        return []
    min_difference = 1
    poly = []
    full_area = get_full_area(mesh)
    for polygon in mesh.geometry.polygons:
        poly_percentage = polygon.area / full_area
        if margin_low < poly_percentage < margin_high:
            difference = abs(percentage - poly_percentage)
            if difference < min_difference:
                min_difference = difference
                poly = polygon

    return [poly] if poly else []


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


def debug_exit(message):
    print(message)
    exit()


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
            place_center_at_polygons(mesh, center_polys)
            # todo get updated template info: boundary proportions, orientation, relative position of item center
            # todo get list of polygon candidates
            # todo check every for boundary proportions, orientation, relative position of the item center

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
    main()
