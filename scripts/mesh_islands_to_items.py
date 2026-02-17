#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# unmerge mesh to suitable items
# ================================

import lx
import modo
import modo.constants as c
import modo.mathutils as mmu

import h3d_utilites.scripts.h3d_utils as h3du

import h3d_item_replace_tools.scripts.h3d_kit_constants as h3dc
from h3d_item_replace_tools.scripts.modo_get_mesh_volume_buggy import get_volume
from h3d_item_replace_tools.scripts.get_polygons_operations import (
    get_polygons_find_by_percentage,
    get_polygons_find_by_largest,
)


class DetectOptions:
    def __init__(
        self,
        do_bounding_box,
        do_center_pos,
        do_com_pos,
        do_mesh_vol,
        bb_threshold,
        center_threshold,
        com_threshold,
        vol_threshold,
    ):
        self.do_bounding_box = modo.mathutils.Vector3(do_bounding_box)
        self.do_center_pos = modo.mathutils.Vector3(do_center_pos)
        self.do_com_pos = modo.mathutils.Vector3(do_com_pos)
        self.do_mesh_vol = do_mesh_vol
        self.bb_threshold = modo.mathutils.Vector3(bb_threshold)
        self.center_threshold = modo.mathutils.Vector3(center_threshold)
        self.com_threshold = modo.mathutils.Vector3(com_threshold)
        self.vol_threshold = vol_threshold


def get_tmp_name(name):
    return h3dc.TMP_GRP_NAME_BASE + name


def simple_unmerge(meshes, largest_rot, largest_pos):
    if not meshes:
        return
    for mesh in meshes:
        if not is_multiple_islands(mesh):
            continue
        mesh.select(replace=True)
        lx.eval("layer.unmerge {}".format(mesh.id))

    parent_folder = meshes[0].parent
    todo_meshes = parent_folder.children()
    for mesh in todo_meshes:
        set_item_center(mesh=mesh, largest_rot=largest_rot, largest_pos=largest_pos)
    return todo_meshes


def is_bounding_box_intersects(mesh1, mesh2, search_dist, largest_rot, largest_pos):
    if not mesh1 or not mesh2:
        return False
    if not mesh1 or not mesh2:
        return False

    set_item_center(mesh1, largest_rot, largest_pos)
    set_item_center(mesh2, largest_rot, largest_pos)
    m1_c1, m1_c2 = mesh1.geometry.boundingBox
    m2_c1, m2_c2 = mesh2.geometry.boundingBox

    bb1 = modo.Scene().addMesh("{}_bb1".format(mesh1.name))
    bb1.setParent(mesh1.parent)
    bb1.select(replace=True)
    lx.eval("tool.set prim.cube on")
    lx.eval("tool.setAttr prim.cube cenX 0.0")
    size_x = abs(m1_c1[0] - m1_c2[0]) + search_dist
    lx.eval("tool.setAttr prim.cube sizeX {}".format(size_x))
    lx.eval("tool.setAttr prim.cube cenY 0.0")
    size_y = abs(m1_c1[1] - m1_c2[1]) + search_dist
    lx.eval("tool.setAttr prim.cube sizeY {}".format(size_y))
    lx.eval("tool.setAttr prim.cube cenZ 0.0")
    size_z = abs(m1_c1[2] - m1_c2[2]) + search_dist
    lx.eval("tool.setAttr prim.cube sizeZ {}".format(size_z))
    lx.eval("tool.doApply")
    lx.eval("tool.set prim.cube off 0")

    bb2 = modo.Scene().addMesh("{}_bb2".format(mesh2.name))
    bb2.setParent(mesh2.parent)
    bb2.select(replace=True)
    lx.eval("tool.set prim.cube on")
    lx.eval("tool.setAttr prim.cube cenX 0.0")
    size_x = abs(m2_c1[0] - m2_c2[0]) + search_dist
    lx.eval("tool.setAttr prim.cube sizeX {}".format(size_x))
    lx.eval("tool.setAttr prim.cube cenY 0.0")
    size_y = abs(m2_c1[1] - m2_c2[1]) + search_dist
    lx.eval("tool.setAttr prim.cube sizeY {}".format(size_y))
    lx.eval("tool.setAttr prim.cube cenZ 0.0")
    size_z = abs(m2_c1[2] - m2_c2[2]) + search_dist
    lx.eval("tool.setAttr prim.cube sizeZ {}".format(size_z))
    lx.eval("tool.doApply")
    lx.eval("tool.set prim.cube off 0")

    lx.eval("select.type item")
    bb1.select(replace=True)

    mesh1.select()
    lx.eval("item.match item pos average:false item:{} itemTo:{}".format(bb1.id, mesh1.id))
    lx.eval("item.match item rot average:false item:{} itemTo:{}".format(bb1.id, mesh1.id))
    lx.eval("item.match item scl average:false item:{} itemTo:{}".format(bb1.id, mesh1.id))
    bb2.select(replace=True)

    mesh2.select()
    lx.eval("item.match item pos average:false item:{} itemTo:{}".format(bb2.id, mesh2.id))
    lx.eval("item.match item rot average:false item:{} itemTo:{}".format(bb2.id, mesh2.id))
    lx.eval("item.match item scl average:false item:{} itemTo:{}".format(bb2.id, mesh2.id))

    bb1.select(replace=True)
    bb2.select()
    lx.eval("poly.boolean intersect lastselect {} false")

    is_intersected = len(bb1.geometry.polygons) > 0  # type: ignore

    bb1.select(replace=True)
    bb2.select()
    lx.eval("!!delete")

    return is_intersected


