# Image Colorization 

This application enables users to upload black and white images and receive colorized versions of those images. Follow the instructions below to set up and run the app locally.

## Prerequisites

Ensure you have Python installed on your machine. This app has been tested with Python 3.8. You can download it from [python.org](https://www.python.org/downloads/).

## Installation

1. **Clone the Repository**

   First, clone this repository to your local machine:

   ```bash
   git clone <https://github.com/vxkram/image-colorization>
   cd <image-colorization>
   ```

2. **Download Model Files**

   Download the necessary model files required by the application:

   - **colorization_deploy_v2.prototxt**: [Download from Github](https://github.com/richzhang/colorization/blob/caffe/colorization/models/colorization_deploy_v2.prototxt)
   - **colorization_release_v2.caffemodel**: [Download from Dropbox](https://www.dropbox.com/s/dx0qvhhp5hbcx7z/colorization_release_v2.caffemodel?dl=1)
   -  **pts_in_hull.npy**: [Download from GitHub](https://github.com/richzhang/colorization/blob/caffe/colorization/resources/pts_in_hull.npy)

3. **Install Dependencies**

   Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

   `requirements.txt` contains the following packages:

   ```
   blinker==1.8.2
   click==8.1.7
   colorama==0.4.6
   Flask==3.0.3
   itsdangerous==2.2.0
   Jinja2==3.1.4
   MarkupSafe==3.0.1
   numpy==2.1.2
   opencv-python==4.10.0.84
   Werkzeug==3.0.4
   ```

## Running the App

To run the application on your local machine:

1. **Start the Flask Server**

   Run the following command in the terminal:

   ```bash
   python app.py
   ```

2. **Access the Application**

   Open your web browser and navigate to `http://localhost:5000`. You should see the interface for uploading black and white images.

3. **Upload and Colorize Images**

   - Click the "Choose File" button to select a black and white image from your computer.
   - Click the "Colorize Image" button to upload your image and view the colorized result.

## Before and After

![Before Colorization](/uploads/eagle.jpg)
![After Colorization](/uploads/colorized_eagle.jpg)

## Features

- Upload black and white images.
- Automatic colorization using deep learning models.
- Easy-to-use web interface.

