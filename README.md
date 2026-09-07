# xnhauhentai

A minimal Flask app to upload and serve videos with short token-based sharing links.

This repository has been reorganized for clarity. Key points:

- Backend code is under src/
- Templates are under templates/
- Uploaded videos are stored in videos/ (add to .gitignore for local dev)
- Database file videos.db is created in project root

Quick start (recommended using a virtualenv):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit ADMIN_PASSWORD and SECRET_KEY
python app.py
```

Open http://127.0.0.1:5000/admin to upload videos.

Project layout (important files):

```
app.py               # small wrapper that imports src.app and runs the server
src/                 # backend source
  app.py             # main Flask application
templates/           # Jinja2 templates (admin.html, video.html)
videos/              # uploaded video files (ignored by git)
videos.db            # SQLite database (ignored by git)
requirements.txt
.env.example
.gitignore
README.md
```
