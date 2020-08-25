# -*- coding: utf-8 -*-
# @Author: johan
# @Date:   2019-02-15 01:47:00
# @Last Modified by:   radiantly
# @Last Modified time: 2020-08-20 19:54:57

import sys
from pathlib import Path

from PIL import Image
import imagehash
from tqdm import trange
from decord import VideoReader, cpu

CHECK_PER_FRAMES = 30  # check per 30 frames (i.e. 1 frame per sec for 30 fps video)
DIFF_THRESHOLD = 3


def extractSlides(videoPath):
    print(f"Reading {videoPath.as_posix()}...")

    vr = VideoReader(videoPath.as_posix(), ctx=cpu(0))

    slides = []
    frameCount = 1
    prevImageHash = None
    imageChanged = False

    for i in trange(0, len(vr), CHECK_PER_FRAMES):
        frame = vr[i].asnumpy()
        pilImage = Image.fromarray(frame)
        prevImageHash = imagehash.average_hash(pilImage) if not prevImageHash else currentImageHash
        currentImageHash = imagehash.average_hash(pilImage)
        imageDiff = currentImageHash - prevImageHash

        if imageChanged and imageDiff < DIFF_THRESHOLD:
            slides.append(pilImage)
            imageChanged = False

        if imageDiff > DIFF_THRESHOLD:
            imageChanged = True

    return slides


def slideManager(videoPaths):
    savedPdfs = []
    for videoPath in videoPaths:
        slides = extractSlides(videoPath)
        if not slides:
            continue
        pdfFileName = f"{videoPath.stem}.pdf"
        slides[0].save(
            pdfFileName, "PDF", resolution=100.0, save_all=True, append_images=slides[1:],
        )
        savedPdfs.append(pdfFileName)
        print(f"Successfully saved {pdfFileName}")
    return savedPdfs


def renamePdfs(pdfNames):
    pdfPaths = [Path(pdfName) for pdfName in pdfNames if Path(pdfName).exists()]
    if not pdfPaths:
        return
    print("\nPress [ENTER] to leave as is and [CTRL+C] to exit.")
    for pdfPath in pdfPaths:
        newName = input(f"New name for {pdfPath.name}: ").replace(".pdf", "")
        if not newName.strip():
            continue
        pdfPath.rename(f"{newName}.pdf")


def main():
    if len(sys.argv) != 2:
        raise Exception(f"Syntax: {sys.argv[0]} <name of video file/directory>")

    basePath = Path(sys.argv[1])

    if not basePath.exists():
        raise Exception(f"Cannot find {basePath.as_posix()}")

    savedPdfs = slideManager(
        [path for path in basePath.rglob("*") if path.suffix in [".mp4"]]
        if basePath.is_dir()  # if directory, process all mp4 videos in it. Else use basepath as videopath.
        else [basePath]
    )

    renamePdfs(savedPdfs)


if __name__ == "__main__":
    main()

