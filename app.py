import os
import time
import uuid

from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from colorize import ModelNotFoundError, colorize_image

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
app.config["UPLOAD_MAX_AGE"] = 60 * 60  # seconds an upload/result is kept


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


def prune_uploads(folder, max_age):
    """Delete uploads and results older than max_age seconds, so the folder can't grow forever."""
    cutoff = time.time() - max_age
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if name.startswith(".") or not os.path.isfile(path):
            continue
        if os.path.getmtime(path) < cutoff:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass  # another request removed it first


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    file = request.files.get("file")
    if not file or file.filename == "":
        return render_template("index.html", error="No file selected."), 400

    if not allowed_file(file.filename):
        return render_template("index.html", error="Only PNG/JPG images are allowed."), 400

    prune_uploads(app.config["UPLOAD_FOLDER"], app.config["UPLOAD_MAX_AGE"])

    unique_id = uuid.uuid4().hex[:8]
    original_filename = f"{unique_id}_{secure_filename(file.filename)}"
    original_path = os.path.join(app.config["UPLOAD_FOLDER"], original_filename)
    file.save(original_path)

    colorized_filename = f"{unique_id}_colorized.jpg"
    colorized_path = os.path.join(app.config["UPLOAD_FOLDER"], colorized_filename)

    try:
        colorize_image(original_path, colorized_path)
    except ModelNotFoundError as exc:
        os.remove(original_path)
        return render_template("index.html", error=str(exc)), 503
    except ValueError as exc:
        os.remove(original_path)
        return render_template("index.html", error=str(exc)), 400

    return redirect(url_for("result", original=original_filename, colorized=colorized_filename))


@app.route("/result")
def result():
    return render_template(
        "result.html",
        original=request.args.get("original"),
        colorized=request.args.get("colorized"),
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
