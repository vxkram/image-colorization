"""Downloads the pretrained Zhang et al. colorization model files into models/.

Source: https://github.com/richzhang/colorization
"""
import os
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

FILES = {
    "colorization_deploy_v2.prototxt": (
        "https://raw.githubusercontent.com/richzhang/colorization/"
        "caffe/colorization/models/colorization_deploy_v2.prototxt"
    ),
    "pts_in_hull.npy": (
        "https://raw.githubusercontent.com/richzhang/colorization/"
        "caffe/colorization/resources/pts_in_hull.npy"
    ),
    "colorization_release_v2.caffemodel": (
        "https://www.dropbox.com/s/dx0qvhhp5hbcx7z/"
        "colorization_release_v2.caffemodel?dl=1"
    ),
}


def download(name, url, dest_dir):
    dest = os.path.join(dest_dir, name)
    if os.path.isfile(dest):
        print(f"[skip] {name} already exists")
        return

    print(f"[download] {name} ...")
    urllib.request.urlretrieve(url, dest)
    print(f"[done] {name} ({os.path.getsize(dest) / 1e6:.1f} MB)")


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    for name, url in FILES.items():
        download(name, url, MODELS_DIR)
    print("\nAll model files are in place.")


if __name__ == "__main__":
    main()
