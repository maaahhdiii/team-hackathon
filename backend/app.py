import sqlite3
import os
import html
import datetime
import jwt
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps

import pathlib

# Serve frontend from ./static when running inside Docker
_STATIC = pathlib.Path(__file__).parent / "static"
app = Flask(
    __name__,
    static_folder=str(_STATIC) if _STATIC.exists() else None,
    static_url_path="",
)
CORS(app, origins="*")



# ─── Vulnerability Feature Flags ────────────────────────────────────────────
VULNS = {
    "sqli": False,
    "xss": False,
    "auth_bypass": False,
}

FLAG_SECRET = "admin-secret"
JWT_STRONG_SECRET = "s3cur3-pr0duct10n-s3cr3t-k3y-2024!"
JWT_WEAK_SECRET = "secret"

DATABASE = os.path.join(os.path.dirname(__file__), "database.db")


# ─── Database Helpers ────────────────────────────────────────────────────────
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            INSERT OR IGNORE INTO users (username, password) VALUES
                ('alice', 'password123'),
                ('bob', 'hunter2'),
                ('admin', 'sup3rs3cr3t');

            INSERT OR IGNORE INTO products (name, description, category) VALUES
                ('Widget Pro', 'Industrial-grade widget for professionals.', 'hardware'),
                ('DataSync', 'Sync your data across all devices seamlessly.', 'software'),
                ('CableKit', 'Complete cable management solution.', 'hardware'),
                ('CloudStore', 'Unlimited cloud storage for your files.', 'software'),
                ('DevBoard', 'Development board for embedded projects.', 'hardware'),
                ('ApiGateway', 'Managed API gateway for microservices.', 'software');
            """
        )
        db.commit()


# ─── JWT Helpers ─────────────────────────────────────────────────────────────
def create_token(username: str) -> str:
    secret = JWT_WEAK_SECRET if VULNS["auth_bypass"] else JWT_STRONG_SECRET
    payload = {
        "sub": username,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ", 1)[1]

        if VULNS["auth_bypass"]:
            # Vulnerable: try weak secret first, then accept any decodable token
            try:
                payload = jwt.decode(token, JWT_WEAK_SECRET, algorithms=["HS256"])
                request.current_user = payload.get("sub", "unknown")
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                # Also accept tokens signed with the strong secret
                try:
                    payload = jwt.decode(
                        token, JWT_STRONG_SECRET, algorithms=["HS256"]
                    )
                    request.current_user = payload.get("sub", "unknown")
                    return f(*args, **kwargs)
                except jwt.InvalidTokenError:
                    return jsonify({"error": "Invalid token"}), 401
        else:
            try:
                payload = jwt.decode(
                    token, JWT_STRONG_SECRET, algorithms=["HS256"]
                )
                request.current_user = payload.get("sub", "unknown")
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401

    return decorated


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.route("/")
def root():
    """Serve the frontend landing page when running in Docker."""
    if app.static_folder:
        from flask import send_from_directory
        return send_from_directory(app.static_folder, "index.html")
    return jsonify({"message": "VulnLab API running. Open the frontend separately."}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "vulns": dict(VULNS)})


# --- Login -------------------------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    db = get_db()

    if VULNS["sqli"]:
        # ⚠ VULNERABLE: raw string concatenation — injectable
        query = (
            f"SELECT * FROM users WHERE username = '{username}' "
            f"AND password = '{password}'"
        )
        cursor = db.execute(query)
    else:
        # ✅ SAFE: parameterized query
        cursor = db.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        )

    user = cursor.fetchone()
    if user is None:
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_token(user["username"])
    return jsonify({"token": token, "username": user["username"]})


# --- Search ------------------------------------------------------------------
@app.route("/search", methods=["GET"])
@require_auth
def search():
    q = request.args.get("q", "")
    db = get_db()

    if VULNS["sqli"]:
        # ⚠ VULNERABLE: raw string concatenation — injectable
        query = f"SELECT * FROM products WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"
        cursor = db.execute(query)
    else:
        # ✅ SAFE: parameterized query
        cursor = db.execute(
            "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?",
            (f"%{q}%", f"%{q}%"),
        )

    rows = cursor.fetchall()
    results = [dict(r) for r in rows]
    return jsonify({"results": results, "count": len(results)})


# --- Comments ----------------------------------------------------------------
@app.route("/comments", methods=["GET"])
@require_auth
def get_comments():
    db = get_db()
    cursor = db.execute(
        "SELECT * FROM comments ORDER BY created_at DESC LIMIT 50"
    )
    rows = cursor.fetchall()

    comments = []
    for row in rows:
        author = row["author"]
        body = row["body"]
        if not VULNS["xss"]:
            # ✅ SAFE: escape HTML entities
            author = html.escape(author)
            body = html.escape(body)
        # ⚠ VULNERABLE when xss=True: raw unsanitized content returned
        comments.append(
            {
                "id": row["id"],
                "author": author,
                "body": body,
                "created_at": row["created_at"],
            }
        )

    return jsonify({"comments": comments})


@app.route("/comment", methods=["POST"])
@require_auth
def post_comment():
    data = request.get_json(silent=True) or {}
    author = data.get("author", "").strip()
    body = data.get("body", "").strip()

    if not author or not body:
        return jsonify({"error": "Author and body are required"}), 400
    if len(body) > 1000:
        return jsonify({"error": "Comment too long (max 1000 chars)"}), 400

    db = get_db()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    db.execute(
        "INSERT INTO comments (author, body, created_at) VALUES (?, ?, ?)",
        (author, body, now),
    )
    db.commit()
    return jsonify({"message": "Comment posted successfully"}), 201


# --- Feature Flags -----------------------------------------------------------
@app.route("/flags/activate", methods=["POST"])
def flags_activate():
    data = request.get_json(silent=True) or {}
    if data.get("secret") != FLAG_SECRET:
        return jsonify({"error": "Forbidden: incorrect secret"}), 403

    vuln = data.get("vuln", "")
    if vuln not in VULNS:
        return jsonify({"error": f"Unknown vulnerability flag: '{vuln}'"}), 400

    VULNS[vuln] = True
    return jsonify({"message": f"Vulnerability '{vuln}' ACTIVATED", "vulns": dict(VULNS)})


@app.route("/flags/deactivate", methods=["POST"])
def flags_deactivate():
    data = request.get_json(silent=True) or {}
    if data.get("secret") != FLAG_SECRET:
        return jsonify({"error": "Forbidden: incorrect secret"}), 403

    vuln = data.get("vuln", "")
    if vuln not in VULNS:
        return jsonify({"error": f"Unknown vulnerability flag: '{vuln}'"}), 400

    VULNS[vuln] = False
    return jsonify({"message": f"Vulnerability '{vuln}' DEACTIVATED", "vulns": dict(VULNS)})


# ─── Bootstrap ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8001, debug=False)
