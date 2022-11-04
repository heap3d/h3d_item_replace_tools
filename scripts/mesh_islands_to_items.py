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
import modo.mathutils as mm
sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from kit_constants import *
from h3d_utils import h3du
from h3d_debug import h3dd, is_print_fn_debug
from modo_get_mesh_volume_buggy import get_volume


DIV_LIT = '-'


def get_tmp_name(name):
    h3dd.print_fn_in(is_print_fn_debug)
    h3dd.print_fn_out(is_print_fn_debug)
    return TMP_GRP_NAME_BASE + name


def modo_unmerge(meshes, largest_rot, largest_pos):
    h3dd.print_fn_in(is_print_fn_debug)
    if not meshes:
        h3dd.print_fn_out(is_print_fn_debug)
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
    h3dd.print_fn_out(is_print_fn_debug)
    return todo_meshes


def is_bounding_box_intersects(mesh1, mesh2, search_dist, largest_rot, largest_pos):
    h3dd.print_fn_in(is_print_fn_debug)
    if not mesh1 or not mesh2:
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not mesh1 or not mesh2:
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    # get bounding box
    set_item_center(mesh1, largest_rot, largest_pos)
    set_item_center(mesh2, largest_rot, largest_pos)
    m1_c1, m1_c2 = mesh1.geometry.boundingBox
    m2_c1, m2_c2 = mesh2.geometry.boundingBox
    # create bb1 using searching radius offset
    bb1 = scene.addMesh('{}_bb1'.format(mesh1.name))
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
    bb2 = scene.addMesh('{}_bb2'.format(mesh2.name))
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
    h3dd.print_fn_out(is_print_fn_debug)
    return is_intersected


def get_longest_dist(mesh):
    h3dd.print_fn_in(is_print_fn_debug)
    c1, c2 = mesh.geometry.boundingBox
    p0 = mm.Vector3(c1[0], c1[1], c1[2])
    p1 = mm.Vector3(c2[0], c1[1], c1[2])
    p2 = mm.Vector3(c2[0], c1[1], c2[2])
    p3 = mm.Vector3(c1[0], c1[1], c2[2])
    p4 = mm.Vector3(c1[0], c2[1], c1[2])
    p5 = mm.Vector3(c2[0], c2[1], c1[2])
    p6 = mm.Vector3(c2[0], c2[1], c2[2])
    p7 = mm.Vector3(c1[0], c2[1], c2[2])

    vectors = (p0, p1, p2, p3, p4, p5, p6, p7)
    lengths = [v.length() for v in vectors]
    h3dd.print_fn_out(is_print_fn_debug)
    return max(lengths)


def is_center_near(current_mesh, compare_mesh, search_dist):
    h3dd.print_fn_in(is_print_fn_debug)
    if not all((current_mesh, compare_mesh)):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if current_mesh.type != 'mesh' or compare_mesh.type != 'mesh':
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    current_mesh_center = mm.Matrix4(current_mesh.channel('worldMatrix').get()).position
    compare_mesh_center = mm.Matrix4(compare_mesh.channel('worldMatrix').get()).position
    cur_mesh_vector = mm.Vector3(current_mesh_center)
    comp_mesh_vector = mm.Vector3(compare_mesh_center)
    distance_between_centers = cur_mesh_vector.distanceBetweenPoints(comp_mesh_vector)

    cur_mesh_longest_length = get_longest_dist(current_mesh)
    comp_mesh_longest_length = get_longest_dist(compare_mesh)
    if distance_between_centers > cur_mesh_longest_length + comp_mesh_longest_length + search_dist * 2:
        h3dd.print_fn_out(is_print_fn_debug)
        return False

    h3dd.print_fn_out(is_print_fn_debug)
    return True


