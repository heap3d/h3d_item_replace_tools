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
import modo.mathutils as mm

USER_VAL_NAME_SEARCH_DIST = 'h3d_sumt_search_dist'
USER_VAL_NAME_TYPE_PCT = 'h3d_sumt_type_pct'
USER_VAL_NAME_LARGEST_ROT = 'h3d_sumt_largest_rot'
USER_VAL_NAME_LARGEST_POS = 'h3d_sumt_largest_pos'
TMP_GRP_NAME_BASE = '$h3d$ unmerge '

scene = modo.scene.current()


def get_user_value(name):
    value = lx.eval('user.value {} ?'.format(name))
    return value


def parent_items_to(items, parent):
    for item in items:
        # item.setParent(parent)
        item.select(replace=True)
        parent.select()
        lx.eval('item.parent inPlace:1')


def get_tmp_name(name):
    return TMP_GRP_NAME_BASE + name


def modo_unmerge(meshes):
    if meshes is None:
        return
    if not meshes:
        return
    for mesh in meshes:
        if not is_multiple_islands(mesh):
            continue
        mesh.select(replace=True)
        lx.eval('layer.unmerge {}'.format(mesh.id))


def merge_meshes(mesh1, mesh2):
    lx.eval('select.type item')
    mesh1.select(replace=True)
    mesh2.select()
    lx.eval('layer.mergeMeshes true')


def is_bounding_box_intersects(mesh1, mesh2, search_dist, largest_rot, largest_pos):
    if mesh1 is None or mesh2 is None:
        return False
    if not mesh1 or not mesh2:
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
    return is_intersected


def get_longest_dist(mesh):
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
    return max(lengths)


def is_center_near(current_mesh, compare_mesh, search_dist):
    if not all((current_mesh, compare_mesh)):
        return False
    if current_mesh.type != 'mesh' or compare_mesh.type != 'mesh':
        return False
    current_mesh_center = mm.Matrix4(current_mesh.channel('worldMatrix').get()).position
    compare_mesh_center = mm.Matrix4(compare_mesh.channel('worldMatrix').get()).position
    cur_mesh_vector = mm.Vector3(current_mesh_center)
    comp_mesh_vector = mm.Vector3(compare_mesh_center)
    distance_between_centers = cur_mesh_vector.distanceBetweenPoints(comp_mesh_vector)

    cur_mesh_longest_length = get_longest_dist(current_mesh)
    comp_mesh_longest_length = get_longest_dist(compare_mesh)
    if distance_between_centers > cur_mesh_longest_length + comp_mesh_longest_length + search_dist * 2:
        return False

    return True


def get_bb_size(mesh):
    if not mesh:
        return mm.Vector3()
    if not mesh.geometry.polygons:
        return mm.Vector3()
    c1, c2 = mesh.geometry.boundingBox
    size_x = abs(c2[0] - c1[0])
    size_y = abs(c2[1] - c1[1])
    size_z = abs(c2[2] - c1[2])
    return mm.Vector3(size_x, size_y, size_z)


def is_mesh_similar(current_mesh, compare_mesh, threshold):
    if not all((current_mesh, compare_mesh)):
        return False
    if current_mesh.type != 'mesh' or compare_mesh.type != 'mesh':
        return False
    if not all(mesh.geometry.polygons for mesh in (current_mesh, compare_mesh)):
        return False
    # todo check axis ratio
    curr_size_v3 = get_bb_size(current_mesh)
    curr_max = max(curr_size_v3)
    curr_min = min(curr_size_v3)
    sizes = list(curr_size_v3)
    sizes.remove(curr_max)
    sizes.remove(curr_min)
    curr_mid = sizes[0]
    comp_size_v3 = get_bb_size(compare_mesh)
    comp_max = max(comp_size_v3)
    comp_min = min(comp_size_v3)
    sizes = list(comp_size_v3)
    sizes.remove(comp_max)
    sizes.remove(comp_min)
    comp_mid = sizes[0]

    # todo check center position
    # todo check center orientation
    return True


def is_mesh_equal(current_mesh, compare_mesh, threshold):
    if not all((current_mesh, compare_mesh)):
        return False
    if current_mesh.type != 'mesh' or compare_mesh.type != 'mesh':
        return False
    if not all(mesh.geometry.polygons for mesh in (current_mesh, compare_mesh)):
        return False
    # todo check axis size
    curr_size_v3 = get_bb_size(current_mesh)
    curr_max = max(curr_size_v3)
    curr_min = min(curr_size_v3)
    sizes = list(curr_size_v3)
    sizes.remove(curr_max)
    sizes.remove(curr_min)
    curr_mid = sizes[0]
    comp_size_v3 = get_bb_size(compare_mesh)
    comp_max = max(comp_size_v3)
    comp_min = min(comp_size_v3)
    sizes = list(comp_size_v3)
    sizes.remove(comp_max)
    sizes.remove(comp_min)
    comp_mid = sizes[0]
    if abs(curr_max / comp_max) > threshold:
        return False
    if abs(curr_min / comp_min) > threshold:
        return False
    if abs(curr_mid / comp_mid) > threshold:
        return False

    return True