def get_longest_dist(mesh):
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
    return max(lengths)


def is_center_near(current_mesh, compare_mesh, search_dist):
    if not all((current_mesh, compare_mesh)):
        return False

    if current_mesh.type != "mesh" or compare_mesh.type != "mesh":
        return False

    current_mesh_center = mmu.Matrix4(
        current_mesh.channel("worldMatrix").get()
    ).position
    compare_mesh_center = mmu.Matrix4(
        compare_mesh.channel("worldMatrix").get()
    ).position
    cur_mesh_vector = mmu.Vector3(current_mesh_center)
    comp_mesh_vector = mmu.Vector3(compare_mesh_center)
    distance_between_centers = cur_mesh_vector.distanceBetweenPoints(comp_mesh_vector)

    cur_mesh_longest_length = get_longest_dist(current_mesh)
    comp_mesh_longest_length = get_longest_dist(compare_mesh)
    if (distance_between_centers > cur_mesh_longest_length + comp_mesh_longest_length + search_dist * 2):
        return False

    return True


def get_center_ratios(mesh):
    if not mesh:
        return mmu.Vector3()

    if not mesh.geometry.polygons:
        return mmu.Vector3()

    v1, v2 = map(mmu.Vector3, mesh.geometry.boundingBox)
    size = h3du.get_mesh_bounding_box_size(mesh)
    return mmu.Vector3(abs(v2.x * 2 / size.x), abs(v2.y * 2 / size.y), abs(v2.z * 2 / size.z))


def get_max_ratio(val1, val2):
    return max(val1, val2) / min(val1, val2)


def is_valid_ratio(val1, val2, threshold):
    if threshold < 0:
        print("threshold <{}>".format(threshold))
        raise ValueError
    try:
        result = max(val1, val2) / min(val1, val2) < threshold + 1
    except TypeError:
        return False
    except ZeroDivisionError:
        return False

    return result


def is_equal_bounding_box(cur_mesh, cmp_mesh, threshold, options):
    cur_size = h3du.get_mesh_bounding_box_size(cur_mesh)
    cmp_size = h3du.get_mesh_bounding_box_size(cmp_mesh)

    if options.do_bounding_box.x:
        if not is_valid_ratio(cur_size.x, cmp_size.x, threshold.x):
            return False
    if options.do_bounding_box.y:
        if not is_valid_ratio(cur_size.y, cmp_size.y, threshold.y):
            return False
    if options.do_bounding_box.z:
        if not is_valid_ratio(cur_size.z, cmp_size.z, threshold.z):
            return False

    return True


