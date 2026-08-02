import os

import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
PROTOTXT = os.path.join(MODELS_DIR, "colorization_deploy_v2.prototxt")
POINTS = os.path.join(MODELS_DIR, "pts_in_hull.npy")
MODEL = os.path.join(MODELS_DIR, "colorization_release_v2.caffemodel")

_net = None
_pts = None


class ModelNotFoundError(RuntimeError):
    pass


def _load_model():
    global _net, _pts

    if _net is not None:
        return _net, _pts

    missing = [p for p in (PROTOTXT, POINTS, MODEL) if not os.path.isfile(p)]
    if missing:
        raise ModelNotFoundError(
            "Missing model file(s): "
            + ", ".join(os.path.basename(p) for p in missing)
            + ". Run `python scripts/download_models.py` first."
        )

    net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
    pts = np.load(POINTS)

    class8 = net.getLayerId("class8_ab")
    conv8 = net.getLayerId("conv8_313_rh")
    pts = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]

    _net, _pts = net, pts
    return _net, _pts


def colorize_image(input_path, output_path):
    net, _ = _load_model()

    image = cv2.imread(input_path)
    if image is None:
        raise ValueError(f"Could not read image: {input_path}")

    scaled = image.astype("float32") / 255.0
    lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)

    resized = cv2.resize(lab, (224, 224))
    L = cv2.split(resized)[0]
    L -= 50

    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
    ab = cv2.resize(ab, (image.shape[1], image.shape[0]))

    L = cv2.split(lab)[0]
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)
    colorized = (255 * colorized).astype("uint8")

    cv2.imwrite(output_path, colorized)
    return output_path
