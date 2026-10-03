"""Previs geometry helpers used by the assembly cell (cell.py): beams, cylinders, cables between two points."""
import math
import numpy as np
import bpy
from mathutils import Vector, Matrix
import lib


def _orient(o, a, b, up=(0, 0, 1)):
    """Place object o (built along local +Z, centred) between points a and b, local X kept horizontal."""
    a, b = Vector(a), Vector(b); d = (b - a)
    z = d.normalized(); x = Vector(up).cross(z)
    if x.length < 1e-6:
        x = Vector((1, 0, 0))
    x.normalize(); y = z.cross(x)
    o.matrix_world = Matrix.Translation((a + b) / 2) @ Matrix((x, y, z)).transposed().to_4x4()


def beam(name, a, b, w, h, mat, bevel=0.012):
    L = (Vector(b) - Vector(a)).length
    o = lib.beveled_box(name, (w, h, L), bevel=bevel, mat=mat)
    _orient(o, a, b)
    return o


def cyl(name, a, b, r, mat, bevel=0.004, verts=48):
    L = (Vector(b) - Vector(a)).length
    o = lib.beveled_cyl(name, r, L, bevel=bevel, mat=mat, verts=verts)
    _orient(o, a, b)
    return o


def cable(name, pts, r, mat):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o
