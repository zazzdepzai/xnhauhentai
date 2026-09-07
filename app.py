from src.app import app

if __name__ == "__main__":
    host = __import__("os").environ.get("HOST", "0.0.0.0")
    port = int(__import__("os").environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=False)