def is_equal_center_pos(cur_mesh, cmp_mesh, threshold, options):
    cur_bb = cur_mesh.geometry.boundingBox
    cmp_bb = cmp_mesh.geometry.boundingBox

    if options.do_center_pos.x:
        if not is_valid_ratio(cur_bb[1][0], cmp_bb[1][0], threshold.x):
            return False

    if options.do_center_pos.y:
        if not is_valid_ratio(cur_bb[1][1], cmp_bb[1][1], threshold.y):
            return False

    if options.do_center_pos.z:
        if not is_valid_ratio(cur_bb[1][2], cmp_bb[1][2], threshold.z):
            return False

    return True


def is_equal_center_of_mass_pos(cur_mesh, cmp_mesh, threshold, options):
    cur_bb = cur_mesh.geometry.boundingBox
    cur_com = mmu.Vector3(get_volume(cur_mesh, com=True))
    cur_com_size = mmu.Vector3(cur_bb[1][0] - cur_com.x, cur_bb[1][1] - cur_com.y, cur_bb[1][2] - cur_com.z)

    cmp_bb = cmp_mesh.geometry.boundingBox
    cmp_com = mmu.Vector3(get_volume(cmp_mesh, com=True))
    cmp_com_size = mmu.Vector3(cmp_bb[1][0] - cmp_com.x, cmp_bb[1][1] - cmp_com.y, cmp_bb[1][2] - cmp_com.z)

    if options.do_com_pos.x:
        if not is_valid_ratio(cur_com_size.x, cmp_com_size.x, threshold.x):
            return False

    if options.do_com_pos.y:
        if not is_valid_ratio(cur_com_size.y, cmp_com_size.y, threshold.y):
            return False

    if options.do_com_pos.z:
        if not is_valid_ratio(cur_com_size.z, cmp_com_size.z, threshold.z):
            return False

    return True


def is_equal_mesh_volume(cur_mesh, cmp_mesh, threshold):
    cur_vol = get_volume(cur_mesh, com=False)
    cur_vol_cube_root = cur_vol ** (1.0 / 3)  # type: ignore

    cmp_vol = get_volume(cmp_mesh, com=False)
    cmp_vol_cube_root = cmp_vol ** (1.0 / 3)  # type: ignore

    if not is_valid_ratio(cur_vol_cube_root, cmp_vol_cube_root, threshold):
        return False

    return True


def is_similar_bounding_box(cur_mesh, cmp_mesh, threshold, options):
    cur_size = h3du.get_mesh_bounding_box_size(cur_mesh)
    cmp_size = h3du.get_mesh_bounding_box_size(cmp_mesh)

    try:
        rel_x = cmp_size.x / cur_size.x
    except ZeroDivisionError:
        rel_x = 0.0
    try:
        rel_y = cmp_size.y / cur_size.y
    except ZeroDivisionError:
        rel_y = 0.0
    try:
        rel_z = cmp_size.z / cur_size.z
    except ZeroDivisionError:
        rel_z = 0.0

    if options.do_bounding_box.x:
        if not is_valid_ratio(rel_y, rel_x, threshold.x):
            return False

    if options.do_bounding_box.y:
        if not is_valid_ratio(rel_y, rel_z, threshold.y):
            return False

    if options.do_bounding_box.z:
        if not is_valid_ratio(rel_x, rel_z, threshold.z):
            return False

    return True


def is_similar_center_pos(cur_mesh, cmp_mesh, threshold, options):
    cur_info_str = h3du.get_mesh_debug_info(cur_mesh)
    curr_center_ratio = get_center_ratios(cur_mesh)
    cur_info_str += "center ratio <{}>\n".format(curr_center_ratio)  # type: ignore
    h3du.set_mesh_debug_info(cur_mesh, cur_info_str)

    cmp_info_str = h3du.get_mesh_debug_info(cmp_mesh)
    comp_center_ratio = get_center_ratios(cmp_mesh)
    cmp_info_str += "center ratio <{}>\n".format(comp_center_ratio)  # type: ignore
    h3du.set_mesh_debug_info(cmp_mesh, cmp_info_str)

    if options.do_center_pos.x:
        if not is_valid_ratio(curr_center_ratio.x, comp_center_ratio.x, threshold.x):
            return False

    if options.do_center_pos.y:
        if not is_valid_ratio(curr_center_ratio.y, comp_center_ratio.y, threshold.y):
            return False

    if options.do_center_pos.z:
        if not is_valid_ratio(curr_center_ratio.z, comp_center_ratio.z, threshold.z):
            return False

    return True


