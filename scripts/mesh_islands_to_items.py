#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# unmerge mesh to suitable items
# ================================

import sys
import lx
import modo
import modo.constants as c
import modo.mathutils as mmu

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_utilites:}')))
from h3d_utils import H3dUtils
from h3d_debug import H3dDebug
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_kit_constants import *
from modo_get_mesh_volume_buggy import get_volume
from get_polygons_operations import get_polygons_find_by_percentage, get_polygons_find_by_largest


def get_tmp_name(name):
    h3dd.print_fn_in()
    h3dd.print_fn_out()
    return TMP_GRP_NAME_BASE + name


def simple_unmerge(meshes, largest_rot, largest_pos):
    h3dd.print_fn_in()
    if not meshes:
        h3dd.print_fn_out()
        return
    for mesh in meshes:
        if not is_multiple_islands(mesh):
            continue
        mesh.select(replace=True)
        lx.eval('layer.unmerge {}'.format(mesh.id))

    # return list of processed meshes
    parent_folder = meshes[0].parent
    todo_meshes = parent_folder.children()
    for mesh in todo_meshes:
        set_item_center(mesh=mesh, largest_rot=largest_rot, largest_pos=largest_pos)
    h3dd.print_fn_out()
    return todo_meshes


def is_bounding_box_intersects(mesh1, mesh2, search_dist, largest_rot, largest_pos):
    h3dd.print_fn_in()
    if not mesh1 or not mesh2:
        h3dd.print_fn_out()
        return False
    if not mesh1 or not mesh2:
        h3dd.print_fn_out()
        return False
    # get bounding box
    set_item_center(mesh1, largest_rot, largest_pos)
    set_item_center(mesh2, largest_rot, largest_pos)
    m1_c1, m1_c2 = mesh1.geometry.boundingBox
    m2_c1, m2_c2 = mesh2.geometry.boundingBox
    # create bb1 using searching radius offset
    bb1 = modo.scene.current().addMesh('{}_bb1'.format(mesh1.name))
    bb1.setParent(mesh1.parent)
    bb1.select(replace=True)
    lx.eval('tool.set prim.cube on')
    lx.eval('tool.setAttr prim.cube cenX 0.0')
    size_x = abs(m1_c1[0] - m1_c2[0]) + search_dist
    lx.eval('tool.setAttr prim.cube sizeX {}'.format(size_x))
    lx.eval('tool.setAttr prim.cube cenY 0.0')
    size_y = abs(m1_c1[1] - m1_c2[1]) + search_dist
    lx.eval('tool.setAttr prim.cube sizeY {}'.format(size_y))
    lx.eval('tool.setAttr prim.cube cenZ 0.0')
    size_z = abs(m1_c1[2] - m1_c2[2]) + search_dist
    lx.eval('tool.setAttr prim.cube sizeZ {}'.format(size_z))
    lx.eval('tool.doApply')
    lx.eval('tool.set prim.cube off 0')
    # create bb2 using searching radius offset
    bb2 = modo.scene.current().addMesh('{}_bb2'.format(mesh2.name))
    bb2.setParent(mesh2.parent)
    bb2.select(replace=True)
    lx.eval('tool.set prim.cube on')
    lx.eval('tool.setAttr prim.cube cenX 0.0')
    size_x = abs(m2_c1[0] - m2_c2[0]) + search_dist
    lx.eval('tool.setAttr prim.cube sizeX {}'.format(size_x))
    lx.eval('tool.setAttr prim.cube cenY 0.0')
    size_y = abs(m2_c1[1] - m2_c2[1]) + search_dist
    lx.eval('tool.setAttr prim.cube sizeY {}'.format(size_y))
    lx.eval('tool.setAttr prim.cube cenZ 0.0')
    size_z = abs(m2_c1[2] - m2_c2[2]) + search_dist
    lx.eval('tool.setAttr prim.cube sizeZ {}'.format(size_z))
    lx.eval('tool.doApply')
    lx.eval('tool.set prim.cube off 0')
    # align bounding boxes with corresponding meshes
    lx.eval('select.type item')
    bb1.select(replace=True)
    # mesh1_copy.select()
    mesh1.select()
    lx.eval('item.match item pos average:false item:{} itemTo:{}'.format(bb1.id, mesh1.id))
    lx.eval('item.match item rot average:false item:{} itemTo:{}'.format(bb1.id, mesh1.id))
    lx.eval('item.match item scl average:false item:{} itemTo:{}'.format(bb1.id, mesh1.id))
    bb2.select(replace=True)
    # mesh2_copy.select()
    mesh2.select()
    lx.eval('item.match item pos average:false item:{} itemTo:{}'.format(bb2.id, mesh2.id))
    lx.eval('item.match item rot average:false item:{} itemTo:{}'.format(bb2.id, mesh2.id))
    lx.eval('item.match item scl average:false item:{} itemTo:{}'.format(bb2.id, mesh2.id))
    # boolean intersection bounding boxes
    bb1.select(replace=True)
    bb2.select()
    lx.eval('poly.boolean intersect lastselect {} false')
    # check if any polygons remain, store result in intersected variable
    is_intersected = len(bb1.geometry.polygons) > 0
    # remove bounding box meshes
    bb1.select(replace=True)
    bb2.select()
    lx.eval('!!delete')
    # return True if intersected
    h3dd.print_fn_out()
    return is_intersected


