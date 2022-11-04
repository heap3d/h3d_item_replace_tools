#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# h3d utilites
# v1.0
import lx
import modo
import modo.mathutils as mmu


class H3dUtils:
    @staticmethod
    def get_user_value(name):
        value = lx.eval('user.value {} ?'.format(name))
        return value

    @staticmethod
    def set_user_value(name, value):
        lx.eval('user.value {} {{{}}}'.format(name, value))

    @staticmethod
    def parent_items_to(items, parent):
        # clear selection
        modo.Scene().deselect()
        # select items
        for item in items:
            item.select()
        # select parent item
        parent.select()
        # parent items to parent item
        lx.eval('item.parent inPlace:1')

    @staticmethod
    def set_mesh_debug_info(mesh, info_str, debug_mode=False):
        if not mesh:
            return
        if debug_mode:
            mesh.select(replace=True)
            lx.eval('item.tagAdd DESC')
            lx.eval('item.tag string DESC "{}"'.format(info_str))

    @staticmethod
    def get_mesh_debug_info(mesh):
        if not mesh:
            return None

        mesh.select(replace=True)
        return lx.eval('item.tag string DESC ?')

    @staticmethod
    def get_full_mesh_area(mesh):
        if not mesh:
            return None
        if mesh.type != 'mesh':
            return 0.0

        full_area = sum([poly.area for poly in mesh.geometry.polygons])
        return full_area

    @staticmethod
    def merge_two_meshes(mesh1, mesh2):
        if not mesh1:
            return
        if not mesh2:
            return
        lx.eval('select.type item')
        mesh1.select(replace=True)
        mesh2.select()
        lx.eval('layer.mergeMeshes true')

    @staticmethod
    def get_mesh_bounding_box_size(mesh):
        if not mesh:
            return mmu.Vector3()
        if not mesh.geometry.polygons:
            return mmu.Vector3()
        v1, v2 = map(mmu.Vector3, mesh.geometry.boundingBox)
        return v2 - v1


h3du = H3dUtils()