def is_similar_center_of_mass_pos(cur_mesh, cmp_mesh, threshold, options):
    cur_bb = cur_mesh.geometry.boundingBox
    cur_com = mmu.Vector3(get_volume(cur_mesh, com=True))
    cur_com_size = mmu.Vector3(cur_bb[1][0] - cur_com.x, cur_bb[1][1] - cur_com.y, cur_bb[1][2] - cur_com.z)
    cur_com_ratio = mmu.Vector3(
        cur_com_size.x / cur_bb[1][0],
        cur_com_size.y / cur_bb[1][1],
        cur_com_size.z / cur_bb[1][2],
    )
    cur_info_str = h3du.get_mesh_debug_info(cur_mesh)
    cur_info_str += "bb <{}>\ncom <{}> com size <{}>\ncom ratio <{}>\n".format(
        list(cur_bb), list(cur_com), list(cur_com_size), list(cur_com_ratio)  # type: ignore
    )
    h3du.set_mesh_debug_info(cur_mesh, cur_info_str)

    cmp_bb = cmp_mesh.geometry.boundingBox
    cmp_com = mmu.Vector3(get_volume(cmp_mesh, com=True))
    cmp_com_size = mmu.Vector3(
        cmp_bb[1][0] - cmp_com.x, cmp_bb[1][1] - cmp_com.y, cmp_bb[1][2] - cmp_com.z
    )
    cmp_com_ratio = mmu.Vector3(
        cmp_com_size.x / cmp_bb[1][0],
        cmp_com_size.y / cmp_bb[1][1],
        cmp_com_size.z / cmp_bb[1][2],
    )
    cmp_info_str = h3du.get_mesh_debug_info(cmp_mesh)
    cmp_info_str += "bb <{}>\ncom <{}> com size <{}>\ncom ratio <{}>\n".format(
        list(cmp_bb), list(cmp_com), list(cmp_com_size), list(cmp_com_ratio)  # type: ignore
    )
    h3du.set_mesh_debug_info(cmp_mesh, cmp_info_str)

    if options.do_com_pos.x:
        if not is_valid_ratio(cur_com_ratio.x, cmp_com_ratio.x, threshold.x):
            return False

    if options.do_com_pos.y:
        if not is_valid_ratio(cur_com_ratio.y, cmp_com_ratio.y, threshold.y):
            return False

    if options.do_com_pos.z:
        if not is_valid_ratio(cur_com_ratio.z, cmp_com_ratio.z, threshold.z):
            return False

    return True