def get_longest_dist(mesh):
    h3dd.print_fn_in()
    v1, v2 = map(mmu.Vector3, mesh.geometry.boundingBox)
    p0 = mmu.Vector3(v1.x, v1.y, v1.z)
    p1 = mmu.Vector3(v2.x, v1.y, v1.z)
    p2 = mmu.Vector3(v2.x, v1.y, v2.z)
    p3 = mmu.Vector3(v1.x, v1.y, v2.z)
    p4 = mmu.Vector3(v1.x, v2.y, v1.z)
    p5 = mmu.Vector3(v2.x, v2.y, v1.z)
    p6 = mmu.Vector3(v2.x, v2.y, v2.z)
    p7 = mmu.Vector3(v1.x, v2.y, v2.z)

    vectors = (p0, p1, p2, p3, p4, p5, p6, p7)
    lengths = [v.length() for v in vectors]
    h3dd.print_fn_out()
    return max(lengths)


def is_center_near(current_mesh, compare_mesh, search_dist):
    h3dd.print_fn_in()
    if not all((current_mesh, compare_mesh)):
        h3dd.print_fn_out()
        return False
    if current_mesh.type != 'mesh' or compare_mesh.type != 'mesh':
        h3dd.print_fn_out()
        return False
    current_mesh_center = mmu.Matrix4(current_mesh.channel('worldMatrix').get()).position
    compare_mesh_center = mmu.Matrix4(compare_mesh.channel('worldMatrix').get()).position
    cur_mesh_vector = mmu.Vector3(current_mesh_center)
    comp_mesh_vector = mmu.Vector3(compare_mesh_center)
    distance_between_centers = cur_mesh_vector.distanceBetweenPoints(comp_mesh_vector)

    cur_mesh_longest_length = get_longest_dist(current_mesh)
    comp_mesh_longest_length = get_longest_dist(compare_mesh)
    if distance_between_centers > cur_mesh_longest_length + comp_mesh_longest_length + search_dist * 2:
        h3dd.print_fn_out()
        return False

    h3dd.print_fn_out()
    return True


def get_center_ratios(mesh):
    h3dd.print_fn_in()
    if not mesh:
        h3dd.print_fn_out()
        return mmu.Vector3()
    if not mesh.geometry.polygons:
        h3dd.print_fn_out()
        return mmu.Vector3()
    v1, v2 = map(mmu.Vector3, mesh.geometry.boundingBox)
    size = h3du.get_mesh_bounding_box_size(mesh)
    h3dd.print_fn_out()
    # return mm.Vector3(abs(c2[0] / (size.x / 2)), abs(c2[1] / (size.y / 2)), abs(c2[2] / (size.z / 2)))
    return mmu.Vector3(map(abs, (v2.x * 2 / size.x, v2.y * 2 / size.y, v2.z * 2 / size.z)))


def get_max_ratio(val1, val2):
    h3dd.print_fn_in()
    h3dd.print_fn_out()
    return max(val1, val2) / min(val1, val2)


def is_valid_ratio(val1, val2, threshold):
    h3dd.print_fn_in()
    if threshold < 0:
        print('threshold <{}>'.format(threshold))
        raise ValueError
    result = max(val1, val2) / min(val1, val2) < threshold + 1
    h3dd.print_debug('val1 <{}>; val2 <{}>; threshold <{}>; val/val <{}>'.format(
        val1, val2, threshold, max(val1, val2) / min(val1, val2)))
    h3dd.print_debug(result, )
    h3dd.print_fn_out()
    return result


def is_equal_bounding_box(cur_mesh, cmp_mesh, threshold, options):
    h3dd.print_fn_in()
    cur_size = h3du.get_mesh_bounding_box_size(cur_mesh)
    cmp_size = h3du.get_mesh_bounding_box_size(cmp_mesh)

    if options.do_bounding_box.x:
        if not is_valid_ratio(cur_size.x, cmp_size.x, threshold.x):
            h3dd.print_fn_out()
            return False
    if options.do_bounding_box.y:
        if not is_valid_ratio(cur_size.y, cmp_size.y, threshold.y):
            h3dd.print_fn_out()
            return False
    if options.do_bounding_box.z:
        if not is_valid_ratio(cur_size.z, cmp_size.z, threshold.z):
            h3dd.print_fn_out()
            return False

    h3dd.print_fn_out()
    return True


