import io
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module


@pytest.fixture
def client(tmp_path):
    app_module.app.config["UPLOAD_FOLDER"] = str(tmp_path)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client


def test_allowed_file():
    assert app_module.allowed_file("photo.jpg")
    assert app_module.allowed_file("photo.PNG")
    assert not app_module.allowed_file("document.pdf")
    assert not app_module.allowed_file("noextension")


def test_index_get_renders_upload_form(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"UPLOAD A B/W IMAGE TO COLORIZE" in response.data


def test_index_post_without_file_returns_error(client):
    response = client.post("/", data={})
    assert response.status_code == 400
    assert b"No file selected" in response.data


def test_index_post_with_disallowed_extension_returns_error(client):
    data = {"file": (io.BytesIO(b"not an image"), "document.pdf")}
    response = client.post("/", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert b"Only PNG/JPG images are allowed" in response.data


def test_index_post_with_missing_model_returns_503(client, monkeypatch):
    def fake_colorize(*args, **kwargs):
        raise app_module.ModelNotFoundError("Missing model file(s): test.caffemodel")

    monkeypatch.setattr(app_module, "colorize_image", fake_colorize)

    data = {"file": (io.BytesIO(b"fake image bytes"), "photo.jpg")}
    response = client.post("/", data=data, content_type="multipart/form-data")
    assert response.status_code == 503
    assert b"Missing model file" in response.data


def test_unreadable_image_is_not_left_on_disk(client, tmp_path):
    data = {"file": (io.BytesIO(b"not really a jpeg"), "photo.jpg")}
    response = client.post("/", data=data, content_type="multipart/form-data")
    assert response.status_code in (400, 503)  # 503 when the model isn't downloaded
    assert os.listdir(tmp_path) == []


def test_prune_uploads_removes_only_old_files(tmp_path):
    old = tmp_path / "old_colorized.jpg"
    new = tmp_path / "new_colorized.jpg"
    keep = tmp_path / ".gitkeep"
    for path in (old, new, keep):
        path.write_bytes(b"x")
    two_hours_ago = time.time() - 2 * 60 * 60
    os.utime(old, (two_hours_ago, two_hours_ago))
    os.utime(keep, (two_hours_ago, two_hours_ago))

    app_module.prune_uploads(str(tmp_path), max_age=60 * 60)

    assert sorted(os.listdir(tmp_path)) == [".gitkeep", "new_colorized.jpg"]


def test_upload_prunes_old_files(client, tmp_path, monkeypatch):
    stale = tmp_path / "stale_colorized.jpg"
    stale.write_bytes(b"x")
    two_hours_ago = time.time() - 2 * 60 * 60
    os.utime(stale, (two_hours_ago, two_hours_ago))
    monkeypatch.setattr(app_module, "colorize_image", lambda src, dst: dst)

    data = {"file": (io.BytesIO(b"fake image bytes"), "photo.jpg")}
    response = client.post("/", data=data, content_type="multipart/form-data")
    assert response.status_code == 302
    assert not stale.exists()
