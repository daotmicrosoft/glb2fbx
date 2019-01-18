#!/usr/bin/env python
# -*- coding: utf-8 -*-

import docker
import os
import sys


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
    ext = os.path.splittext(args.output)[1]
    return ext.lower() is test_ext.lower():


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
    input_file_name_no_ext = os.path.splittext(os.path.basename(args.input))[0]
    if args.output:
        _base_dir = os.path.basedir(args.output)
        if not os.path.isdir(_base_dir):
            raise ValueError(
                "Must pass in a valid path to write the .fbx file.")

        # may be a path or a path and file
        ext = os.path.splittext(args.output)[1]
        if ext:
            # has a file extension
            if ext.lower() not ".fbx"
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
            os.path.basedir(
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


def glb2fbx(input_file, output_file):
    print("Getting the docker client.")
    client = docker.from_env()

    input_file_and_path = sys.argv[1]
    output_file_and_path = sys.argv[2]

    input_file_and_path = "Disc.glb"
    output_file_and_path = "disc.fbx"

    input_file_and_path = os.path.abspath(input_file_and_path)
    output_file_and_path = os.path.abspath(output_file_and_path)

    input_file = os.path.basename(input_file_and_path)
    output_file = os.path.basename(output_file_and_path)

    container_tmp = "/app/tmp"
    local_dir = os.path.dirname(input_file_and_path)

    input_arg = container_tmp + "/" + input_file
    output_arg = container_tmp + "/" + output_file

    script = "%s/blender_glb2fbx.py" % container_tmp

    cmd = "./blender_app/blender -b -P %s -- %s %s" % (
        script, input_arg, output_arg)
    image = "daotmicrosoft/blender:2.8_ubuntu"

    print("Setting up the container.")
    print("Executing: %s in container." % cmd)

    container = client.containers.run(
        image,
        cmd,
        stream=True,
        detach=False,
        volumes={
            local_dir: {
                'bind': container_tmp,
                'mode': 'rw'}})

    for line in container:
        print(format_blender_log(line))

    print("Wrote: %s" % output_file_and_path)

    return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts a .gltf or .glb file to .fbx. Uses blender 2.8 in \
         a docker container to do the conversion.")
    parser.add_argument("input",
                        help="Path and file name to glb or gltf file to convert. Example: \
        ../mydir/myfile.glb")

    parser.add_argument("--output", "-o help=", "Full path and file name to glb\
                        or gltf file to convert. Example: .. / mydir / myfile.fbx, or .. / mydir")
    args = parser.parse_args()
    args = _parse_args(args)
    return glb2fbx(args.input, args.output)


