import sys
import bpy

print ("%s: Input file: %s"%(sys.argv[0],sys.argv[-2]))
print ("%s: Ouput file: %s"%(sys.argv[0],sys.argv[-1]))
bpy.ops.import_scene.gltf(filepath=sys.argv[-2])
bpy.ops.export_scene.fbx(filepath=sys.argv[-1])