#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# find a match between template and target meshes
# ================================

import copy
import sys
import modo
import modo.constants as c
import lx

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
import h3d_utils as h3du
from h3d_debug import H3dDebug
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
import h3d_kit_constants as h3dc
from mesh_islands_to_items import is_mesh_similar, DetectOptions


def place_center_at_polygons(mesh, polys, do_poly_triple):
    h3dd.print_fn_in()
    if not mesh:
        h3dd.print_fn_out()
        return
    if not polys:
        h3dd.print_fn_out()
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
    # enable select on paste

    # copy
    lx.eval('copy')
    # paste
    lx.eval('paste')
    # triple
    if do_poly_triple:
        lx.eval('poly.triple')
    # work plane fit to selected polygon
    lx.eval('workPlane.fitSelect')
    # delete temporary polygons
    lx.eval('delete')
    # create locator and align it to work plane grid
    lx.eval('select.type item')
    tmp_loc = modo.scene.current().addItem(itype=c.LOCATOR_TYPE)
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
    h3dd.print_fn_out()


def get_similar_mesh_center_polys(cur_mesh, cmp_mesh, center_polys, do_poly_triple):
    h3dd.print_fn_in()
    if not cur_mesh:
        h3dd.print_fn_out()
        return []
    if not center_polys:
        h3dd.print_fn_out()
        return []
    if cur_mesh.name == cmp_mesh.name:
        h3dd.print_fn_out()
        return [cur_mesh.geometry.polygons[h3du.get_user_value(h3dc.USER_VAL_NAME_CENTER_IDX)]]
    for poly in center_polys:
        # duplicate mesh
        test_mesh = modo.scene.current().duplicateItem(cur_mesh)
        test_mesh.name = '{} [{}]'.format(cur_mesh.name, poly.index)
        # select poly
        lx.eval('select.type polygon')
        lx.eval('select.drop polygon')
        test_polys = [(test_mesh.geometry.polygons[poly.index])]
        # set center to selected poly
        place_center_at_polygons(test_mesh, test_polys, do_poly_triple)
        # test if duplicated mesh similar to template mesh
        if is_mesh_similar(test_mesh, cmp_mesh, detect_options):
            modo.scene.current().removeItems(test_mesh)
            h3dd.print_fn_out()
            return [poly]
        modo.scene.current().removeItems(test_mesh)
    h3dd.print_fn_out()
    return []


def get_similar_mesh_center_polys_Y_axis(cur_mesh, cmp_mesh, center_polys, do_poly_triple):
    h3dd.print_fn_in()
    if not cur_mesh:
        h3dd.print_fn_out()
        return []
    if not center_polys:
        h3dd.print_fn_out()
        return []
    if cur_mesh.name == cmp_mesh.name:
        h3dd.print_fn_out()
        return [cur_mesh.geometry.polygons[h3du.get_user_value(h3dc.USER_VAL_NAME_CENTER_IDX)]]
    for poly in center_polys:
        # duplicate mesh
        test_mesh = modo.scene.current().duplicateItem(cur_mesh)
        test_mesh.name = '{} [{}]'.format(cur_mesh.name, poly.index)
        # select poly
        lx.eval('select.type polygon')
        lx.eval('select.drop polygon')
        test_polys = [(test_mesh.geometry.polygons[poly.index])]
        # set center to selected poly
        place_center_at_polygons(test_mesh, test_polys, do_poly_triple)
        # modify detect options to using Y axis only
        modified_detect_options = copy.copy(detect_options)
        modified_detect_options.do_bounding_box.x = False
        modified_detect_options.do_bounding_box.z = False
        modified_detect_options.do_center_pos.x = False
        modified_detect_options.do_center_pos.z = False
        modified_detect_options.do_com_pos.x = False
        modified_detect_options.do_com_pos.z = False
        # test if duplicated mesh similar to template mesh
        if is_mesh_similar(test_mesh, cmp_mesh, modified_detect_options):
            modo.scene.current().removeItems(test_mesh)
            h3dd.print_fn_out()
            return [poly]
        modo.scene.current().removeItems(test_mesh)
    h3dd.print_fn_out()
    return []


save_log = h3du.get_user_value(h3dc.USER_VAL_NAME_SAVE_LOG)
log_name = h3du.replace_file_ext(modo.scene.current().name)
h3dd = H3dDebug(enable=save_log, file=log_name)

do_bb = modo.mathutils.Vector3()
do_bb.x = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_BOUNDING_BOX_X)
do_bb.y = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_BOUNDING_BOX_Y)
do_bb.z = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_BOUNDING_BOX_Z)
bb_thld = modo.mathutils.Vector3()
bb_thld.x = h3du.get_user_value(h3dc.USER_VAL_NAME_BB_THRESHOLD_X)
bb_thld.y = h3du.get_user_value(h3dc.USER_VAL_NAME_BB_THRESHOLD_Y)
bb_thld.z = h3du.get_user_value(h3dc.USER_VAL_NAME_BB_THRESHOLD_Z)

do_ctr = modo.mathutils.Vector3()
do_ctr.x = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_CENTER_POS_X)
do_ctr.y = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_CENTER_POS_Y)
do_ctr.z = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_CENTER_POS_Z)
ctr_thld = modo.mathutils.Vector3()
ctr_thld.x = h3du.get_user_value(h3dc.USER_VAL_NAME_CENTER_THRESHOLD_X)
ctr_thld.y = h3du.get_user_value(h3dc.USER_VAL_NAME_CENTER_THRESHOLD_Y)
ctr_thld.z = h3du.get_user_value(h3dc.USER_VAL_NAME_CENTER_THRESHOLD_Z)

do_com = modo.mathutils.Vector3()
do_com.x = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_COM_POS_X)
do_com.y = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_COM_POS_Y)
do_com.z = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_COM_POS_Z)
com_thld = modo.mathutils.Vector3()
com_thld.x = h3du.get_user_value(h3dc.USER_VAL_NAME_COM_THRESHOLD_X)
com_thld.y = h3du.get_user_value(h3dc.USER_VAL_NAME_COM_THRESHOLD_Y)
com_thld.z = h3du.get_user_value(h3dc.USER_VAL_NAME_COM_THRESHOLD_Z)

do_vol = h3du.get_user_value(h3dc.USER_VAL_NAME_DO_MESH_VOL)
vol_thld = h3du.get_user_value(h3dc.USER_VAL_NAME_VOL_THRESHOLD)

detect_options = DetectOptions(do_bounding_box=do_bb,
                               do_center_pos=do_ctr,
                               do_com_pos=do_com,
                               do_mesh_vol=do_vol,
                               bb_threshold=bb_thld,
                               center_threshold=ctr_thld,
                               com_threshold=com_thld,
                               vol_threshold=vol_thld)
