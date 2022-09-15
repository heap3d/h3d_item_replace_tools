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

import modo
import modo.constants as c
import lx

USER_VAL_NAME_TEMPLATE_MESH = 'h3d_pt_template_mesh'
USER_VAL_NAME_CENTER_IDX = 'h3d_pt_template_poly_center_idx'
USER_VAL_NAME_CENTER_AREA_PERC = 'h3d_pt_center_area_percent'
USER_VAL_NAME_AREA_THRESHOLD = 'h3d_pt_center_area_threshold'

scene = modo.scene.current()


def get_selected_mesh():
    selected = scene.selectedByType(itype=c.MESH_TYPE)
    return selected[:1]


def get_full_area(mesh):
    polygons = mesh.geometry.polygons

    full_area = sum([poly.area for poly in polygons])
    print('mesh:<{}>  full area:<{}>'.format(mesh.name, full_area))
    return full_area


def get_user_value(name):
    value = lx.eval('user.value {} ?'.format(name))
    return value


def set_user_value(name, value):
    lx.eval('user.value {} {{{}}}'.format(name, value))


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


def main():
    print('')
    print('start...')

    selected_mesh = get_selected_mesh()
    for test_mesh in selected_mesh[:1]:
        # todo get updated template info: boundary proportions, orientation, relative position of item center
        print('mesh:<{}>'.format(test_mesh))
        set_user_value(USER_VAL_NAME_TEMPLATE_MESH, test_mesh.name)
        selected_polys = test_mesh.geometry.polygons.selected

        if not selected_polys:
            print('mesh:<{}>  has no selected polygons'.format(test_mesh.name))
            continue

        center_poly = selected_polys[0]
        set_user_value(USER_VAL_NAME_CENTER_IDX, center_poly.index)
        full_area = get_full_area(test_mesh)
        percentage = center_poly.area / full_area
        print('center poly area:<{}>  full area:<{}>  percentage:<{}>'.format(
            center_poly.area, full_area, percentage))
        set_user_value(USER_VAL_NAME_CENTER_AREA_PERC, percentage)
        threshold = get_user_value(USER_VAL_NAME_AREA_THRESHOLD)
        margin_low = get_margin_low(percentage, threshold)
        margin_high = get_margin_high(percentage, threshold)
        print('percentage:<{}>  threshold:<{}>  margin low|high:<{}|{}>'.format(
            percentage, threshold, margin_low, margin_high))

    print('done.')


if __name__ == '__main__':
    main()
