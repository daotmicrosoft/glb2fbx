#!/usr/bin/env python
# -*- coding: utf-8 -*-

import docker
import os
import tempfile
import shutil

class Glb2Fbx:

    def __init__(
            self,
            input_file,
            output_file,
            blender_script="blender_glb2fbx.py",
            container_dir="/app/tmp",
            image="daotmicrosoft/blender:2.8_ubuntu"):

        self.input_file = input_file
        self.output_file = output_file
        self.blender_script = os.path.abspath(blender_script)
        self.image = image
        self.container_dir = container_dir

        self.client = docker.from_env()

        self._remap_dir_to_container()

    def _remap_dir_to_container(self):
        """
        Replace the input and output dirs with
        container_input/output_dir
        """
        # make a tmp dir, and link all files in that dir
        self._tmp = tempfile.mkdtemp()
        self._volume = {}
        self._volume[self._tmp] = {'bind': self.container_dir, 'mode': 'rw'}

        #link the input_file
        input_file_linked_path = os.path.join(self._tmp, "input_file.glb")
        print ("trying to link %s to %s"%(self.input_file, input_file_linked_path))
        try:
            os.symlink(self.input_file, input_file_linked_path)
        except:
            print ("Windows doesn't allow sym links. Copying file %s to %s"%(self.input_file, input_file_linked_path))
            shutil.copyfile(self.input_file, input_file_linked_path)


        #link the directory the container writes to
        output_dir_linked_path = os.path.join(self._tmp, "output_dir")
        try:
            os.symlink(os.path.dirname(self.output_file), output_dir_linked_path)
            self.copy_output = False
        except:
            print ("Windows doesn't allow sym links. Will copy output out of container.")
            output_dir_linked_path = self.container_dir
            self.copy_output = True

        #link the script
        blender_script_linked_path = os.path.join(self._tmp, "script.py")
        try:
            os.symlink(self.blender_script, blender_script_linked_path)
        except:
            print ("Windows doesn't allow sym links. Copying file %s to %s"%(self.blender_script, blender_script_linked_path))
            shutil.copyfile(self.blender_script, blender_script_linked_path)

        #now each of the input files are symbolically one dir, which is mapped
        #to the container

        #next, we replace the local tmp path with the container path for each
        #file
        self.input_arg = unixify_path(os.path.join(self.container_dir, os.path.basename(input_file_linked_path)))
        self.output_arg = unixify_path(os.path.join(output_dir_linked_path, os.path.basename(self.output_file)))
        self.script_arg = unixify_path(os.path.join(self.container_dir, os.path.basename(blender_script_linked_path)))

        


    def __call__(self):

        cmd = "./blender_app/blender -b -P %s -- %s %s" % (
            self.script_arg, self.input_arg, self.output_arg)


        
        print("Executing: %s in container." % cmd)


        _log = self.client.containers.run(
            self.image,
            cmd,
            stream=True,
            detach=False,
            volumes=self._volume)

        for line in _log:
            print(format_blender_log(line))

        print("Wrote: %s" % self.output_file)

        if self.copy_output:
            print ("----------> Copying %s to %s"%(self.output_arg, self.output_file))
            src = os.path.join(self._tmp, os.path.basename(self.output_file))
            shutil.copyfile(src,self.output_file)

        print ("Cleaning up.")
        shutil.rmtree(self._tmp)
        return self.output_file


def format_blender_log(line):
    return str(line).replace(
        "\\n",
        "").replace(
        "\\t",
        "   ").replace(
            "b'",
            "").replace(
                "'",
        "")
import argparse


def ends_with_ext(_path, test_ext):
    ext = os.path.splitext(_path)[1]
    return ext.lower() == test_ext.lower()


def _conform_path(_path):
    _path = unixify_path(_path)
    return os.path.abspath(_path)


def check_input_flag(args):
    args.input = os.path.abspath(args.input)
    print ('CHECKINT %s'%(os.path.isfile(args.input)))

    if not (os.path.isfile(args.input) and (ends_with_ext(args.input, ".glb") or \
        ends_with_ext(args.input, ".gltf"))):
        
        raise ValueError("Must pass in a valid path to a .glb or .gltf file.")

    args.input = _conform_path(args.input)
    return args


def check_output_flag(args):
    input_file_name_no_ext = os.path.splitext(os.path.basename(args.input))[0]
    
    if args.output:
        args.output = os.path.abspath(args.output)
        _base_dir = os.path.dirname(args.output)
        if not os.path.isdir(_base_dir):
            raise ValueError(
                "Must pass in a valid path to write the .fbx file.")

        # may be a path or a path and file
        ext = os.path.splitext(args.output)[1]
        if ext:
            # has a file extension
            if ext.lower() != ".fbx":
                raise ValueError("Output file extension must be .fbx")
        # is a dir:
        else:
            if not os.path.isdir(args.output):
                raise ValueError(
                    "Must pass in a valid directory path to --output.")

            # valid dir, so let's construct the output file name.

            args.output = os.path.join(
                args.output, input_file_name_no_ext+".fbx")

    else:
        args.output = os.path.join(
            os.path.dirname(
                args.input), input_file_name_no_ext+".fbx")

    args.output = _conform_path(args.output)

    return args


def _parse_args(args):
    args = check_input_flag(args)
    args = check_output_flag(args)
    return args


def unixify_path(path_name):
    return path_name.replace("\\", "/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts a .gltf or .glb file to .fbx. Uses blender 2.8 in a docker container to do the conversion.")
    parser.add_argument("input",
                        help="Path and file name to glb or gltf file to convert. Example: ../mydir/myfile.glb")

    parser.add_argument("--output", "-o", help="Full path and file name to glb or gltf file to convert. Example: ../mydir/myfile.fbx, or ../mydir")
    args = _parse_args(parser.parse_args())
    print (args)

    #do the business
    print ("Converting %s to %s"%(args.input, args.output))
    Glb2Fbx(args.input, args.output)()