def is_equal_center_pos(cur_mesh, cmp_mesh, threshold, options):
    h3dd.print_fn_in()
    cur_bb = cur_mesh.geometry.boundingBox
    cmp_bb = cmp_mesh.geometry.boundingBox

    if options.do_center_pos.x:
        if not is_valid_ratio(cur_bb[1][0], cmp_bb[1][0], threshold.x):
            h3dd.print_fn_out()
            return False
    if options.do_center_pos.y:
        if not is_valid_ratio(cur_bb[1][1], cmp_bb[1][1], threshold.y):
            h3dd.print_fn_out()
            return False
    if options.do_center_pos.z:
        if not is_valid_ratio(cur_bb[1][2], cmp_bb[1][2], threshold.z):
            h3dd.print_fn_out()
            return False

    h3dd.print_fn_out()
    return True


def is_equal_center_of_mass_pos(cur_mesh, cmp_mesh, threshold, options):
    h3dd.print_fn_in()
    cur_bb = cur_mesh.geometry.boundingBox
    cur_com = mmu.Vector3(get_volume(cur_mesh, com=True))
    cur_com_size = mmu.Vector3(cur_bb[1][0] - cur_com.x, cur_bb[1][1] - cur_com.y, cur_bb[1][2] - cur_com.z)

    cmp_bb = cmp_mesh.geometry.boundingBox
    cmp_com = mmu.Vector3(get_volume(cmp_mesh, com=True))
    cmp_com_size = mmu.Vector3(cmp_bb[1][0] - cmp_com.x, cmp_bb[1][1] - cmp_com.y, cmp_bb[1][2] - cmp_com.z)

    if options.do_com_pos.x:
        if not is_valid_ratio(cur_com_size.x, cmp_com_size.x, threshold.x):
            h3dd.print_fn_out()
            return False
    if options.do_com_pos.y:
        if not is_valid_ratio(cur_com_size.y, cmp_com_size.y, threshold.y):
            h3dd.print_fn_out()
            return False
    if options.do_com_pos.z:
        if not is_valid_ratio(cur_com_size.z, cmp_com_size.z, threshold.z):
            h3dd.print_fn_out()
            return False

    h3dd.print_fn_out()
    return True


def is_equal_mesh_volume(cur_mesh, cmp_mesh, threshold):
    h3dd.print_fn_in()
    cur_vol = get_volume(cur_mesh, com=False)
    cur_vol_cube_root = cur_vol ** (1.0 / 3)

    cmp_vol = get_volume(cmp_mesh, com=False)
    cmp_vol_cube_root = cmp_vol ** (1.0 / 3)

    if not is_valid_ratio(cur_vol_cube_root, cmp_vol_cube_root, threshold):
        h3dd.print_fn_out()
        return False

    h3dd.print_fn_out()
    return True


def is_similar_bounding_box(cur_mesh, cmp_mesh, threshold, options):
    h3dd.print_fn_in()
    # check bounding box
    cur_size = h3du.get_mesh_bounding_box_size(cur_mesh)
    cmp_size = h3du.get_mesh_bounding_box_size(cmp_mesh)

    rel_x = cmp_size.x / cur_size.x
    rel_y = cmp_size.y / cur_size.y
    rel_z = cmp_size.z / cur_size.z

    if options.do_bounding_box.x:
        if not is_valid_ratio(rel_y, rel_x, threshold.x):
            h3dd.print_fn_out()
            return False
    if options.do_bounding_box.y:
        if not is_valid_ratio(rel_y, rel_z, threshold.y):
            h3dd.print_fn_out()
            return False
    if options.do_bounding_box.z:
        if not is_valid_ratio(rel_x, rel_z, threshold.z):
            h3dd.print_fn_out()
            return False

    h3dd.print_fn_out()
    return True


def is_similar_center_pos(cur_mesh, cmp_mesh, threshold, options):
    h3dd.print_fn_in()
    # check center position
    cur_info_str = h3du.get_mesh_debug_info(cur_mesh)
    curr_center_ratio = get_center_ratios(cur_mesh)
    cur_info_str += 'center ratio <{}>\n'.format(curr_center_ratio)
    h3du.set_mesh_debug_info(cur_mesh, cur_info_str)

    cmp_info_str = h3du.get_mesh_debug_info(cmp_mesh)
    comp_center_ratio = get_center_ratios(cmp_mesh)
    cmp_info_str += 'center ratio <{}>\n'.format(comp_center_ratio)
    h3du.set_mesh_debug_info(cmp_mesh, cmp_info_str)

    if options.do_center_pos.x:
        if not is_valid_ratio(curr_center_ratio.x, comp_center_ratio.x, threshold.x):
            h3dd.print_fn_out()
            return False
    if options.do_center_pos.y:
        if not is_valid_ratio(curr_center_ratio.y, comp_center_ratio.y, threshold.y):
            h3dd.print_fn_out()
            return False
    if options.do_center_pos.z:
        if not is_valid_ratio(curr_center_ratio.z, comp_center_ratio.z, threshold.z):
            h3dd.print_fn_out()
            return False

    h3dd.print_fn_out()
    return True


