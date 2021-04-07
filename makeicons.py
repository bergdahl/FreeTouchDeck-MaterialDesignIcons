#!/usr/bin/env python3

"""makeicons.py: Creates 75x75 pixels BMP files out of MaterialDesign icons."""

__author__ = "Jonny Bergdahl"
__copyright__ = "Copyright 2021, Bergdahl IT AB"

import os
from os.path import basename
import glob
from pathlib import Path
import shutil
import fnmatch
from git import Git
import pyvips
from zipfile import ZipFile
from PIL import Image, ImageOps
import numpy

BUILD_DIR = 'build'
MDI_PATH = 'MaterialDesign/svg'
ICON_DIR = 'icons'
MDI_REPO = 'https://github.com/Templarian/MaterialDesign.git'

print("makeicons executing")
build_dir = os.path.join(os.path.curdir, BUILD_DIR)
icons_dir = os.path.join(os.path.curdir, ICON_DIR)
svg_path = os.path.join(build_dir, MDI_PATH)

if os.path.exists(build_dir):
    # Clean up old work directory
    print(f'Cleaning work directory {build_dir}')
    shutil.rmtree(build_dir)
if os.path.exists(build_dir):
    # Clean up old work directory
    print(f'Cleaning icons directory {icons_dir}')
    shutil.rmtree(icons_dir)

print('Creating work directories')
os.mkdir(build_dir)
os.mkdir(icons_dir)

print(f'Cloning MaterialDesign repository into {build_dir}')
repo = Git(build_dir)
result = repo.clone(MDI_REPO)

svg_files_count = len(fnmatch.filter(os.listdir(svg_path), '*.svg'))
print(f'Found {svg_files_count} files in {svg_path}')

print('Creating zip file icons.zip')
with ZipFile('icons.zip', 'w') as zip:

    # Create bitmaps
    for svg_file in glob.iglob(os.path.join(svg_path, '*.svg')):
        file_name = Path(os.path.basename(svg_file)).stem
        print(f'Processing {file_name}.svg', end = '')

        # Load SVG file and save as PNG for PIL
        svg = pyvips.Image.thumbnail(svg_file, 75, height=75)
        output_png_name = os.path.join(build_dir, 'temp.png')
        svg.write_to_file(output_png_name)
        print('.', end = '')

        # Use PIL top open file
        png = Image.open(output_png_name)
        print('.', end = '')

        # Convert to numpy arrays for image manipulation
        rgba = numpy.array(png)
        # Set all non transparent pixels to white
        rgba[rgba[...,-1] != 0] = [255,255,255,255]
        print('.', end = '')
        # Set all transparent pixels to black
        rgba[rgba[...,-1] == 0] = [0,0,0,0]
        print('.', end = '')

        # Convert array back to Image
        img = Image.fromarray(rgba)
        print('.', end = '')

        # Convert ot 24-bit RGB
        bmp = img.convert(mode='RGB', colors=24)
        print('.', end = '')

        # Save as BMP
        output_file_name = os.path.join(icons_dir, f'{file_name}.bmp')
        print(f' => {output_file_name}')
        bmp.save(output_file_name, 'BMP')

        # Add to zip
        zip.write(output_file_name, basename(output_file_name))

print('Cleaning up')
shutil.rmtree(build_dir)
shutil.rmtree(icons_dir)
print('All done!')
