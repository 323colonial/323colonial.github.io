"""Denoise one baked lightmap EXR with OpenImageDenoise via the compositor.

    blender -b --factory-startup -P denoise.py -- in.exr out.exr
"""
import bpy, sys
src, dst = sys.argv[-2], sys.argv[-1]
sc = bpy.context.scene
im = bpy.data.images.load(src)
w, h = im.size
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
ng = bpy.data.node_groups.new("dn", "CompositorNodeTree")
sc.compositing_node_group = ng
ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
n_im = ng.nodes.new("CompositorNodeImage"); n_im.image = im
n_dn = ng.nodes.new("CompositorNodeDenoise")
n_out = ng.nodes.new("NodeGroupOutput")
ng.links.new(n_im.outputs[0], n_dn.inputs[0])
ng.links.new(n_dn.outputs[0], n_out.inputs[0])
sc.render.image_settings.file_format = "OPEN_EXR"
sc.render.image_settings.color_depth = "32"
sc.render.filepath = dst
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
bpy.ops.render.render(write_still=True)
print("OK")
