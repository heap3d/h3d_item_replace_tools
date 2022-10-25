#!/usr/bin/python
################################################################################
#
# calculate_mesh_vol_cog.py
#
# Version: 1.000
#
#
#   Copyright (c) 2001-2022, The Foundry Group LLC
#   All Rights Reserved. Patents granted and pending.
#
#
# Author: Gwynne Reddick
#
# Description: Commands to calculate the volume and center of mass of a
#              watertight mesh.
#
# Last Update: 14:16 03/03/15
#
################################################################################
import lxifc
import lxu
import lx


# modo code from calculate_mesh_vol_cog.py
def get_volume(mesh, com=False):
    """Calculates the volume or center of gravity (if com argument is True) of a mesh item. Uses a TriangleSoup
    object to sample the mesh surface(s).

    All lines commented by Dmytro Holub to turn off monitors
    """
    # if com:
    #     main_monitor = lx.object.Monitor(dialog_svc.MonitorAllocate('Calculating Center Of Mass ...'))
    # else:
    #     main_monitor = lx.object.Monitor(dialog_svc.MonitorAllocate('Calculating Volume ...'))
    # main_monitor.Initialize(2)
    if com:
        cx = cy = cz = 0.0
    volume = 0.0
    scene = mesh.Context()
    chan_eval = scene.Channels(None, lx.service.Selection().GetTime())
    isurf = lx.object.SurfaceItem(mesh)
    surf = isurf.GetSurface(chan_eval, 1)
    # surf_monitor = lx.object.Monitor(dialog_svc.MonitorAllocate('Sampling surfaces ...'))
    surf_monitor = 'Modified by Dmytro Holub, comment this line and uncomment all others to restore original'
    soup = TriSoup(surf_monitor)
    samp = lx.object.TableauSurface()
    surf_bincount = surf.BinCount()
    # surf_monitor.Initialize(surf.GLCount())
    for x in range(surf_bincount):
        samp.set(surf.BinByIndex(x))
        soup.Sample(samp)
        # surf_monitor.Increment(1)
    # dialog_svc.MonitorRelease()
    # main_monitor.Increment(1)
    # poly_monitor = lx.object.Monitor(dialog_svc.MonitorAllocate('Calculating mesh volume ...'))
    # poly_monitor.Initialize(len(soup.output))
    for poly in soup.output:
        x1, y1, z1, x2, y2, z2, x3, y3, z3 = poly
        v = x1 * (y2 * z3 - y3 * z2) + y1 * (z2 * x3 - z3 * x2) + z1 * (x2 * y3 - x3 * y2)
        volume += v
        if com:
            cx += (x1 + x2 + x3) * v
            cy += (y1 + y2 + y3) * v
            cz += (z1 + z2 + z3) * v
        # poly_monitor.Increment(1)
    # dialog_svc.MonitorRelease()
    # main_monitor.Increment(1)
    # dialog_svc.MonitorRelease()
    if com:
        cx /= 4 * volume
        cy /= 4 * volume
        cz /= 4 * volume
        return (round(cx, 5), round(cy, 5), round(cz, 5))
    else:
        volume /= 6
        return volume


# modo code from calculate_mesh_vol_cog.py
class TriSoup(lxifc.TriangleSoup):
    def __init__(self, mon):
        # self.mon = lx.object.Monitor(mon)
        self.output = []
        self.vdesc = lx.service.Tableau().AllocVertex()
        self.vdesc.AddFeature(lx.symbol.iTBLX_BASEFEATURE, lx.symbol.sTBLX_FEATURE_POS)

    def Sample(self, surf):
        surf.SetVertex(self.vdesc)
        surf.Sample(surf.Bound(), -1.0, self)

    def soup_Segment(self, segID, stype):
        # clear the verts list and return a new triangle segment.
        self.vrts = []
        return stype == lx.symbol.iTBLX_SEG_TRIANGLE

    def soup_Vertex(self, vbuf):
        # Gets the next vertex and adds it to the current polygon
        vbuf.setType('f')
        vbuf.setSize(3)
        self.vrts.append(vbuf.get())
        return len(self.vrts) - 1

    def soup_Polygon(self, v0, v1, v2):
        # process the next polygon
        x0 = lxu.vector.sub(self.vrts[v1], self.vrts[v0])
        x1 = lxu.vector.sub(self.vrts[v2], self.vrts[v0])

        p0x, p0y, p0z = self.vrts[v0]
        p1x, p1y, p1z = self.vrts[v1]
        p2x, p2y, p2z = self.vrts[v2]
        self.output.append((p0x, p0y, p0z, p1x, p1y, p1z, p2x, p2y, p2z))
        # self.mon.Increment(1)
