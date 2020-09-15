# Automatically generate pdf files from the screenshots folder
# Built for KK. Created by @radiantly. Tested by @PangorroHammer.

# Before running, install the pillow image library using
# pip install pillow

# Python 3.6+ required. Run using:
# python scr2pdf.py

from PIL import Image
from pathlib import Path

def main():
    screenshotFolder = Path.home() / "Pictures" / "Screenshots"

    start = int(input("Enter the starting screenshot number: "))
    end = int(input("Enter the ending screenshot number: "))

    screenshotNames = [screenshotFolder / f"Screenshot ({i}).png" for i in range(start, end + 1)]

    imageList = [Image.open(image).convert("RGB") for image in screenshotNames if image.exists()]

    if not len(imageList):
        raise "No images could be found."
    print(f"{len(imageList)} images found.")
    
    pdfFileName = input("Enter a name for the pdf file: ")

    saveLocation = Path.home() / "Documents" / f"{pdfFileName}.pdf"

    imageList[0].save(saveLocation, "PDF" ,resolution=100.0, save_all=True, append_images=imageList[1:])

    print(f"Successfully saved to {str(saveLocation)}")

if __name__ == "__main__":
    main()
