import sys
import bpy


#clean out the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()


print ("%s: Input file: %s"%(sys.argv[0],sys.argv[-2]))
print ("%s: Ouput file: %s"%(sys.argv[0],sys.argv[-1]))
bpy.ops.import_scene.gltf(filepath=sys.argv[-2])
print ("bob")
bpy.ops.export_scene.fbx(filepath=sys.argv[-1], path_mode='COPY', embed_textures=True)

