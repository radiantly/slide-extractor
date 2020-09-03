import sys
from pathlib import Path

import numpy
import fitz
import cv2
from PIL import Image


cropPoints = []


def getCropCoords(pilIm):
    global cropPoints

    # If crop coordinates already exist, return them.
    if len(cropPoints) >= 2:
        (crop_left, crop_top), (crop_right, crop_bottom) = cropPoints[:2]
        return (crop_left, crop_top, crop_right, crop_bottom)

    # Handle clicks in the imshow window
    def clickHandler(event, x, y, flags, param):
        # If mouse click, record coordinates
        if event == cv2.EVENT_LBUTTONDOWN:
            cropPoints.append((x, y))

            if len(cropPoints) >= 2:
                print(f"Crop points: {cropPoints}")

    # Convert PIL image to cv2 image
    cvImage = cv2.cvtColor(numpy.array(pilIm), cv2.COLOR_RGB2BGR)

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", clickHandler)
    while len(cropPoints) < 2:
        cv2.imshow("image", cvImage)
        cv2.waitKey(50)
    cv2.destroyWindow("image")
    return getCropCoords(pilIm)


def processPDF(pdfPath):
    croppedImages = []
    doc = fitz.open(pdfPath)
    for i in range(len(doc)):
        for img in doc.getPageImageList(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            pilIm = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            croppedImages.append(pilIm.crop(getCropCoords(pilIm)))

    return croppedImages


def savePDF(images: list, defaultPath: Path = None):
    pdfFileName = input("Enter a name for the pdf file: ").replace(".pdf", "")
    if not pdfFileName and defaultPath:
        saveLocation = defaultPath
    else:
        saveLocation = Path.cwd() / f"{pdfFileName}.pdf"
    images[0].save(saveLocation, "PDF", resolution=100.0, save_all=True, append_images=images[1:])


def main():
    if len(sys.argv) != 2:
        raise Exception(f"Syntax: {sys.argv[0]} PDF_FILE")

    pdfPath = Path(sys.argv[1])
    if not pdfPath.exists():
        raise Exception(f"PDF {pdfPath.as_posix()} does not exist")

    savePDF(processPDF(pdfPath), defaultPath=pdfPath)


if __name__ == "__main__":
    main()