def get_center_ratios(mesh):
    h3dd.print_fn_in(is_print_fn_debug)
    if not mesh:
        h3dd.print_fn_out(is_print_fn_debug)
        return mm.Vector3()
    if not mesh.geometry.polygons:
        h3dd.print_fn_out(is_print_fn_debug)
        return mm.Vector3()
    v1, v2 = map(mm.Vector3, mesh.geometry.boundingBox)
    size = h3du.get_mesh_bounding_box_size(mesh)
    h3dd.print_fn_out(is_print_fn_debug)
    # return mm.Vector3(abs(c2[0] / (size.x / 2)), abs(c2[1] / (size.y / 2)), abs(c2[2] / (size.z / 2)))
    return mm.Vector3(map(abs, (v2.x * 2 / size.x, v2.y * 2 / size.y, v2.z * 2 / size.z)))


def get_max_ratio(val1, val2):
    h3dd.print_fn_in(is_print_fn_debug)
    h3dd.print_fn_out(is_print_fn_debug)
    return max(val1, val2) / min(val1, val2)


def is_valid_ratio(val1, val2, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
    if threshold < 0:
        print('threshold <{}>'.format(threshold))
        raise ValueError
    result = max(val1, val2) / min(val1, val2) < threshold + 1
    h3dd.print_debug(result, is_print_fn_debug)
    h3dd.print_fn_out(is_print_fn_debug)
    return result


def is_equal_bounding_box(cur_mesh, cmp_mesh, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
    cur_size = h3du.get_mesh_bounding_box_size(cur_mesh)
    cmp_size = h3du.get_mesh_bounding_box_size(cmp_mesh)
    if not is_valid_ratio(cur_size.x, cmp_size.x, threshold.x):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not is_valid_ratio(cur_size.y, cmp_size.y, threshold.y):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not is_valid_ratio(cur_size.z, cmp_size.z, threshold.z):
        h3dd.print_fn_out(is_print_fn_debug)
        return False

    h3dd.print_fn_out(is_print_fn_debug)
    return True


def is_equal_center_pos(cur_mesh, cmp_mesh, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
    cur_bb = cur_mesh.geometry.boundingBox
    cmp_bb = cmp_mesh.geometry.boundingBox

    if not is_valid_ratio(cur_bb[1][0], cmp_bb[1][0], threshold.x):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not is_valid_ratio(cur_bb[1][1], cmp_bb[1][1], threshold.y):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not is_valid_ratio(cur_bb[1][2], cmp_bb[1][2], threshold.z):
        h3dd.print_fn_out(is_print_fn_debug)
        return False

    h3dd.print_fn_out(is_print_fn_debug)
    return True


def is_equal_center_of_mass_pos(cur_mesh, cmp_mesh, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
    cur_bb = cur_mesh.geometry.boundingBox
    cur_com = mm.Vector3(get_volume(cur_mesh, com=True))
    cur_com_size = mm.Vector3(cur_bb[1][0] - cur_com.x, cur_bb[1][1] - cur_com.y, cur_bb[1][2] - cur_com.z)

    cmp_bb = cmp_mesh.geometry.boundingBox
    cmp_com = mm.Vector3(get_volume(cmp_mesh, com=True))
    cmp_com_size = mm.Vector3(cmp_bb[1][0] - cmp_com.x, cmp_bb[1][1] - cmp_com.y, cmp_bb[1][2] - cmp_com.z)

    if not is_valid_ratio(cur_com_size.x, cmp_com_size.x, threshold.x):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not is_valid_ratio(cur_com_size.y, cmp_com_size.y, threshold.y):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not is_valid_ratio(cur_com_size.z, cmp_com_size.z, threshold.z):
        h3dd.print_fn_out(is_print_fn_debug)
        return False

    h3dd.print_fn_out(is_print_fn_debug)
    return True


def is_equal_mesh_volume(cur_mesh, cmp_mesh, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
    cur_vol = get_volume(cur_mesh, com=False)
    cur_vol_cube_root = cur_vol ** (1.0 / 3)

    cmp_vol = get_volume(cmp_mesh, com=False)
    cmp_vol_cube_root = cmp_vol ** (1.0 / 3)

    if not is_valid_ratio(cur_vol_cube_root, cmp_vol_cube_root, threshold):
        h3dd.print_fn_out(is_print_fn_debug)
        return False

    h3dd.print_fn_out(is_print_fn_debug)
    return True


def is_similar_bounding_box(cur_mesh, cmp_mesh, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
    # check bounding box
    cur_size = h3du.get_mesh_bounding_box_size(cur_mesh)
    cmp_size = h3du.get_mesh_bounding_box_size(cmp_mesh)

    rel_x = cmp_size.x / cur_size.x
    rel_y = cmp_size.y / cur_size.y
    rel_z = cmp_size.z / cur_size.z

    if not is_valid_ratio(rel_y, rel_x, threshold.x):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not is_valid_ratio(rel_y, rel_z, threshold.z):
        h3dd.print_fn_out(is_print_fn_debug)
        return False

    h3dd.print_fn_out(is_print_fn_debug)
    return True


def is_similar_center_pos(cur_mesh, cmp_mesh, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
    # check center position
    cur_info_str = h3du.get_mesh_debug_info(cur_mesh)
    curr_center_ratio = get_center_ratios(cur_mesh)
    cur_info_str += 'center ratio <{}>\n'.format(curr_center_ratio)
    h3du.set_mesh_debug_info(cur_mesh, cur_info_str)

    cmp_info_str = h3du.get_mesh_debug_info(cmp_mesh)
    comp_center_ratio = get_center_ratios(cmp_mesh)
    cmp_info_str += 'center ratio <{}>\n'.format(comp_center_ratio)
    h3du.set_mesh_debug_info(cmp_mesh, cmp_info_str)

    if not is_valid_ratio(curr_center_ratio.x, comp_center_ratio.x, threshold.x):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not is_valid_ratio(curr_center_ratio.y, comp_center_ratio.y, threshold.y):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not is_valid_ratio(curr_center_ratio.z, comp_center_ratio.z, threshold.z):
        h3dd.print_fn_out(is_print_fn_debug)
        return False

    h3dd.print_fn_out(is_print_fn_debug)
    return True


def is_similar_center_of_mass_pos(cur_mesh, cmp_mesh, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
    # check center of mass position
    cur_bb = cur_mesh.geometry.boundingBox
    cur_com = mm.Vector3(get_volume(cur_mesh, com=True))
    cur_com_size = mm.Vector3(cur_bb[1][0] - cur_com.x, cur_bb[1][1] - cur_com.y, cur_bb[1][2] - cur_com.z)
    cur_com_ratio = mm.Vector3(cur_com_size.x / cur_bb[1][0], cur_com_size.y / cur_bb[1][1],
                               cur_com_size.z / cur_bb[1][2])
    cur_info_str = h3du.get_mesh_debug_info(cur_mesh)
    cur_info_str += 'bb <{}>\ncom <{}> com size <{}>\ncom ratio <{}>\n'.format(list(cur_bb), list(cur_com),
                                                                           list(cur_com_size), list(cur_com_ratio))
    h3du.set_mesh_debug_info(cur_mesh, cur_info_str)

    cmp_bb = cmp_mesh.geometry.boundingBox
    cmp_com = mm.Vector3(get_volume(cmp_mesh, com=True))
    cmp_com_size = mm.Vector3(cmp_bb[1][0] - cmp_com.x, cmp_bb[1][1] - cmp_com.y, cmp_bb[1][2] - cmp_com.z)
    cmp_com_ratio = mm.Vector3(cmp_com_size.x / cmp_bb[1][0], cmp_com_size.y / cmp_bb[1][1],
                               cmp_com_size.z / cmp_bb[1][2])
    cmp_info_str = h3du.get_mesh_debug_info(cmp_mesh)
    cmp_info_str += 'bb <{}>\ncom <{}> com size <{}>\ncom ratio <{}>\n'.format(list(cmp_bb), list(cmp_com),
                                                                           list(cmp_com_size), list(cmp_com_ratio))
    h3du.set_mesh_debug_info(cmp_mesh, cmp_info_str)

    if not is_valid_ratio(cur_com_ratio.x, cmp_com_ratio.x, threshold.x):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not is_valid_ratio(cur_com_ratio.y, cmp_com_ratio.y, threshold.y):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not is_valid_ratio(cur_com_ratio.z, cmp_com_ratio.z, threshold.z):
        h3dd.print_fn_out(is_print_fn_debug)
        return False

    h3dd.print_fn_out(is_print_fn_debug)
    return True


def is_similar_mesh_volume(cur_mesh, cmp_mesh, threshold):
    h3dd.print_fn_in(is_print_fn_debug)
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
        h3dd.print_fn_out(is_print_fn_debug)
        return False

    h3dd.print_fn_out(is_print_fn_debug)
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
    h3dd.print_fn_in(is_print_fn_debug)
    if not all((cur_mesh, cmp_mesh)):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if cur_mesh.type != 'mesh' or cmp_mesh.type != 'mesh':
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not all(mesh.geometry.polygons for mesh in (cur_mesh, cmp_mesh)):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    # cleat tags
    h3du.set_mesh_debug_info(cur_mesh, '')
    h3du.set_mesh_debug_info(cmp_mesh, '')
    # do checks
    h3dd.print_debug('cur_mesh <{}>:<{}>; cmp_mesh <{}>:<{}>'.format(cur_mesh.name, cur_mesh, cmp_mesh.name, cmp_mesh), is_print_fn_debug)
    if any(options.do_bounding_box):
        if not is_similar_bounding_box(cur_mesh, cmp_mesh, options.bb_threshold):
            h3dd.print_fn_out(is_print_fn_debug)
            return False
    if any(options.do_center_pos):
        if not is_similar_center_pos(cur_mesh, cmp_mesh, options.center_threshold):
            h3dd.print_fn_out(is_print_fn_debug)
            return False
    if any(options.do_com_pos):
        if not is_similar_center_of_mass_pos(cur_mesh, cmp_mesh, options.com_threshold):
            h3dd.print_fn_out(is_print_fn_debug)
            return False
    if options.do_mesh_vol:
        if not is_similar_mesh_volume(cur_mesh, cmp_mesh, options.vol_threshold):
            h3dd.print_fn_out(is_print_fn_debug)
            return False

    # all checks passed
    h3dd.print_debug(True, is_print_fn_debug)
    h3dd.print_fn_out(is_print_fn_debug)
    return True


def is_mesh_equal(cur_mesh, cmp_mesh, options):
    h3dd.print_fn_in(is_print_fn_debug)
    if not all((cur_mesh, cmp_mesh)):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if cur_mesh.type != 'mesh' or cmp_mesh.type != 'mesh':
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if not all(mesh.geometry.polygons for mesh in (cur_mesh, cmp_mesh)):
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    # do checks
    h3dd.print_debug('Comparing bounding box of cur_mesh <{}> vs cmp_mesh <{}>   threshold <{}>...'.format(cur_mesh.name, cmp_mesh.name, options.bb_threshold), is_print_fn_debug)
    if any(options.do_bounding_box):
        if not is_equal_bounding_box(cur_mesh, cmp_mesh, options.bb_threshold):
            h3dd.print_debug('bb is not equal', is_print_fn_debug)
            h3dd.print_fn_out(is_print_fn_debug)
            return False
    if any(options.do_center_pos):
        if not is_equal_center_pos(cur_mesh, cmp_mesh, options.center_threshold):
            h3dd.print_debug('center pos is not equal', is_print_fn_debug)
            h3dd.print_fn_out(is_print_fn_debug)
            return False
    if any(options.do_com_pos):
        if not is_equal_center_of_mass_pos(cur_mesh, cmp_mesh, options.com_threshold):
            h3dd.print_debug('com is not equal', is_print_fn_debug)
            h3dd.print_fn_out(is_print_fn_debug)
            return False
    if options.do_mesh_vol:
        if not is_equal_mesh_volume(cur_mesh, cmp_mesh, options.vol_threshold):
            h3dd.print_debug('vol is not equal', is_print_fn_debug)
            h3dd.print_fn_out(is_print_fn_debug)
            return False
    h3dd.print_debug('the meshes is equal', is_print_fn_debug)
    # all checks passed
    h3dd.print_fn_out(is_print_fn_debug)
    return True


def parent_item_to_item_name(item, group_loc_name):
    h3dd.print_fn_in(is_print_fn_debug)
    try:
        group_loc = scene.item(group_loc_name)
    except LookupError:
        # create new group_loc if not exist
        group_loc = scene.addItem(itype=c.GROUPLOCATOR_TYPE, name=group_loc_name)
        # parent group_loc to the item.parent
        group_loc.select(replace=True)
        item.parent.select()
        if group_loc.name != item.parent.name:
            lx.eval('item.parent inPlace:1')
    item.select(replace=True)
    group_loc.select()
    lx.eval('item.parent inPlace:1')

    h3dd.print_fn_out(is_print_fn_debug)
    return group_loc


def name_sfx2num(name, template_name):
    h3dd.print_fn_in(is_print_fn_debug)
    if not name or not template_name:
        h3dd.print_fn_out(is_print_fn_debug)
        return None
    if not name.startswith(template_name):
        h3dd.print_fn_out(is_print_fn_debug)
        return None
    num_str = name[len(template_name):]
    try:
        number = int(num_str)
    except ValueError:
        h3dd.print_fn_out(is_print_fn_debug)
        return None

    h3dd.print_fn_out(is_print_fn_debug)
    return number


def num2name_sfx(num):
    h3dd.print_fn_in(is_print_fn_debug)
    h3dd.print_fn_out(is_print_fn_debug)
    return '{:03d}'.format(num)


def set_mesh_info(store_item, mesh_source):
    h3dd.print_fn_in(is_print_fn_debug)
    # store mesh name where geo info stored
    if store_item is None:
        h3dd.print_fn_out(is_print_fn_debug)
        return
    if mesh_source is None:
        h3dd.print_fn_out(is_print_fn_debug)
        return
    h3dd.print_debug('store_ite {}>; mesh_source <{}>'.format(store_item.name, mesh_source.name), enable=is_print_fn_debug)
    store_item.select(replace=True)
    lx.eval('item.tagAdd CMMT')
    lx.eval('item.tag string CMMT "{}"'.format(mesh_source.name))

    h3dd.print_fn_out(is_print_fn_debug)


def get_mesh_from_info(store_item):
    h3dd.print_fn_in(is_print_fn_debug)
    # return mesh item by stored name or None
    if not store_item:
        h3dd.print_fn_out(is_print_fn_debug)
        return None
    store_item.select(replace=True)
    mesh_name = lx.eval('item.tag string CMMT ?')
    h3dd.print_debug('mesh <{}>'.format(mesh_name), is_print_fn_debug)
    try:
        mesh_source = scene.item(mesh_name)
    except LookupError:
        h3dd.print_debug('LookupError', is_print_fn_debug)
        h3dd.print_fn_out(is_print_fn_debug)
        return None

    h3dd.print_fn_out(is_print_fn_debug)
    return mesh_source


def get_group_locators_by_template(template):
    h3dd.print_fn_in(is_print_fn_debug)
    items = scene.items(itype=c.GROUPLOCATOR_TYPE, name='{}*'.format(template))
    h3dd.print_items(list(i.name for i in items), message='group locators:', enable=is_print_fn_debug)
    h3dd.print_fn_out(is_print_fn_debug)
    return items


def group_equal_meshes(meshes):
    h3dd.print_fn_in(is_print_fn_debug)
    if not meshes:
        h3dd.print_fn_out(is_print_fn_debug)
        return
    # get similar groups list with unsorted meshes
    working_similar_groups = get_group_locators_by_template(GEO_SHAPE_SIMILAR_TYPE_NAME_BASE)
    h3dd.print_items(list(i.name for i in working_similar_groups), message='initial working_similar_groups:', enable=is_print_fn_debug)
    h3dd.print_debug('working_similar_groups cycle start:', is_print_fn_debug)
    h3dd.indent_inc()
    for similar_group in working_similar_groups:
        h3dd.print_debug('', is_print_fn_debug)
        h3dd.print_debug('working_similar_groups cycle next iteration:', is_print_fn_debug)
        equal_groups = similar_group.children(itemType=c.GROUPLOCATOR_TYPE)
        h3dd.print_items(equal_groups, message='initial equal groups:', enable=is_print_fn_debug)
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
                if is_mesh_equal(similar_mesh, cmp_mesh, detect_options):
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
    h3dd.print_fn_out(is_print_fn_debug)


def group_similar_items(meshes):
    h3dd.print_fn_in(is_print_fn_debug)
    h3dd.print_items(list(i.name for i in meshes), message='meshes:', enable=is_print_fn_debug)
    if not meshes:
        h3dd.print_fn_out(is_print_fn_debug)
        return
    # get similar type group locators list
    similar_groups = get_group_locators_by_template(GEO_SHAPE_SIMILAR_TYPE_NAME_BASE)
    type_nums = list(name_sfx2num(group.name, GEO_SHAPE_SIMILAR_TYPE_NAME_BASE) for group in similar_groups)
    h3dd.print_items(list(i.name for i in similar_groups), message='initial similar_groups:', enable=is_print_fn_debug)
    h3dd.print_items(type_nums, message='type_nums:', enable=is_print_fn_debug)
    if type_nums:
        max_type_num = max(type_nums)
    else:
        max_type_num = 0
    h3dd.print_debug('max_type_num <{}>'.format(max_type_num), is_print_fn_debug)
    h3dd.print_debug('', is_print_fn_debug)
    h3dd.print_debug('meshes cycle start:', is_print_fn_debug)
    h3dd.indent_inc()
    for mesh in meshes:
        h3dd.print_debug('', is_print_fn_debug)
        h3dd.print_debug('meshes cycle next iteration:', is_print_fn_debug)
        is_type_found = False
        h3dd.print_debug('mesh <{}>'.format(mesh.name), is_print_fn_debug)
        h3dd.print_items(list(i.name for i in similar_groups), message='similar_groups:', enable=is_print_fn_debug)
        h3dd.print_debug('', is_print_fn_debug)
        h3dd.print_debug('similar_groups cycle start:', is_print_fn_debug)
        h3dd.indent_inc()
        for similar_type in similar_groups:
            h3dd.print_debug('', is_print_fn_debug)
            h3dd.print_debug('similar_groups cycle next iteration:', is_print_fn_debug)
            h3dd.print_debug('similar_type <{}>'.format(similar_type.name), is_print_fn_debug)
            if is_mesh_similar(mesh, get_mesh_from_info(similar_type), detect_options):
                parent_item_to_item_name(mesh, similar_type.name)
                is_type_found = True
                break
        h3dd.indent_dec()
        h3dd.print_debug('similar_groups cycle finish', is_print_fn_debug)
        h3dd.print_debug('', is_print_fn_debug)
        h3dd.print_debug('is_type_found <{}>'.format(is_type_found), is_print_fn_debug)
        if is_type_found:
            continue
        # create new similar type group
        h3dd.print_debug('new similar type group detected', is_print_fn_debug)
        max_type_num += 1
        h3dd.print_debug('max_type_num <{}>'.format(max_type_num), is_print_fn_debug)
        new_similar_type_group = parent_item_to_item_name(
            mesh,
            '{}{}'.format(GEO_SHAPE_SIMILAR_TYPE_NAME_BASE, num2name_sfx(max_type_num))
        )
        # add new_similar_type_group to the similar_groups
        similar_groups.append(new_similar_type_group)
        h3dd.print_items(list(i.name for i in similar_groups), message='similar_groups added: <{}>'.format(new_similar_type_group.name), enable=is_print_fn_debug)
        # set mesh info
        set_mesh_info(new_similar_type_group, mesh)

    h3dd.indent_dec()
    h3dd.print_debug('mesh cycle finish', is_print_fn_debug)
    h3dd.print_debug('', is_print_fn_debug)
    # group equal meshes
    if do_group_equal:
        group_equal_meshes(meshes)

    h3dd.print_fn_out(is_print_fn_debug)


def smart_unmerge(meshes, largest_rot, largest_pos, merge_closest, search_dist):
    # todo unified axis orientation for complex meshes
    h3dd.print_fn_in(is_print_fn_debug)
    if not meshes:
        h3dd.print_fn_out(is_print_fn_debug)
        return
    # check for any polygons in the meshes
    if not any(mesh.geometry.polygons for mesh in meshes):
        h3dd.print_fn_out(is_print_fn_debug)
        return
    # todo do unmerge in a new scene to speed up the process
    modo_unmerge(meshes=meshes, largest_rot=largest_rot, largest_pos=largest_pos)
    parent_folder = meshes[0].parent
    todo_meshes = parent_folder.children()
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
    # return todo_meshes
    todo_meshes = parent_folder.children()
    h3dd.print_fn_out(is_print_fn_debug)
    return todo_meshes


def is_multiple_islands(mesh):
    h3dd.print_fn_in(is_print_fn_debug)
    if not mesh:
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    if mesh.type != 'mesh':
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    # check for any polygons in the meshes
    if not mesh.geometry.polygons:
        h3dd.print_fn_out(is_print_fn_debug)
        return False
    total_count = len(mesh.geometry.polygons)
    island_count = len(mesh.geometry.polygons[0].getIsland())
    if total_count <= island_count:
        h3dd.print_debug('False', is_print_fn_debug)
        h3dd.print_fn_out(is_print_fn_debug)
        return False

    h3dd.print_debug('True', is_print_fn_debug)
    h3dd.print_fn_out(is_print_fn_debug)
    return True


def place_center_at_polygons(mesh, polys, largest_rot, largest_pos):
    h3dd.print_fn_in(is_print_fn_debug)
    if not mesh:
        h3dd.print_fn_out(is_print_fn_debug)
        return
    if mesh.type != 'mesh':
        h3dd.print_fn_out(is_print_fn_debug)
        return
    parent = mesh.parent
    h3dd.print_debug('mesh <{}>:<{}>; parent <{}>; polys <{}>'.format(mesh.name, mesh, parent.name, polys), is_print_fn_debug)
    mesh.select(replace=True)
    lx.eval('item.editorColor darkgrey')

    # fit workplane with no selection
    lx.eval('select.type polygon')
    lx.eval('select.drop polygon')
    lx.eval('workPlane.fitSelect')
    lx.eval('select.type item')
    tmp_loc = scene.addItem(itype=c.LOCATOR_TYPE)
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

    h3dd.print_fn_out(is_print_fn_debug)


def get_polygons_find_by_largest(mesh):
    h3dd.print_fn_in(is_print_fn_debug)
    # return matched polygon or [] if none
    if mesh is None:
        h3dd.print_fn_out(is_print_fn_debug)
        return []
    if mesh.type != 'mesh':
        h3dd.print_fn_out(is_print_fn_debug)
        return []
    polys = get_polygons_find_by_margins(mesh=mesh, percentage=1.0, margin_low=0.0, margin_high=1.0)
    h3dd.print_debug('polys <{}>'.format(polys), is_print_fn_debug)
    h3dd.print_fn_out(is_print_fn_debug)
    return polys


def get_polygons_find_by_margins(mesh, percentage, margin_low, margin_high):
    h3dd.print_fn_in(is_print_fn_debug)
    # return matched polygon or [] if none
    if not mesh:
        h3dd.print_fn_out(is_print_fn_debug)
        return []
    if mesh.type != 'mesh':
        h3dd.print_fn_out(is_print_fn_debug)
        return []
    min_difference = 1
    poly = []
    full_area = h3du.get_full_mesh_area(mesh)
    for polygon in mesh.geometry.polygons:
        poly_percentage = polygon.area / full_area
        if margin_low < poly_percentage < margin_high:
            difference = abs(percentage - poly_percentage)
            if difference < min_difference:
                min_difference = difference
                poly = polygon

    h3dd.print_fn_out(is_print_fn_debug)
    return [poly] if poly else []


def set_item_center(mesh, largest_rot, largest_pos):
    h3dd.print_fn_in(is_print_fn_debug)
    if not mesh:
        h3dd.print_fn_out(is_print_fn_debug)
        return
    if largest_rot or largest_pos:
        polys = get_polygons_find_by_largest(mesh)
    else:
        polys = []
    place_center_at_polygons(mesh, polys, largest_rot, largest_pos)

    h3dd.print_fn_out(is_print_fn_debug)


def main():
    h3dd.print_debug('\n\n----- mesh_islands_to_items.py -----\n', is_print_fn_debug)
    h3dd.print_fn_in(is_print_fn_debug)
    print('')
    print('start...')

    is_unmerge_regular_mode = False
    is_group_similar_mode = False

    print('lx.args: <{}>'.format(lx.args()))
    if lx.args():
        for arg in lx.args():
            print('command line argument: <{}>'.format(arg))
            if arg == '-regular':
                is_unmerge_regular_mode = True
                print('Simple Unmerge Mesh command used.')
            elif arg == '-group':
                is_group_similar_mode = True
                print('Group Similar Meshes command used.')

    selected_meshes = scene.selectedByType(itype=c.MESH_TYPE)
    if not selected_meshes:
        h3dd.print_fn_out(is_print_fn_debug)
        return
    # create temp group folder
    tmp_grp = scene.addItem(itype=c.GROUPLOCATOR_TYPE, name=get_tmp_name(selected_meshes[0].name))
    h3dd.print_debug('selected_meshes <{}>; tmp_grp <{}>'.format(list(i.name for i in selected_meshes), tmp_grp.name), is_print_fn_debug)
    h3du.parent_items_to(selected_meshes, tmp_grp)

    if is_unmerge_regular_mode:
        todo_meshes = modo_unmerge(
            meshes=selected_meshes,
            largest_rot=largest_rot,
            largest_pos=largest_pos
        )
        if do_group_similar:
            group_similar_items(todo_meshes)
    elif is_group_similar_mode:
        group_similar_items(meshes=selected_meshes)
    else:
        todo_meshes = smart_unmerge(
            meshes=selected_meshes,
            largest_rot=largest_rot,
            largest_pos=largest_pos,
            merge_closest=merge_closest,
            search_dist=search_dist
        )
        h3dd.print_debug('do_group_similar <{}>'.format(do_group_similar), is_print_fn_debug)
        if do_group_similar:
            group_similar_items(todo_meshes)
    # select processed meshes
    scene.deselect()
    for item in tmp_grp.children():
        item.select()

    print('done.')
    h3dd.print_fn_out(is_print_fn_debug)


if __name__ == '__main__':
    # get user values from UI
    search_dist = h3du.get_user_value(USER_VAL_NAME_SEARCH_DIST)
    largest_rot = h3du.get_user_value(USER_VAL_NAME_LARGEST_ROT)
    largest_pos = h3du.get_user_value(USER_VAL_NAME_LARGEST_POS)
    do_group_similar = h3du.get_user_value(USER_VAL_NAME_GROUP_SIMILAR)
    do_group_equal = h3du.get_user_value(USER_VAL_NAME_GROUP_EQUAL)
    merge_closest = h3du.get_user_value(USER_VAL_NAME_MERGE_CLOSEST)

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

    dialog_svc = lx.service.StdDialog()
    scene = modo.Scene()

    main()