def is_similar_mesh_volume(cur_mesh, cmp_mesh, threshold):
    try:
        cur_size = h3du.get_mesh_bounding_box_size(cur_mesh)
        cur_bb_vol = cur_size.x * cur_size.y * cur_size.z
        cur_vol = get_volume(cur_mesh, com=False)
        cur_vol_cube_root = cur_vol ** (1.0 / 3)  # type: ignore
        cur_bb_vol_cube_root = cur_bb_vol ** (1.0 / 3)
        cur_vol_root_ratio = cur_vol_cube_root / cur_bb_vol_cube_root
        cur_info_str = h3du.get_mesh_debug_info(cur_mesh)
        cur_info_str += "vol <{}> bb_vol <{}>\nroot ratio <{}>/<{}>=<{}>\n".format(
            cur_vol, cur_bb_vol, cur_vol_cube_root, cur_bb_vol_cube_root, cur_vol_root_ratio  # type: ignore
        )
        h3du.set_mesh_debug_info(cur_mesh, cur_info_str)

        cmp_size = h3du.get_mesh_bounding_box_size(cmp_mesh)
        cmp_bb_vol = cmp_size.x * cmp_size.y * cmp_size.z
        cmp_vol = get_volume(cmp_mesh, com=False)
        cmp_vol_cube_root = cmp_vol ** (1.0 / 3)  # type: ignore
        cmp_bb_vol_cube_root = cmp_bb_vol ** (1.0 / 3)
        cmp_vol_root_ratio = cmp_vol_cube_root / cmp_bb_vol_cube_root
        cmp_info_str = h3du.get_mesh_debug_info(cmp_mesh)
        cmp_info_str += "vol <{}> bb_vol <{}>\nroots ratio <{}>/<{}>=<{}>\n".format(
            cmp_vol, cmp_bb_vol, cmp_vol_cube_root, cmp_bb_vol_cube_root, cmp_vol_root_ratio  # type: ignore
        )
        h3du.set_mesh_debug_info(cmp_mesh, cmp_info_str)

    except ZeroDivisionError:
        return False

    if not is_valid_ratio(cur_vol_root_ratio, cmp_vol_root_ratio, threshold):
        return False

    return True


def is_mesh_similar(cur_mesh, cmp_mesh, options):
    if not all((cur_mesh, cmp_mesh)):
        return False

    if cur_mesh.type != "mesh" or cmp_mesh.type != "mesh":
        return False

    if not all(mesh.geometry.polygons for mesh in (cur_mesh, cmp_mesh)):
        return False

    h3du.set_mesh_debug_info(cur_mesh, "")
    h3du.set_mesh_debug_info(cmp_mesh, "")

    if any(options.do_bounding_box):
        if not is_similar_bounding_box(cur_mesh, cmp_mesh, options.bb_threshold, options):
            return False

    if any(options.do_center_pos):
        if not is_similar_center_pos(cur_mesh, cmp_mesh, options.center_threshold, options):
            return False

    if any(options.do_com_pos):
        if not is_similar_center_of_mass_pos(cur_mesh, cmp_mesh, options.com_threshold, options):
            return False

    if options.do_mesh_vol:
        if not is_similar_mesh_volume(cur_mesh, cmp_mesh, options.vol_threshold):
            return False

    return True


def is_mesh_equal(cur_mesh, cmp_mesh, options):
    if not all((cur_mesh, cmp_mesh)):
        return False

    if cur_mesh.type != "mesh" or cmp_mesh.type != "mesh":
        return False

    if not all(mesh.geometry.polygons for mesh in (cur_mesh, cmp_mesh)):
        return False

    if any(options.do_bounding_box):
        if not is_equal_bounding_box(cur_mesh, cmp_mesh, options.bb_threshold, options):
            return False

    if any(options.do_center_pos):
        if not is_equal_center_pos(cur_mesh, cmp_mesh, options.center_threshold, options):
            return False

    if any(options.do_com_pos):
        if not is_equal_center_of_mass_pos(cur_mesh, cmp_mesh, options.com_threshold, options):
            return False

    if options.do_mesh_vol:
        if not is_equal_mesh_volume(cur_mesh, cmp_mesh, options.vol_threshold):
            return False

    return True


def parent_item_to_item_name(item, group_loc_name):
    try:
        group_loc = modo.Scene().item(group_loc_name)

    except LookupError:
        group_loc = modo.Scene().addItem(itype=c.GROUPLOCATOR_TYPE, name=group_loc_name)

        parent = item.parent
        if parent:
            if group_loc_name != parent.name:
                h3du.parent_items_to([group_loc,], parent, inplace=True)

    h3du.parent_items_to([item,], group_loc, inplace=True)

    return group_loc


def name_sfx2num(name, template_name):
    if not name or not template_name:
        return None

    if not name.startswith(template_name):
        return None

    num_str = name[len(template_name):]
    try:
        number = int(num_str)
    except ValueError:
        return None

    return number


def num2name_sfx(num):
    return "{:03d}".format(num)


def set_mesh_info(store_item, mesh_source):
    if store_item is None:
        return

    if mesh_source is None:
        return

    store_item.select(replace=True)
    lx.eval("item.tagAdd CMMT")
    lx.eval('item.tag string CMMT "{}"'.format(mesh_source.name))