def is_similar_center_of_mass_pos(cur_mesh, cmp_mesh, threshold, options):
    h3dd.print_fn_in()
    # check center of mass position
    cur_bb = cur_mesh.geometry.boundingBox
    cur_com = mmu.Vector3(get_volume(cur_mesh, com=True))
    cur_com_size = mmu.Vector3(cur_bb[1][0] - cur_com.x, cur_bb[1][1] - cur_com.y, cur_bb[1][2] - cur_com.z)
    cur_com_ratio = mmu.Vector3(cur_com_size.x / cur_bb[1][0], cur_com_size.y / cur_bb[1][1],
                                cur_com_size.z / cur_bb[1][2])
    cur_info_str = h3du.get_mesh_debug_info(cur_mesh)
    cur_info_str += 'bb <{}>\ncom <{}> com size <{}>\ncom ratio <{}>\n'.format(list(cur_bb), list(cur_com),
                                                                               list(cur_com_size), list(cur_com_ratio))
    h3du.set_mesh_debug_info(cur_mesh, cur_info_str)

    cmp_bb = cmp_mesh.geometry.boundingBox
    cmp_com = mmu.Vector3(get_volume(cmp_mesh, com=True))
    cmp_com_size = mmu.Vector3(cmp_bb[1][0] - cmp_com.x, cmp_bb[1][1] - cmp_com.y, cmp_bb[1][2] - cmp_com.z)
    cmp_com_ratio = mmu.Vector3(cmp_com_size.x / cmp_bb[1][0], cmp_com_size.y / cmp_bb[1][1],
                                cmp_com_size.z / cmp_bb[1][2])
    cmp_info_str = h3du.get_mesh_debug_info(cmp_mesh)
    cmp_info_str += 'bb <{}>\ncom <{}> com size <{}>\ncom ratio <{}>\n'.format(list(cmp_bb), list(cmp_com),
                                                                               list(cmp_com_size), list(cmp_com_ratio))
    h3du.set_mesh_debug_info(cmp_mesh, cmp_info_str)

    if options.do_com_pos.x:
        if not is_valid_ratio(cur_com_ratio.x, cmp_com_ratio.x, threshold.x):
            h3dd.print_fn_out()
            return False
    if options.do_com_pos.y:
        if not is_valid_ratio(cur_com_ratio.y, cmp_com_ratio.y, threshold.y):
            h3dd.print_fn_out()
            return False
    if options.do_com_pos.z:
        if not is_valid_ratio(cur_com_ratio.z, cmp_com_ratio.z, threshold.z):
            h3dd.print_fn_out()
            return False

    h3dd.print_fn_out()
    return True


def is_similar_mesh_volume(cur_mesh, cmp_mesh, threshold):
    h3dd.print_fn_in()
    # check mesh volume
    cur_size = h3du.get_mesh_bounding_box_size(cur_mesh)
    cur_bb_vol = cur_size.x * cur_size.y * cur_size.z
    cur_vol = get_volume(cur_mesh, com=False)
    cur_vol_cube_root = cur_vol ** (1.0 / 3)
    cur_bb_vol_cube_root = cur_bb_vol ** (1.0 / 3)
    cur_vol_root_ratio = cur_vol_cube_root / cur_bb_vol_cube_root
    cur_info_str = h3du.get_mesh_debug_info(cur_mesh)
    cur_info_str += 'vol <{}> bb_vol <{}>\nroot ratio <{}>/<{}>=<{}>\n'.format(
        cur_vol, cur_bb_vol, cur_vol_cube_root, cur_bb_vol_cube_root, cur_vol_root_ratio)
    h3du.set_mesh_debug_info(cur_mesh, cur_info_str)

    cmp_size = h3du.get_mesh_bounding_box_size(cmp_mesh)
    cmp_bb_vol = cmp_size.x * cmp_size.y * cmp_size.z
    cmp_vol = get_volume(cmp_mesh, com=False)
    cmp_vol_cube_root = cmp_vol ** (1.0 / 3)
    cmp_bb_vol_cube_root = cmp_bb_vol ** (1.0 / 3)
    cmp_vol_root_ratio = cmp_vol_cube_root / cmp_bb_vol_cube_root
    cmp_info_str = h3du.get_mesh_debug_info(cmp_mesh)
    cmp_info_str += 'vol <{}> bb_vol <{}>\nroots ratio <{}>/<{}>=<{}>\n'.format(
        cmp_vol, cmp_bb_vol, cmp_vol_cube_root, cmp_bb_vol_cube_root, cmp_vol_root_ratio)
    h3du.set_mesh_debug_info(cmp_mesh, cmp_info_str)

    if not is_valid_ratio(cur_vol_root_ratio, cmp_vol_root_ratio, threshold):
        h3dd.print_fn_out()
        return False

    h3dd.print_fn_out()
    return True


