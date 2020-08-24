# -*- coding: utf-8 -*-
# @Author: johan
# @Date:   2019-02-15 01:47:00
# @Last Modified by:   radiantly
# @Last Modified time: 2020-08-20 19:54:57

import os
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

from PIL import Image
import imagehash
import cv2

CHECK_PER_FRAMES = 45  # check per 30 frames (i.e. 1 frame per sec for 30 fps video)
DIFF_THRESHOLD = 3


def extractSlides(args):
    videoPath, currentWorker, totalWorkers = args
    cap = cv2.VideoCapture(videoPath.as_posix())
    totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    startFrame = totalFrames * currentWorker // totalWorkers
    endFrame = totalFrames * (currentWorker + 1) // totalWorkers
    currentFrame = startFrame

    cap.set(cv2.CAP_PROP_POS_FRAMES, startFrame)
    success, cv2_im = cap.read()

    slides = []
    prev_im_hash = None
    imageChanged = False

    while success and currentFrame < endFrame:
        cv2_im = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im)

        # compare current frame to previous frame, save frame if sufficiently different
        prev_im_hash = imagehash.phash(pil_im) if not prev_im_hash else im_hash
        im_hash = imagehash.phash(pil_im)

        if imageChanged and im_hash - prev_im_hash < DIFF_THRESHOLD:
            slides.append(pil_im)
            imageChanged = False

        if im_hash - prev_im_hash > DIFF_THRESHOLD:
            imageChanged = True

        for i in range(CHECK_PER_FRAMES):  # skip frames
            success, cv2_im = cap.read()

        currentFrame += CHECK_PER_FRAMES
    cap.release()
    return slides


def slideManager(videoPath):
    workers = os.cpu_count()

    print(f"Reading {videoPath.as_posix()} with {workers} workers...")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        # lastSlide = None
        allSlides = []
        for slides in executor.map(
            extractSlides, [(videoPath, i, workers) for i in range(workers)]
        ):
            if not slides:
                continue
            if (
                allSlides
                and imagehash.phash(allSlides[-1]) - imagehash.phash(slides[0]) < DIFF_THRESHOLD
            ):
                slides = slides[1:]
            allSlides.extend(slides)

    pdfFileName = input("Enter a name for the pdf file: ")
    saveLocation = Path.cwd() / f"{pdfFileName}.pdf"
    allSlides[0].save(
        saveLocation, "PDF", resolution=100.0, save_all=True, append_images=allSlides[1:]
    )


def main():
    if len(sys.argv) != 2:
        raise Exception(f"Syntax: {sys.argv[0]} <name of video file/directory>")

    basePath = Path(sys.argv[1])

    if not basePath.exists():
        raise Exception(f"Cannot find {basePath.as_posix()}")

    if basePath.is_dir():
        for videoPath in [path for path in basePath.rglob("*") if path.suffix in [".mp4", ".mkv"]]:
            slideManager(videoPath)
    else:
        slideManager(basePath)


if __name__ == "__main__":
    main()