def get_mesh_from_info(store_item):
    if not store_item:
        return None

    store_item.select(replace=True)
    mesh_name = lx.eval("item.tag string CMMT ?")
    try:
        mesh_source = modo.Scene().item(mesh_name)
    except LookupError:
        return None

    return mesh_source


def get_group_locators_by_template(template):
    items = modo.Scene().items(
        itype=c.GROUPLOCATOR_TYPE, name="{}*".format(template)
    )
    return items


def group_equal_meshes(meshes, options):
    if not meshes:
        return

    working_similar_groups = get_group_locators_by_template(
        h3dc.GEO_SHAPE_SIMILAR_TYPE_NAME_BASE
    )
    for similar_group in working_similar_groups:
        equal_groups = similar_group.children(itemType=c.GROUPLOCATOR_TYPE)
        similar_group_num = name_sfx2num(similar_group.name, h3dc.GEO_SHAPE_SIMILAR_TYPE_NAME_BASE)
        type_nums = list(
            name_sfx2num(
                group.name,
                "{}{}{}".format(
                    h3dc.GEO_SHAPE_EQUAL_TYPE_NAME_BASE,
                    num2name_sfx(similar_group_num),
                    h3dc.DIV_LIT,
                ),
            )
            for group in equal_groups
        )
        if type_nums:
            max_type_num = max(type_nums)  # type: ignore
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

            max_type_num += 1
            new_equal_group = parent_item_to_item_name(
                similar_mesh,
                "{}{}{}{}".format(
                    h3dc.GEO_SHAPE_EQUAL_TYPE_NAME_BASE,
                    num2name_sfx(name_sfx2num(similar_group.name, h3dc.GEO_SHAPE_SIMILAR_TYPE_NAME_BASE)),
                    h3dc.DIV_LIT,
                    num2name_sfx(max_type_num),
                ),
            )

            equal_groups.append(new_equal_group)

            set_mesh_info(new_equal_group, similar_mesh)


def group_similar_items(meshes, options):
    if not meshes:
        return

    similar_groups = get_group_locators_by_template(
        h3dc.GEO_SHAPE_SIMILAR_TYPE_NAME_BASE
    )
    type_nums = list(
        name_sfx2num(group.name, h3dc.GEO_SHAPE_SIMILAR_TYPE_NAME_BASE)
        for group in similar_groups
    )
    if type_nums:
        max_type_num = max(type_nums)  # type: ignore
    else:
        max_type_num = 0
    for mesh in meshes:
        is_type_found = False
        for similar_type in similar_groups:
            if is_mesh_similar(mesh, get_mesh_from_info(similar_type), options):
                parent_item_to_item_name(mesh, similar_type.name)
                is_type_found = True
                break

        if is_type_found:
            continue

        max_type_num += 1
        new_similar_type_group = parent_item_to_item_name(
            mesh,
            f'{h3dc.GEO_SHAPE_SIMILAR_TYPE_NAME_BASE}{num2name_sfx(max_type_num)}',
        )

        similar_groups.append(new_similar_type_group)

        set_mesh_info(new_similar_type_group, mesh)


def smart_unmerge(
    meshes, largest_rot, largest_pos, merge_closest, search_dist, area_threshold
):
    if not meshes:
        return

    if not any(mesh.geometry.polygons for mesh in meshes):
        return

    todo_meshes = simple_unmerge(
        meshes=meshes, largest_rot=largest_rot, largest_pos=largest_pos
    )
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
                    largest_pos=largest_pos,
                ):
                    continue

                todo_meshes.remove(compare_mesh)
                h3du.merge_two_meshes(current_mesh, compare_mesh)
                current_mesh_modified = True
            if current_mesh_modified:
                todo_meshes.append(current_mesh)

    result_meshes = parent_folder.children()
    for mesh in result_meshes:
        set_item_center_normalized(
            mesh=mesh,
            largest_rot=largest_rot,
            largest_pos=largest_pos,
            threshold=area_threshold,
        )

    return result_meshes


