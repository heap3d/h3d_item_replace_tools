#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# channel to setup
# Set the current value of the channels of all items to Setup mode

import modo
import lx


def get_position(locator):
    if not locator.isAnInstance:
        try:
            transforms = locator.transforms
        except AttributeError:
            return None
        return transforms.position
    for xfrm in locator.itemGraph('xfrmCore').reverse():
        if xfrm.type == 'translation':
            # return first appropriate transform in a stack
            return xfrm


def get_rotation(locator):
    if not locator.isAnInstance:
        try:
            transforms = locator.transforms
        except AttributeError:
            return None
        return transforms.rotation
    for xfrm in locator.itemGraph('xfrmCore').reverse():
        if xfrm.type == 'rotation':
            # return first appropriate transform in a stack
            return xfrm


def get_scale(locator):
    if not locator.isAnInstance:
        try:
            transforms = locator.transforms
        except AttributeError:
            return None
        return transforms.scale
    for xfrm in locator.itemGraph('xfrmCore').reverse():
        if xfrm.type == 'scale':
            # return first appropriate transform in a stack
            return xfrm


def main():
    items = modo.scene.current().items(itype='locator', superType=True)
    for item in items:
        # print(item.name, item)
        # if item.type == 'replicator':
        #     continue
        item.select(replace=True)
        position = get_position(item)
        # print('position:<{}>'.format(position))
        if position:
            lx.eval('select.drop channel')
            lx.eval('select.channel {{{}:pos.X@lmb=x}} add'.format(position.id))
            lx.eval('select.channel {{{}:pos.Y@lmb=x}} add'.format(position.id))
            lx.eval('select.channel {{{}:pos.Z@lmb=x}} add'.format(position.id))

        rotation = get_rotation(item)
        # print('rotation:<{}>'.format(rotation))
        if rotation:
            lx.eval('select.channel {{{}:rot.X@lmb=x}} add'.format(rotation.id))
            lx.eval('select.channel {{{}:rot.Y@lmb=x}} add'.format(rotation.id))
            lx.eval('select.channel {{{}:rot.Z@lmb=x}} add'.format(rotation.id))

        scale = get_scale(item)
        # print('scale:<{}>'.format(scale))
        if scale:
            lx.eval('select.channel {{{}:scl.X@lmb=x}} add'.format(scale.id))
            lx.eval('select.channel {{{}:scl.Y@lmb=x}} add'.format(scale.id))
            lx.eval('select.channel {{{}:scl.Z@lmb=x}} add'.format(scale.id))

        if any((position, rotation, scale)):
            lx.eval('channel.toSetup')


if __name__ == '__main__':
    main()