class DetectOptions:
    def __init__(self,
                 do_bounding_box, do_center_pos, do_com_pos, do_mesh_vol,
                 bb_threshold, center_threshold, com_threshold, vol_threshold):
        self.do_bounding_box = modo.mathutils.Vector3(do_bounding_box)
        self.do_center_pos = modo.mathutils.Vector3(do_center_pos)
        self.do_com_pos = modo.mathutils.Vector3(do_com_pos)
        self.do_mesh_vol = do_mesh_vol
        self.bb_threshold = modo.mathutils.Vector3(bb_threshold)
        self.center_threshold = modo.mathutils.Vector3(center_threshold)
        self.com_threshold = modo.mathutils.Vector3(com_threshold)
        self.vol_threshold = vol_threshold


def is_mesh_similar(cur_mesh, cmp_mesh, options):
    h3dd.print_fn_in()
    if not all((cur_mesh, cmp_mesh)):
        h3dd.print_fn_out()
        return False
    if cur_mesh.type != 'mesh' or cmp_mesh.type != 'mesh':
        h3dd.print_fn_out()
        return False
    if not all(mesh.geometry.polygons for mesh in (cur_mesh, cmp_mesh)):
        h3dd.print_fn_out()
        return False
    # cleat tags
    h3du.set_mesh_debug_info(cur_mesh, '')
    h3du.set_mesh_debug_info(cmp_mesh, '')
    # do checks
    h3dd.print_debug('cur_mesh <{}>:<{}>; cmp_mesh <{}>:<{}>'.format(cur_mesh.name, cur_mesh, cmp_mesh.name, cmp_mesh))
    if any(options.do_bounding_box):
        if not is_similar_bounding_box(cur_mesh, cmp_mesh, options.bb_threshold, options):
            h3dd.print_fn_out()
            return False
    if any(options.do_center_pos):
        if not is_similar_center_pos(cur_mesh, cmp_mesh, options.center_threshold, options):
            h3dd.print_fn_out()
            return False
    if any(options.do_com_pos):
        if not is_similar_center_of_mass_pos(cur_mesh, cmp_mesh, options.com_threshold, options):
            h3dd.print_fn_out()
            return False
    if options.do_mesh_vol:
        if not is_similar_mesh_volume(cur_mesh, cmp_mesh, options.vol_threshold):
            h3dd.print_fn_out()
            return False

    # all checks passed
    h3dd.print_debug(True)
    h3dd.print_fn_out()
    return True


def is_mesh_equal(cur_mesh, cmp_mesh, options):
    h3dd.print_fn_in()
    if not all((cur_mesh, cmp_mesh)):
        h3dd.print_fn_out()
        return False
    if cur_mesh.type != 'mesh' or cmp_mesh.type != 'mesh':
        h3dd.print_fn_out()
        return False
    if not all(mesh.geometry.polygons for mesh in (cur_mesh, cmp_mesh)):
        h3dd.print_fn_out()
        return False
    # do checks
    h3dd.print_debug(
        'Comparing bounding box of cur_mesh <{}> vs cmp_mesh <{}>   threshold <{}>...'
        .format(cur_mesh.name, cmp_mesh.name, options.bb_threshold))
    if any(options.do_bounding_box):
        if not is_equal_bounding_box(cur_mesh, cmp_mesh, options.bb_threshold, options):
            h3dd.print_debug('bb is not equal')
            h3dd.print_fn_out()
            return False
    if any(options.do_center_pos):
        if not is_equal_center_pos(cur_mesh, cmp_mesh, options.center_threshold, options):
            h3dd.print_debug('center pos is not equal')
            h3dd.print_fn_out()
            return False
    if any(options.do_com_pos):
        if not is_equal_center_of_mass_pos(cur_mesh, cmp_mesh, options.com_threshold, options):
            h3dd.print_debug('com is not equal')
            h3dd.print_fn_out()
            return False
    if options.do_mesh_vol:
        if not is_equal_mesh_volume(cur_mesh, cmp_mesh, options.vol_threshold):
            h3dd.print_debug('vol is not equal')
            h3dd.print_fn_out()
            return False
    h3dd.print_debug('the meshes is equal')
    # all checks passed
    h3dd.print_fn_out()
    return True


def parent_item_to_item_name(item, group_loc_name):
    h3dd.print_fn_in()
    try:
        group_loc = modo.scene.current().item(group_loc_name)
    except LookupError:
        # create new group_loc if not exist
        group_loc = modo.scene.current().addItem(itype=c.GROUPLOCATOR_TYPE, name=group_loc_name)
        # parent group_loc to the item.parent
        group_loc.select(replace=True)
        item.parent.select()
        if group_loc.name != item.parent.name:
            lx.eval('item.parent inPlace:1')
    item.select(replace=True)
    group_loc.select()
    lx.eval('item.parent inPlace:1')

    h3dd.print_fn_out()
    return group_loc


