from flask import Flask, request, redirect, jsonify
import sqlite3, string, random, os

app = Flask(__name__)
DB = os.environ.get("DB_PATH", "links.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS links (
        code TEXT PRIMARY KEY,
        url TEXT NOT NULL,
        clicks INTEGER DEFAULT 0)""")
    conn.commit()
    conn.close()

def make_code(n=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    if not url.startswith(("http://", "https://")):
        return jsonify(error="url must start with http:// or https://"), 400
    code = make_code()
    conn = get_db()
    conn.execute("INSERT INTO links (code, url) VALUES (?, ?)", (code, url))
    conn.commit()
    conn.close()
    return jsonify(code=code, short_url=request.host_url + code), 201

@app.route("/stats/<code>")
def stats(code):
    conn = get_db()
    row = conn.execute("SELECT * FROM links WHERE code = ?", (code,)).fetchone()
    conn.close()
    if row is None:
        return jsonify(error="not found"), 404
    return jsonify(code=code, url=row["url"], clicks=row["clicks"])

@app.route("/<code>")
def go(code):
    conn = get_db()
    row = conn.execute("SELECT url FROM links WHERE code = ?", (code,)).fetchone()
    if row is None:
        conn.close()
        return jsonify(error="not found"), 404
    conn.execute("UPDATE links SET clicks = clicks + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    return redirect(row["url"])

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)