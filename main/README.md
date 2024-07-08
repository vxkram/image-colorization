# Image Colorization
## Overview
This Python project utilizes OpenCV and deep learning to colorize black and white images. The colorization is achieved by leveraging a pre-trained deep neural network model. The model takes a grayscale image as input and predicts the corresponding colorized version.

## Model and Resources
1. Model files:
   - colorization_deploy_v2.prototxt: [Download](colorization_deploy_v2.prototxt)
   - pts_in_hull.npy: [Download](https://github.com/richzhang/colorization/blob/caffe/colorization/resources/pts_in_hull.npy)
   - colorization_release_v2.caffemodel: [Download](https://www.dropbox.com/s/dx0qvhhp5hbcx7z/colorization_release_v2.caffemodel?dl=1)

## Installation
1. Install dependenies:
   ``` cmd
   pip install numpy opencv-python
   ```
2. Download model files.
3. Place the downloaded files in a folder named "model".
4. Place the image to be colorized in a foler named "images".
5. Make sure both the mentioned folders are in the same directory as the Python file.

## Usage 
1. Run the Python script:
   ``` cmd
   python colorize.py -i path/to/your/image.jpg
   ```
   Replace path/to/your/image.jpg with the path to the black and     white image you want to colorize.
2. The script will display the original and colorized images side by side

## Project Structure
- **/model**: Directory containing the pre-trained model files.
- **/images**: Directory containing the black and white images.
- **colorize.py**: Main script for image colorization.