def move_item_to_group_loc(item, group_loc_name):
    # check if group locator exist
    try:
        group_loc = scene.item(group_loc_name)
    except LookupError:
        # create group_loc
        group_loc = scene.addItem(itype='groupLocator', name=group_loc_name)
    group_loc.setParent(item.parent)
    item.setParent(group_loc)


def smart_unmerge(meshes, search_dist, largest_rot, largest_pos, type_detect_dist):
    if meshes is None:
        return
    if not meshes:
        return
    # check for any polygons in the meshes
    if not any(mesh.geometry.polygons for mesh in meshes):
        return
    # todo do unmerge in a new scene to speed up the process
    modo_unmerge(meshes)
    parent_folder = meshes[0].parent
    todo_meshes = parent_folder.children()
    while todo_meshes:
        current_mesh = todo_meshes.pop(0)
        current_mesh_modified = False
        compare_meshes = list(todo_meshes)
        while compare_meshes:
            compare_mesh = compare_meshes.pop()
            if not is_center_near(current_mesh, compare_mesh, search_dist):
                continue
            if not is_bounding_box_intersects(current_mesh, compare_mesh, search_dist, largest_rot, largest_pos):
                continue
            todo_meshes.remove(compare_mesh)
            merge_meshes(current_mesh, compare_mesh)
            current_mesh_modified = True
        if current_mesh_modified:
            todo_meshes.append(current_mesh)
    # todo group similar items
    todo_meshes = parent_folder.children()
    item_types = {1: todo_meshes[0]}
    typed_items = {}
    # detect items type
    for mesh in todo_meshes:
        matched_type = 0
        for item_type in item_types:
            if is_mesh_similar(mesh, item_types[item_type], type_detect_dist):
                matched_type = item_type
                break
        if matched_type == 0:
            # create new item type
            matched_type = max(item_types) + 1
            # add mesh to the new item type
            item_types[matched_type] = mesh
        # add item type to current mesh
        typed_items[mesh] = matched_type
    if len(item_types) < 2:
        return
    for item in typed_items:
        group_loc_name = 't{:02d}'.format(typed_items[item])
        move_item_to_group_loc(item, group_loc_name)


def is_multiple_islands(mesh):
    if mesh is None:
        return False
    if mesh.type != 'mesh':
        return False
    # check for any polygons in the meshes
    if not mesh.geometry.polygons:
        return

    total_count = len(mesh.geometry.polygons)
    island_count = len(mesh.geometry.polygons[0].getIsland())
    if total_count > island_count:
        return True

    return False


def place_center_at_polygons(mesh, polys, largest_rot, largest_pos):
    if mesh is None:
        return
    parent = mesh.parent
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


def get_full_area(mesh):
    full_area = sum([poly.area for poly in mesh.geometry.polygons])
    return full_area


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


def set_item_center(mesh, largest_rot, largest_pos):
    if mesh is None:
        return
    if largest_rot or largest_pos:
        polys = get_polygons_find_by_largest(mesh)
    else:
        polys = []
    place_center_at_polygons(mesh, polys, largest_rot, largest_pos)


def main():
    print('')
    print('start...')

    # get user values from UI
    search_dist = get_user_value(USER_VAL_NAME_SEARCH_DIST)
    largest_rot = get_user_value(USER_VAL_NAME_LARGEST_ROT)
    largest_pos = get_user_value(USER_VAL_NAME_LARGEST_POS)
    type_detect_pct = get_user_value(USER_VAL_NAME_TYPE_PCT)

    is_unmerge_regular = False

    print('lx.args:<{}>'.format(lx.args()))
    if lx.args():
        for arg in lx.args():
            print('command line argument: <{}>'.format(arg))
            if arg == '-regular':
                is_unmerge_regular = True
                print('Modo Unmerge Mesh command used.')

    selected_meshes = scene.selectedByType(itype=c.MESH_TYPE)
    if not selected_meshes:
        return
    # create temp group folder
    tmp_grp = scene.addItem(itype=c.GROUPLOCATOR_TYPE, name=get_tmp_name(selected_meshes[0].name))
    parent_items_to(selected_meshes, tmp_grp)

    if is_unmerge_regular:
        modo_unmerge(selected_meshes)
    else:
        smart_unmerge(selected_meshes, search_dist, largest_rot, largest_pos, type_detect_pct)

    # set item center
    for item in tmp_grp.children():
        set_item_center(item, largest_rot, largest_pos)
    # select processed meshes
    scene.deselect()
    for item in tmp_grp.children():
        item.select()

    print('done.')


if __name__ == '__main__':
    main()
