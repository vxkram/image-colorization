import os

import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
PROTOTXT = os.path.join(MODELS_DIR, "colorization_deploy_v2.prototxt")
POINTS = os.path.join(MODELS_DIR, "pts_in_hull.npy")
MODEL = os.path.join(MODELS_DIR, "colorization_release_v2.caffemodel")
MAX_SIDE = 2048  # longest side, in pixels, that colorize_image works at

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


def colorize_image(input_path, output_path, max_side=MAX_SIDE):
    net, _ = _load_model()

    image = cv2.imread(input_path)
    if image is None:
        raise ValueError(f"Could not read image: {input_path}")

    # The network only sees a 224x224 copy, so a huge photo gains no colour,
    # just memory (about 80 MB per megapixel). Work at max_side at most.
    height, width = image.shape[:2]
    if max(height, width) > max_side:
        scale = max_side / max(height, width)
        image = cv2.resize(image, (round(width * scale), round(height * scale)), interpolation=cv2.INTER_AREA)
        height, width = image.shape[:2]

    lab = cv2.cvtColor(image.astype("float32") / 255.0, cv2.COLOR_BGR2LAB)
    del image

    L = cv2.resize(lab, (224, 224))[:, :, 0]
    L -= 50

    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

    # Reuse the full-size Lab array: keep its L, swap in the predicted a/b,
    # and convert in place instead of building new full-size copies.
    lab[:, :, 1:] = cv2.resize(ab, (width, height))
    cv2.cvtColor(lab, cv2.COLOR_LAB2BGR, dst=lab)
    np.clip(lab, 0, 1, out=lab)
    lab *= 255

    cv2.imwrite(output_path, lab.astype("uint8"))
    return output_path