def name_sfx2num(name, template_name):
    h3dd.print_fn_in()
    if not name or not template_name:
        h3dd.print_fn_out()
        return None
    if not name.startswith(template_name):
        h3dd.print_fn_out()
        return None
    num_str = name[len(template_name):]
    try:
        number = int(num_str)
    except ValueError:
        h3dd.print_fn_out()
        return None

    h3dd.print_fn_out()
    return number


def num2name_sfx(num):
    h3dd.print_fn_in()
    h3dd.print_fn_out()
    return '{:03d}'.format(num)


def set_mesh_info(store_item, mesh_source):
    h3dd.print_fn_in()
    # store mesh name where geo info stored
    if store_item is None:
        h3dd.print_fn_out()
        return
    if mesh_source is None:
        h3dd.print_fn_out()
        return
    h3dd.print_debug('store_ite {}>; mesh_source <{}>'.format(store_item.name, mesh_source.name))
    store_item.select(replace=True)
    lx.eval('item.tagAdd CMMT')
    lx.eval('item.tag string CMMT "{}"'.format(mesh_source.name))

    h3dd.print_fn_out()


def get_mesh_from_info(store_item):
    h3dd.print_fn_in()
    # return mesh item by stored name or None
    if not store_item:
        h3dd.print_fn_out()
        return None
    store_item.select(replace=True)
    mesh_name = lx.eval('item.tag string CMMT ?')
    h3dd.print_debug('mesh <{}>'.format(mesh_name))
    try:
        mesh_source = modo.scene.current().item(mesh_name)
    except LookupError:
        h3dd.print_debug('LookupError')
        h3dd.print_fn_out()
        return None

    h3dd.print_fn_out()
    return mesh_source


def get_group_locators_by_template(template):
    h3dd.print_fn_in()
    items = modo.scene.current().items(itype=c.GROUPLOCATOR_TYPE, name='{}*'.format(template))
    h3dd.print_items(list(i.name for i in items), message='group locators:')
    h3dd.print_fn_out()
    return items


def group_equal_meshes(meshes, options):
    h3dd.print_fn_in()
    if not meshes:
        h3dd.print_fn_out()
        return
    # get similar groups list with unsorted meshes
    working_similar_groups = get_group_locators_by_template(GEO_SHAPE_SIMILAR_TYPE_NAME_BASE)
    h3dd.print_items(list(i.name for i in working_similar_groups), message='initial working_similar_groups:')
    h3dd.print_debug('working_similar_groups cycle start:')
    h3dd.indent_inc()
    for similar_group in working_similar_groups:
        h3dd.print_debug('')
        h3dd.print_debug('working_similar_groups cycle next iteration:')
        equal_groups = similar_group.children(itemType=c.GROUPLOCATOR_TYPE)
        h3dd.print_items(equal_groups, message='initial equal groups:')
        similar_group_num = name_sfx2num(similar_group.name, GEO_SHAPE_SIMILAR_TYPE_NAME_BASE)
        type_nums = list(
            name_sfx2num(group.name, '{}{}{}'.format(
                GEO_SHAPE_EQUAL_TYPE_NAME_BASE,
                num2name_sfx(similar_group_num),
                DIV_LIT))
            for group in equal_groups)
        if type_nums:
            max_type_num = max(type_nums)
        else:
            max_type_num = 0
        similar_meshes = similar_group.children(itemType=c.MESH_TYPE)
        for similar_mesh in similar_meshes:
            is_type_found = False
            for equal_type in equal_groups:
                cmp_mesh = get_mesh_from_info(equal_type)
                if is_mesh_equal(similar_mesh, cmp_mesh, options):
                    parent_item_to_item_name(similar_mesh, equal_type.name)
                    is_type_found = True
                    break
            if is_type_found:
                continue
            # create new equal type group
            max_type_num += 1
            new_equal_group = parent_item_to_item_name(similar_mesh, '{}{}{}{}'.format(
                GEO_SHAPE_EQUAL_TYPE_NAME_BASE,
                num2name_sfx(name_sfx2num(similar_group.name, GEO_SHAPE_SIMILAR_TYPE_NAME_BASE)),
                DIV_LIT,
                num2name_sfx(max_type_num)
            ))
            # add new equal group to equal_groups
            equal_groups.append(new_equal_group)
            # set mesh info
            set_mesh_info(new_equal_group, similar_mesh)
    h3dd.indent_dec()
    h3dd.print_fn_out()


