# glb2fbx
Convert gltf or glb file to fbx using a blender 2.8 docker image.

This tool uses Docker to run Blender2.8. Inside blender, the .glb or .gltf model is imported then exported as an .fbx file. Once complete, the container is shut down.

The repo comes with a .glb file for testing.

Currently does not support materials and textures.

## Requirements
- Docker client. If you don't have Docker running on your mahcine, install it by going to [https://docs.docker.com/](https://docs.docker.com/)
- Python 3.7+

## Usage
### Examples
- *python glb2fbx.py Disc.glb -o Disc.fbx* (Will look for Disc.glb in the current directory, and write Disc.fbx into the current directory.)

- *python glb2fbx.py /Users/me/myfile.glb* (Will look for myfile.glb in /Users/me/. and write /Users/me/myfile.fbx.)
