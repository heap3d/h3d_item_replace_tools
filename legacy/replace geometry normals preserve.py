#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub, Ihor Tykhomyrov
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# Replace old GEO in REF scene with new GEO with normals preserving
# Select old item, then add new to selection, run the script
# ================================
import math

import modo
import lx


scene = modo.Scene()


def debug_exit(message='debug exit'):
    print(message)
    exit()


def main():
    if len(scene.selectedByType('mesh')) != 2:
        print('Please select two mesh items to run')
        return
    old_mesh = scene.selectedByType(itype='mesh')[0]
    new_mesh = scene.selectedByType(itype='mesh')[1]

    # add locator
    tmp_loc = scene.addItem(itype='locator')
    # parent loc to new mesh
    lx.eval('item.parent {} {} 0 inPlace:0 duplicate:0'.format(tmp_loc.id, new_mesh.id))
    # un parent loc in place
    lx.eval('item.parent {} {{}} 0 inPlace:1 duplicate:0'.format(tmp_loc.id))
    # select old mesh
    old_mesh.select(replace=True)
    # find vertex normal map name
    vert_normal_maps = []
    for vmap in old_mesh.geometry.vmaps:
        if 'VertexNormalMap' in str(vmap):
            vert_normal_maps.append(vmap)
    for vnmap in vert_normal_maps:
        # select old mesh vertex normal map
        lx.eval('select.vertexMap "{}" norm replace'.format(vnmap.name))
        # delete selected vertex maps
        lx.eval('!vertMap.delete norm')
    # select all polys for old mesh and delete polygons
    old_mesh.select(replace=True)
    lx.eval('select.type polygon')
    lx.eval('select.invert')
    lx.eval('delete')
    # item select mode
    lx.eval('select.type item')
    # add new mesh item to selection
    new_mesh.select()
    # merge selected mesh items without Transform Compensation
    lx.eval('layer.mergeMeshes false')
    # select tmp_loc
    tmp_loc.select(replace=True)
    # ask for transform coordinates
    posX = lx.eval('transform.channel pos.X ?')
    posY = lx.eval('transform.channel pos.Y ?')
    posZ = lx.eval('transform.channel pos.Z ?')
    rotX = lx.eval('transform.channel rot.X ?')
    rotY = lx.eval('transform.channel rot.Y ?')
    rotZ = lx.eval('transform.channel rot.Z ?')
    # select old_mesh
    old_mesh.select(replace=True)
    # select vertex normal map
    for vmap in old_mesh.geometry.vmaps:
        if 'VertexNormalMap' in str(vmap):
            lx.eval('select.vertexMap "{}" norm replace'.format(vmap.name))
            break
    # activate Action Center Origin
    # lx.eval('tool.set actr.origin on')
    # polygon selection mode
    lx.eval('select.type polygon')
    # lx.eval('select.invert')
    # rotate
    # lx.eval('tool.set TransformRotate on')
    # lx.eval('tool.noChange')
    # # lx.eval('tool.setAttr xfrm.transform normal update')
    # lx.eval('tool.setAttr xfrm.transform RX {}'.format(math.degrees(rotX)))
    # lx.eval('tool.setAttr xfrm.transform RY {}'.format(math.degrees(rotY)))
    # lx.eval('tool.setAttr xfrm.transform RZ {}'.format(math.degrees(rotZ)))
    # lx.eval('tool.doApply')
    # lx.eval('tool.set TransformRotate off 0')
    # move
    # lx.eval('tool.set TransformMove on')
    # lx.eval('tool.noChange')
    # # lx.eval('tool.setAttr xfrm.transform normal update')
    # lx.eval('tool.setAttr xfrm.transform TX {}'.format(posX))
    # lx.eval('tool.setAttr xfrm.transform TY {}'.format(posY))
    # lx.eval('tool.setAttr xfrm.transform TZ {}'.format(posZ))
    # lx.eval('tool.setAttr xfrm.transform U {}'.format(posX))
    # lx.eval('tool.setAttr xfrm.transform V {}'.format(posY))
    # lx.eval('tool.doApply')
    # lx.eval('tool.set TransformMove off 0')
    # delete temporary locator
    scene.removeItems(tmp_loc)
    # turn Action Center Origin off
    lx.eval('tool.set actr.origin off')


if __name__ == '__main__':
    main()
