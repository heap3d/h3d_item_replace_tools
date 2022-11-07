#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# get_polygons_xxx() operations
# ================================

import sys
import lx

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_utils import h3du
from h3d_debug import h3dd, is_print_fn_debug


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
    h3dd.print_debug('mesh <{}>:<{}>; percentage <{}>; threshold <{}>'.format(mesh.name, mesh, percentage, threshold))
    h3dd.print_debug('margin_low <{}>; margin_high <{}>'.format(margin_low, margin_high))
    polys = get_polygons_find_by_margins(mesh, threshold, margin_low, margin_high, do_multipoly=True)
    h3dd.print_items(polys, 'polys:', is_print_fn_debug)
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

