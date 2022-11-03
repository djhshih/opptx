#!/usr/bin/env python3

import os, sys, glob
from PIL import Image

indir = sys.argv[1]

format_from = "tiff"
format_to = "jpeg"
dryrun = False
quality = 95

converted = {}

# convert images to jpeg
for infile in glob.glob(os.path.join(indir, "ppt", "media", "*" + format_from)):
    outfile = os.path.splitext(infile)[0] + "." + format_to
    if infile != outfile:
        try:
            with Image.open(infile) as im:
                if not dryrun:
                    if im.mode == "RGBA":
                        # original new image is in RGBA mode
                        # create new image with white background
                        im2 = Image.new("RGB", im.size, (255, 255, 255))
                        im.load()  # required for .split()
                        # paste old image onto new image with alpha channel as
                        # the mask (channel 3)
                        im2.paste(im, mask=im.split()[3])
                    else:
                        im2 = im
                    # write new file and delete old one
                    im2.save(outfile, "JPEG", quality=quality)
                    os.remove(infile)
                    print("Converted", infile)
                pass
            converted[os.path.basename(infile)] = os.path.basename(outfile)
        except OSError as e:
            print("Cannot image save as jpeg:", outfile)
            print(e)

# update image files in reference links
for infn in glob.glob(os.path.join(indir, "ppt", "slides", "_rels", "*.xml.rels")):
    content = None
    replaced = False
    with open(infn) as inf:
        content = inf.read()
        for oldfn in converted.keys():
            oldpath = os.path.join("media", oldfn)
            if content.find(oldpath) > 0:
                newpath = os.path.join("media", converted[oldfn])
                content = content.replace(oldpath, newpath)
                print("Updated", oldfn, "in", infn)
                replaced = True

    if replaced and not dryrun:
        # re-open in write mode and overwrite the content
        with open(infn, "w") as inf:
            inf.write(content)

