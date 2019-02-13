#!/usr/bin/env python
# -*- coding: utf-8 -*-

import docker
import tempfile
import shutil
from pathlib import Path
import argparse


class Glb2Fbx:

    def __init__(
            self,
            input_source_glb_file,
            output_fbx_file,
            input_blender_script_file="glb_to_fbx_blender.py",
            input_container_dir="/app/tmp",
            output_container_dir="/app/tmp1",
            image="daotmicrosoft/blender:2.8_ubuntu",
            debug=False):
        """
        Manage the data ingress and egress from the docker container. Files
        prefixed with 'input_*_file' are consolidated into a created
        'input_tmp_dir'. Then the container mounts the tmp_dir as
        'input_container_dir'. The container will also mount the directory where
        'output_*_file' will be written.
        """
        # blow away the tmp dirs when we're done?
        self.debug = debug
        try:
            self.client = docker.from_env()
            self.client.ping()
        except:
            raise Exception("Make sure docker desktop client is running. Cannot reach docker server.")
        self.image = image

        # consolidate input files to 'input_tmp_dir'
        #
        # using resolve, since mac os returns a symbolic link,
        # which docker cannot access.
        self.input_tmp_dir = Path(tempfile.mkdtemp()).resolve().__str__()
        self.input_container_dir = input_container_dir
        self.output_container_dir = output_container_dir

        # map input/output_container_dir to input_tmp_dir, our directory of
        self.volumes = dict()
        self.volumes[self.input_tmp_dir] = {
            'bind': self.input_container_dir, 'mode': 'rw'}
        self.volumes[Path(output_fbx_file).absolute().parent.__str__()] = {
            'bind': self.output_container_dir, 'mode': 'rw'}

        # check and consolodate the input files into tmp dir, and swap out paths
        # for container input path (which are mapped to where the files are
        # consolidated to)
        self.check_input_file(input_source_glb_file, ['.glb', '.gltf'])
        self.input_source_glb_file = self.containerize_file(
            input_source_glb_file)

        self.check_input_file(input_blender_script_file, '.py')
        self.input_blender_script_file = self.containerize_file(
            input_blender_script_file)

        # check and swap out path for container output path
        self.check_output_file_dir(output_fbx_file, '.fbx')
        self.returned_output_fbx_file = output_fbx_file
        self.output_fbx_file = self.swap_directory_paths(
            output_fbx_file, output_container_dir)

    def containerize_file(self, source_file):
        source_file = Path(source_file).absolute().__str__()
        dest_file = Path(self.input_tmp_dir, Path(source_file).name).__str__()
        print("Copying %s to %s" % (source_file, dest_file))
        shutil.copyfile(source_file, dest_file)
        return self.swap_directory_paths(source_file, self.input_container_dir)

    def __call__(self):
        """
        Do the business.

        """
        cmd = "./blender_app/blender -b -P %s -- %s %s" % (
            self.input_blender_script_file,
            self.input_source_glb_file,
            self.output_fbx_file)
        print("Executing: %s in container." % cmd)

        _log = self.client.containers.run(
            self.image,
            cmd,
            stream=True,
            detach=False,
            volumes=self.volumes)

        for line in _log:
            print(line.decode('UTF-8'), end="")

        if self.debug:
            print("Did you not get what you wanted? Here's the docker cmd to debug:")
            print("docker run -itv %s:%s %s bash" % (self.input_tmp_dir.lower(), self.input_container_dir, self.image))
            print("Run this inside the container:")
            print(cmd)
        else:
            print("Cleaning up.")
            shutil.rmtree(self.input_tmp_dir)

        return self.returned_output_fbx_file

    def check_input_file(self, input_file, extension):
        _error = "%s either doesn't exist, or is wrong type." % input_file
        if isinstance(extension, list):
            for ext in extension:
                if self.is_valid_file(input_file, ext):
                    return True
            raise ValueError(_error)
        else:
            if not self.is_valid_file(input_file, extension):
                raise ValueError(_error)

    def check_output_file_dir(self, _file, extension):
        if not self.is_file_type(_file, extension):
            raise ValueError("%s needs to end with: %s" % (_file, extension))
        if not Path(_file).parent.exists():
            raise ValueError("%s does not exist." % Path(_file).parent)

    def is_file_type(self, _file, extension):
        return _file.lower().endswith(extension.lower())

    def is_valid_file(self, _file, extension):
        return Path(_file).exists() and self.is_file_type(_file, extension)

    def swap_directory_paths(self, source_file, dest_path):
        """
        Replace the path to 'source_file' with 'dest_path'
        """
        return Path(dest_path, Path(source_file).name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts a .gltf or .glb file to .fbx. Uses blender 2.8 in a docker container to do the "
                    "conversion.")

    parser.add_argument("input_glb_file",
                        help="Path and file name to glb or gltf file to convert.")

    parser.add_argument("output_fbx_file",
                        help="Full path and file name to glb or gltf file to convert.")

    parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help="Do not clean up tmp dir, and print out commands to debug in docker.")
    parser.set_defaults(debug=False)

    args = parser.parse_args()
    Glb2Fbx(
        args.input_glb_file,
        args.output_fbx_file,
        debug=args.debug)()
