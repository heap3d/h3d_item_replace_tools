#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# Leonard
# move item center position by component selection
# ================================

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import (
    get_select_type,
)

from h3d_item_replace_tools.scripts.center_utilites import (
    get_selected_components,
    update_center,
    numparents,
    select_if_exists,
)


def main():
    selected_meshes: list[modo.Mesh] = modo.Scene().selectedByType(itype=c.MESH_TYPE)
    selected_meshes.sort(key=numparents, reverse=True)
    if not selected_meshes:
        return

    select_type = get_select_type()
    selected_components: dict[modo.Mesh, list] = dict()
    for mesh in selected_meshes:
        selected_components[mesh] = get_selected_components(mesh, select_type)

    new_meshes: list[modo.Mesh] = []
    for mesh in selected_meshes:
        if not mesh.geometry.numVertices:
            continue

        if not mesh.geometry.numVertices:
            return mesh

        new_mesh = update_center(mesh, select_type, selected_components[mesh], align_pos=False)

        new_meshes.append(new_mesh)

    select_if_exists(new_meshes)


if __name__ == '__main__':
    main()
