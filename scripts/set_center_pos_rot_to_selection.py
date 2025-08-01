#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# set item center position and orientation by component selection
# ================================

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import (
    get_select_type,
    duplicate_item,
)

from scripts.center_utilites import (
    get_selected_components,
    select_components,
    place_center_at_locator,
    update_instance,
    create_loc_at_selection,
)


def main():
    selected_meshes = modo.Scene().selectedByType(itype=c.MESH_TYPE)
    select_type = get_select_type()

    selected_components: dict[modo.Mesh, list] = dict()
    for mesh in selected_meshes:
        selected_components[mesh] = get_selected_components(mesh, select_type)

    new_meshes: list[modo.Mesh] = []
    for mesh in selected_meshes:
        select_components(mesh, selected_components[mesh], select_type)

        locator = create_loc_at_selection(mesh, select_type, orient=True)

        new_mesh = duplicate_item(mesh)
        if not isinstance(new_mesh, modo.Mesh):
            raise TypeError('Failed to duplicate mesh.')

        place_center_at_locator(new_mesh, locator)
        modo.Scene().removeItems(locator)

        update_instance(new_mesh, mesh)

        new_meshes.append(new_mesh)

    if new_meshes:
        modo.Scene().deselect()
        for mesh in new_meshes:
            mesh.select()


if __name__ == '__main__':
    main()
