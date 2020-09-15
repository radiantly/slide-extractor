import sys
from pathlib import Path

from PIL import Image, ImageStat
import imagehash
import cv2

from cropPdf import getCropCoords


DIFF_THRESHOLD = 5


def extractSlides(videoPath):
    cap = cv2.VideoCapture(videoPath.as_posix())
    totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    CHECK_PER_FRAMES = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"Reading {videoPath.as_posix()} ({CHECK_PER_FRAMES} fps)...")

    success, cv2_im = cap.read()

    slides = []
    slideHashes = []
    frameCount = 1
    prev_im_hash = None
    imageChanged = False

    while success:
        print(
            f"[{frameCount}/{totalFrames}] {len(slides)} slide{'s' if len(slides) != 1 else ''} found.\r",
            end="",
        )

        cv2_im = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im)

        if ImageStat.Stat(pil_im.convert("L")).mean[0] > 150:
            crop_box = getCropCoords(pil_im)
            pil_im = pil_im.crop(crop_box)

            # compare current frame to previous frame, save frame if sufficiently different
            prev_im_hash = imagehash.phash(pil_im) if not prev_im_hash else im_hash
            im_hash = imagehash.phash(pil_im)

            # Only add slide if
            if (
                imageChanged  # Slide change has been detected
                and im_hash - prev_im_hash < DIFF_THRESHOLD  # This frame is the same as the last
                and all(
                    im_hash - slideHash > DIFF_THRESHOLD for slideHash in slideHashes
                )  # Slide has not already been added to list
                and ImageStat.Stat(pil_im.convert("L")).mean[0]
                > 150  # Slide must be sufficiently bright
            ):
                # pil_im.save("frame{}.png".format(str(frameCount).zfill(3)), dpi=(72, 72))
                slides.append(pil_im)
                slideHashes.append(im_hash)
                imageChanged = False

            if im_hash - prev_im_hash > DIFF_THRESHOLD:
                imageChanged = True

        for i in range(CHECK_PER_FRAMES):  # skip frames
            success, cv2_im = cap.read()
        frameCount += CHECK_PER_FRAMES

    pdfFileName = input("Enter a name for the pdf file: ")
    saveLocation = Path.cwd() / f"{pdfFileName}.pdf"
    slides[0].save(saveLocation, "PDF", resolution=100.0, save_all=True, append_images=slides[1:])


def main():
    if len(sys.argv) != 2:
        raise Exception(f"Syntax: {sys.argv[0]} <name of video file/directory>")

    basePath = Path(sys.argv[1])

    if not basePath.exists():
        raise Exception(f"Cannot find {basePath.as_posix()}")

    if basePath.is_dir():
        for videoPath in [path for path in basePath.rglob("*") if path.suffix in [".mp4", ".mkv"]]:
            extractSlides(videoPath)
    else:
        extractSlides(basePath)


if __name__ == "__main__":
    main()
