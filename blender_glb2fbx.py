import sys
import bpy

def main():
    #clean out the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


    print ("%s: Input file: %s"%(sys.argv[0],sys.argv[-2]))
    print ("%s: Ouput file: %s"%(sys.argv[0],sys.argv[-1]))
    bpy.ops.import_scene.gltf(filepath=sys.argv[-2])
    bpy.ops.export_scene.fbx(filepath=sys.argv[-1])

if __name__ == "__main__":