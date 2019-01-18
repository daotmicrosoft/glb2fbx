#!/usr/bin/env python
# -*- coding: utf-8 -*-

import docker
import os
import sys


class Glb2Fbx:

    def __init__(
            self,
            input_file,
            output_file,
            blender_script="blender_glb2fbx.py",
            image="daotmicrosoft/blender:2.8_ubuntu",
            container_input_dir="/app/tmp",
            container_output_dir="/app/tmp1",
            container_work_dir="/app"):

        self.input_file = input_file
        self.output_file = output_file
        self.blender_script = os.path.abspath(blender_script)
        self.image = image
        self.container_input_dir = container_input_dir
        self.container_output_dir = container_output_dir
        self.container_work_dir = container_work_dir

        self.client = docker.from_env()

        self._remap_dir_to_container()

    def _remap_dir_to_container(self):
        """
        Replace the input and output dirs with
        container_input/output_dir
        """
        self._volumes = {}

        input_file_name = os.path.basename(self.input_file)
        input_file_dir_name = os.path.dirname(self.input_file)
        self.input_arg = os.path.join(
            self.container_input_dir, input_file_name)
        self._volumes[input_file_dir_name] = {
            'bind': self.container_input_dir,
            'mode': 'rw'}

        output_file_name = os.path.basename(self.output_file)
        output_file_dir_name = os.path.dirname(self.output_file)
        self.output_arg = os.path.join(
            self.container_output_dir, output_file_name)
        self._volumes[output_file_dir_name] = {
            'bind': self.container_output_dir,
            'mode': 'rw'}

        blender_script_file_name = os.path.basename(self.blender_script)
        self.script_arg = os.path.join(
            self.container_work_dir, blender_script_file_name)
        self._volumes[blender_script_file_name] = {
            'bind': self.container_work_dir,
            'mode': 'rw'}

    def __call__(self):

        cmd = "./blender_app/blender -b -P %s -- %s %s" % (
            self.script_arg, self.input_arg, self.output_arg)

        print("Executing: %s in container." % cmd)

        _log = self.client.containers.run(
            self.image,
            cmd,
            stream=True,
            detach=False,
            volumes=self._volumes)

        for line in _log:
            print(format_blender_log(line))

        print("Wrote: %s" % self.output_file)

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
    ext = os.path.splitext(args.output)[1]
    return ext.lower() is test_ext.lower()


def _conform_path(_path):
    _path = unixify_path(_path)
    return os.path.abspath(_path)


def check_input_flag(args):
    if not os.path.isfile(
        args.input) and (
        ends_with_ext(
            args.input,
            ".glb") or ends_with_ext(
                args.input,
            ".gltf")):
        raise ValueError("Must pass in a valid path to a .glb or .gltf file.")

    args.input = _conform_path(args.input)
    return args


def check_output_flag(args):
    input_file_name_no_ext = os.path.splitext(os.path.basename(args.input))[0]
    if args.output:
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
                args.output, input_file_name_no_ext, ".fbx")

    else:
        args.output = os.path.join(
            os.path.dirname(
                args.input),
            input_file_name_no_ext,
            ".fbx")

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
    args = parser.parse_args()
    args = _parse_args(args)

    cmd_obj = Glb2Fbx(args.input, args.output)
    cmd_obj()
