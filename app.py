import os, secrets, sqlite3
from flask import Flask, request, redirect, url_for, render_template, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "mklamk")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "videos")
DB_PATH = os.path.join(BASE_DIR, "videos.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")
ALLOWED = {".mp4", ".webm", ".mov", ".m4v", ".ogg"}

os.makedirs(VIDEO_DIR, exist_ok=True)

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

with db() as con:
    con.execute("""CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE NOT NULL,
        filename TEXT NOT NULL,
        original_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

def admin_ok():
    return request.form.get("password") == ADMIN_PASSWORD or request.headers.get("X-Admin-Password") == ADMIN_PASSWORD

@app.get("/")
def index():
    return redirect(url_for("admin"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    message = ""
    share_url = ""
    if request.method == "POST":
        if not admin_ok():
            message = "Sai mật khẩu admin."
        else:
            f = request.files.get("video")
            if not f or not f.filename:
                message = "Chưa chọn video."
            else:
                ext = os.path.splitext(f.filename)[1].lower()
                if ext not in ALLOWED:
                    message = "Định dạng không được hỗ trợ."
                else:
                    token = secrets.token_urlsafe(24)
                    filename = token + ext
                    f.save(os.path.join(VIDEO_DIR, filename))
                    with db() as con:
                        con.execute(
                            "INSERT INTO videos(token,filename,original_name) VALUES(?,?,?)",
                            (token, filename, secure_filename(f.filename))
                        )
                    share_url = url_for("watch", token=token, _external=True)
                    message = "Tạo link thành công."
    return render_template("admin.html", message=message, share_url=share_url)

@app.get("/v/<token>")
def watch(token):
    with db() as con:
        row = con.execute("SELECT filename FROM videos WHERE token=?", (token,)).fetchone()
    if not row:
        abort(404)
    return render_template("video.html", token=token)

@app.get("/stream/<token>")
def stream(token):
    with db() as con:
        row = con.execute("SELECT filename FROM videos WHERE token=?", (token,)).fetchone()
    if not row:
        abort(404)
    return send_from_directory(VIDEO_DIR, row["filename"], conditional=True)

@app.get("/api/admin/list")
def api_list():
    if request.headers.get("X-Admin-Password") != ADMIN_PASSWORD:
        return jsonify(error="Unauthorized"), 401
    with db() as con:
        rows = con.execute("SELECT token,original_name,created_at FROM videos ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=False)
