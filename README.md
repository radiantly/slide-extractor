# Slide-extractor

A nifty python script to extract slides from videos and save it as a pdf. Python3+ required.

### `slide-extractor.py`

This is the newest iteration of the script and uses the [Decord](https://github.com/dmlc/decord) library to read frames from the video.

```zsh
# Install dependencies
pip install decord pillow tqdm imagehash

# Run script
python slide-extractor.py <NameofVideoFile/Directory>
```

If you have trouble installing Decord, follow the installation instructions on their page [here](https://github.com/dmlc/decord#install-from-source).

<details><summary>Older versions</summary>

### `slide-extractor-opencv.py` (legacy)

This script uses opencv to read frames from the video. This is twice as slow when compared with the previous script.

```zsh
# Install dependencies
pip install opencv-contrib-python pillow imagehash

# Run script
python slide-extractor-opencv.py <NameofVideoFile/Directory>
```

### `slide-extractor-opencv-multiprocessing.py` (legacy)

This script uses opencv to read frames from the video. This is faster than the other opencv script, but a major drawback is that no progress bar or indication of processing is shown to the user.

```zsh
# Install dependencies
pip install opencv-contrib-python pillow imagehash

# Run script
python slide-extractor-opencv-multiprocessing.py <NameofVideoFile/Directory>
```

</details>

Original script from [johan456789/slide-extractor](https://github.com/johan456789/slide-extractor)
