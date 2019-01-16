import docker
import os
import sys

print ("Getting the docker client.")
client = docker.from_env()

input_file_and_path = sys.argv[1]
output_file_and_path = sys.argv[2]



input_file_and_path = os.path.abspath(input_file_and_path)
output_file_and_path = os.path.abspath(output_file_and_path)

input_file = os.path.basename(input_file_and_path)
output_file = os.path.basename(output_file_and_path)

container_tmp = "/app/tmp"
local_dir = os.path.dirname(input_file_and_path)

input_arg = container_tmp + "/" + input_file
output_arg = container_tmp + "/" + output_file

script = "%s/blender_glb2fbx.py"%container_tmp

cmd = "./blender_app/blender -b -P %s -- %s %s "%(script, input_arg, output_arg)
image = "daotmicrosoft/blender:2.8_ubuntu"

print ("Setting up the container.")
print ("Executing: %s in container."%cmd)
container = client.containers.run(image, cmd, detach=True, volumes={local_dir: {'bind': container_tmp, 'mode': 'rw'}})
print (container.logs())



#glb2fbx -i <file> -o <outputfile>

#make the container and mount the input, output, and script dirs
#/Users/daveotte/work/docker_demo