def is_multiple_islands(mesh):
    if not mesh:
        return False

    if mesh.type != "mesh":
        return False

    if not mesh.geometry.polygons:
        return False

    total_count = len(mesh.geometry.polygons)
    island_count = len(mesh.geometry.polygons[0].getIsland())
    if total_count <= island_count:
        return False

    return True


def place_center_at_polygons(mesh, polys, largest_rot, largest_pos):
    if not mesh:
        return

    if mesh.type != "mesh":
        return

    parent = mesh.parent
    mesh.select(replace=True)
    lx.eval("item.editorColor darkgrey")

    lx.eval("select.type polygon")
    lx.eval("select.drop polygon")
    lx.eval("workPlane.fitSelect")
    lx.eval("select.type item")
    tmp_loc = modo.Scene().addItem(itype=c.LOCATOR_TYPE)
    tmp_loc.select(replace=True)
    lx.eval("item.matchWorkplane pos")
    lx.eval("item.matchWorkplane rot")
    lx.eval("workPlane.reset")

    mesh.select(replace=True)
    lx.eval("select.type polygon")
    lx.eval("select.drop polygon")

    for poly in polys:
        poly.select()

    lx.eval("workPlane.fitSelect")

    lx.eval("select.type item")
    tmp_loc.select(replace=True)
    if largest_pos:
        lx.eval("item.matchWorkplane pos")
    if largest_rot:
        lx.eval("item.matchWorkplane rot")

    rot_x, rot_y, rot_z = tmp_loc.rotation.get(degrees=True)
    tmp_loc.rotation.set((rot_x, rot_y, rot_z + 180.0), degrees=True)

    mesh.select(replace=True)
    tmp_loc.select()
    lx.eval("item.parent inPlace:1")

    mesh.select(replace=True)
    lx.eval("transform.freeze")

    lx.eval("item.parent parent:{{}} inPlace:1")

    if parent is not None:
        parent.select()
        lx.eval("item.parent inPlace:1")

    tmp_loc.select(replace=True)
    lx.eval("item.delete")

    lx.eval("workPlane.reset")


def set_item_center(mesh, largest_rot, largest_pos):
    if not mesh:
        return

    if largest_rot or largest_pos:
        polys = get_polygons_find_by_largest(mesh)
    else:
        polys = []
    place_center_at_polygons(mesh=mesh, polys=polys, largest_rot=largest_rot, largest_pos=largest_pos)


def is_center_normalized(mesh):
    if not mesh:
        return False

    com = mmu.Vector3(get_volume(mesh, com=True))
    if com.y < 0:
        return False

    return True


def set_item_center_normalized(mesh, largest_rot, largest_pos, threshold):
    if not mesh:
        return

    if not (largest_rot or largest_pos):
        return

    polys = get_polygons_find_by_largest(mesh)
    filtered_poly = None

    largest_poly = polys[0]
    rel_area_percent = largest_poly.area / h3du.get_full_mesh_area(mesh)
    polygon_candidates = get_polygons_find_by_percentage(
        mesh=mesh, percentage=rel_area_percent, threshold=threshold
    )

    for poly in polygon_candidates:
        test_mesh = modo.Scene().duplicateItem(mesh)
        test_mesh.name = "{} [{}]".format(mesh.name, poly.index)  # type: ignore

        lx.eval("select.type polygon")
        lx.eval("select.drop polygon")
        test_polys = [(test_mesh.geometry.polygons[poly.index])]  # type: ignore

        place_center_at_polygons(
            mesh=test_mesh,
            polys=test_polys,
            largest_rot=largest_rot,
            largest_pos=largest_pos,
        )
        if is_center_normalized(test_mesh):
            filtered_poly = mesh.geometry.polygons[poly.index]

        modo.Scene().removeItems(test_mesh)
        if filtered_poly:
            break

    result_polys = [filtered_poly] if filtered_poly else [largest_poly]
    place_center_at_polygons(
        mesh=mesh, polys=result_polys, largest_rot=largest_rot, largest_pos=largest_pos
    )