def group_similar_items(meshes, options):
    h3dd.print_fn_in()
    h3dd.print_items(list(i.name for i in meshes), message='meshes:')
    if not meshes:
        h3dd.print_fn_out()
        return
    # get similar type group locators list
    similar_groups = get_group_locators_by_template(GEO_SHAPE_SIMILAR_TYPE_NAME_BASE)
    type_nums = list(name_sfx2num(group.name, GEO_SHAPE_SIMILAR_TYPE_NAME_BASE) for group in similar_groups)
    h3dd.print_items(list(i.name for i in similar_groups), message='initial similar_groups:')
    h3dd.print_items(type_nums, message='type_nums:')
    if type_nums:
        max_type_num = max(type_nums)
    else:
        max_type_num = 0
    h3dd.print_debug('max_type_num <{}>'.format(max_type_num))
    h3dd.print_debug('')
    h3dd.print_debug('meshes cycle start:')
    h3dd.indent_inc()
    for mesh in meshes:
        h3dd.print_debug('')
        h3dd.print_debug('meshes cycle next iteration:')
        is_type_found = False
        h3dd.print_debug('mesh <{}>'.format(mesh.name))
        h3dd.print_items(list(i.name for i in similar_groups), message='similar_groups:')
        h3dd.print_debug('')
        h3dd.print_debug('similar_groups cycle start:')
        h3dd.indent_inc()
        for similar_type in similar_groups:
            h3dd.print_debug('')
            h3dd.print_debug('similar_groups cycle next iteration:')
            h3dd.print_debug('similar_type <{}>'.format(similar_type.name))
            if is_mesh_similar(mesh, get_mesh_from_info(similar_type), options):
                parent_item_to_item_name(mesh, similar_type.name)
                is_type_found = True
                break
        h3dd.indent_dec()
        h3dd.print_debug('similar_groups cycle finish')
        h3dd.print_debug('')
        h3dd.print_debug('is_type_found <{}>'.format(is_type_found))
        if is_type_found:
            continue
        # create new similar type group
        h3dd.print_debug('new similar type group detected')
        max_type_num += 1
        h3dd.print_debug('max_type_num <{}>'.format(max_type_num))
        new_similar_type_group = parent_item_to_item_name(
            mesh,
            '{}{}'.format(GEO_SHAPE_SIMILAR_TYPE_NAME_BASE, num2name_sfx(max_type_num))
        )
        # add new_similar_type_group to the similar_groups
        similar_groups.append(new_similar_type_group)
        h3dd.print_items(list(i.name for i in similar_groups),
                         message='similar_groups added: <{}>'.format(new_similar_type_group.name))
        # set mesh info
        set_mesh_info(new_similar_type_group, mesh)

    h3dd.indent_dec()
    h3dd.print_debug('mesh cycle finish')
    h3dd.print_debug('')

    h3dd.print_fn_out()


def smart_unmerge(meshes, largest_rot, largest_pos, merge_closest, search_dist, area_threshold):
    h3dd.print_fn_in()
    if not meshes:
        h3dd.print_fn_out()
        return
    # check for any polygons in the meshes
    if not any(mesh.geometry.polygons for mesh in meshes):
        h3dd.print_fn_out()
        return
    todo_meshes = simple_unmerge(meshes=meshes, largest_rot=largest_rot, largest_pos=largest_pos)
    parent_folder = meshes[0].parent
    if merge_closest:
        while todo_meshes:
            current_mesh = todo_meshes.pop(0)
            current_mesh_modified = False
            compare_meshes = list(todo_meshes)
            while compare_meshes:
                compare_mesh = compare_meshes.pop()
                if not is_center_near(current_mesh, compare_mesh, search_dist):
                    continue
                if not is_bounding_box_intersects(
                        mesh1=current_mesh,
                        mesh2=compare_mesh,
                        search_dist=search_dist,
                        largest_rot=largest_rot,
                        largest_pos=largest_pos
                ):
                    continue
                todo_meshes.remove(compare_mesh)
                h3du.merge_two_meshes(current_mesh, compare_mesh)
                current_mesh_modified = True
            if current_mesh_modified:
                todo_meshes.append(current_mesh)

    result_meshes = parent_folder.children()
    for mesh in result_meshes:
        set_item_center_normalized(mesh=mesh, largest_rot=largest_rot, largest_pos=largest_pos,
                                   threshold=area_threshold)
    # return result meshes
    h3dd.print_fn_out()
    return result_meshes


def is_multiple_islands(mesh):
    h3dd.print_fn_in()
    if not mesh:
        h3dd.print_fn_out()
        return False
    if mesh.type != 'mesh':
        h3dd.print_fn_out()
        return False
    # check for any polygons in the meshes
    if not mesh.geometry.polygons:
        h3dd.print_fn_out()
        return False
    total_count = len(mesh.geometry.polygons)
    island_count = len(mesh.geometry.polygons[0].getIsland())
    if total_count <= island_count:
        h3dd.print_debug('False')
        h3dd.print_fn_out()
        return False

    h3dd.print_debug('True')
    h3dd.print_fn_out()
    return True


def place_center_at_polygons(mesh, polys, largest_rot, largest_pos):
    h3dd.print_fn_in()
    if not mesh:
        h3dd.print_fn_out()
        return
    if mesh.type != 'mesh':
        h3dd.print_fn_out()
        return
    parent = mesh.parent
    h3dd.print_debug('mesh <{}>:<{}>; parent <{}>; polys <{}>'.format(mesh.name, mesh, parent.name, polys))
    mesh.select(replace=True)
    lx.eval('item.editorColor darkgrey')

    # fit workplane with no selection
    lx.eval('select.type polygon')
    lx.eval('select.drop polygon')
    lx.eval('workPlane.fitSelect')
    lx.eval('select.type item')
    tmp_loc = modo.scene.current().addItem(itype=c.LOCATOR_TYPE)
    tmp_loc.select(replace=True)
    lx.eval('item.matchWorkplane pos')
    lx.eval('item.matchWorkplane rot')
    lx.eval('workPlane.reset')

    # fit workplane with selection
    mesh.select(replace=True)
    lx.eval('select.type polygon')
    lx.eval('select.drop polygon')
    # select input polygons
    for poly in polys:
        poly.select()
    # work plane fit to selected polygon
    lx.eval('workPlane.fitSelect')
    # create locator and align it to work plane grid
    lx.eval('select.type item')
    tmp_loc.select(replace=True)
    if largest_pos:
        lx.eval('item.matchWorkplane pos')
    if largest_rot:
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


def set_item_center(mesh, largest_rot, largest_pos):
    h3dd.print_fn_in()
    if not mesh:
        h3dd.print_fn_out()
        return
    if largest_rot or largest_pos:
        polys = get_polygons_find_by_largest(mesh)
    else:
        polys = []
    place_center_at_polygons(mesh=mesh, polys=polys, largest_rot=largest_rot, largest_pos=largest_pos)

    h3dd.print_fn_out()


def is_center_normalized(mesh):
    h3dd.print_fn_in()
    if not mesh:
        h3dd.print_debug('not mesh; return False')
        h3dd.print_fn_out()
        return False
    # get center of mass
    com = mmu.Vector3(get_volume(mesh, com=True))
    if com.y < 0:
        h3dd.print_debug('com.y < 0; return False')
        h3dd.print_fn_out()
        return False

    h3dd.print_debug('return True')
    h3dd.print_fn_out()
    return True


def set_item_center_normalized(mesh, largest_rot, largest_pos, threshold):
    h3dd.print_fn_in()
    if not mesh:
        h3dd.print_debug('not mesh')
        h3dd.print_fn_out()
        return
    if not (largest_rot or largest_pos):
        h3dd.print_debug('not (largest_rot or largest_pos)')
        h3dd.print_fn_out()
        return
    polys = get_polygons_find_by_largest(mesh)
    h3dd.print_debug(
        'mesh <{}>:<{}>; largest_rot <{}>; largest_pos <{}>; threshold <{}>'
        .format(mesh.name, mesh, largest_rot, largest_pos, threshold))
    h3dd.print_items(polys, 'polys:')
    filtered_poly = None

    largest_poly = polys[0]
    # get largest polygon relative area
    rel_area_percent = largest_poly.area / h3du.get_full_mesh_area(mesh)
    h3dd.print_debug('largest_poly index <{}>; rel_area_percent <{}>; area <{}>; mesh full area <{}>'.format(
        largest_poly.index, rel_area_percent, largest_poly.area, h3du.get_full_mesh_area(mesh)))
    polygon_candidates = get_polygons_find_by_percentage(
        mesh=mesh,
        percentage=rel_area_percent,
        threshold=threshold)
    h3dd.print_items(polygon_candidates, 'polygon_candidates:')
    h3dd.print_debug('polygon_candidates cycle start:')
    for poly in polygon_candidates:
        # duplicate mesh
        test_mesh = modo.scene.current().duplicateItem(mesh)
        test_mesh.name = '{} [{}]'.format(mesh.name, poly.index)
        # select poly
        lx.eval('select.type polygon')
        lx.eval('select.drop polygon')
        test_polys = [(test_mesh.geometry.polygons[poly.index])]
        h3dd.print_items(test_polys, 'test_polys:')
        # set center to selected poly
        place_center_at_polygons(mesh=test_mesh, polys=test_polys, largest_rot=largest_rot, largest_pos=largest_pos)
        if is_center_normalized(test_mesh):
            filtered_poly = mesh.geometry.polygons[poly.index]
        modo.scene.current().removeItems(test_mesh)
        if filtered_poly:
            break

    result_polys = [filtered_poly] if filtered_poly else [largest_poly]
    h3dd.print_items(result_polys, 'result_polys:')
    place_center_at_polygons(mesh=mesh, polys=result_polys, largest_rot=largest_rot, largest_pos=largest_pos)

    h3dd.print_fn_out()


h3du = H3dUtils()
save_log = h3du.get_user_value(USER_VAL_NAME_SAVE_LOG)
log_name = h3du.replace_file_ext(modo.scene.current().name)
h3dd = H3dDebug(enable=save_log, file=log_name)
