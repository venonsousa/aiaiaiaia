from flask import Flask, request, jsonify, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_bcrypt import Bcrypt

import time
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

# =========================
# LOGIN SETUP
# =========================
login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

users_db = {}

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    return users_db.get(user_id)

# =========================
# CONFIG
# =========================
UNFOLLOW_LIMIT = 30
DELAY_MIN = 10
DELAY_MAX = 30
SAFE_LIST = ["amigo1"]

# =========================
# API MOCK (substituir depois)
# =========================
class APIClient:
    def __init__(self, token):
        self.token = token

    def get_followers(self):
        return ["user1", "user2", "user3"]

    def get_following(self):
        return ["user1", "user2", "user3", "user4", "user5"]

    def unfollow(self, username):
        print(f"[API] Unfollow {username}")

api = APIClient("fake-token")

# =========================
# LOGICA
# =========================
def get_non_followers(following, followers):
    return [u for u in following if u not in followers]

def apply_safe_list(users):
    return [u for u in users if u not in SAFE_LIST]

def run_unfollow(users):
    count = 0

    for user in users:
        if count >= UNFOLLOW_LIMIT:
            break

        api.unfollow(user)
        count += 1

        delay = random.randint(DELAY_MIN, DELAY_MAX)
        print(f"[INFO] Delay {delay}s")
        time.sleep(delay)

# =========================
# ROTAS
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# AUTH
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "dados inválidos"}), 400

    hashed = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    user = User(data["username"], data["username"], hashed)
    users_db[user.id] = user

    return jsonify({"status": "usuário criado"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = users_db.get(data["username"])

    if user and bcrypt.check_password_hash(user.password, data["password"]):
        login_user(user)
        return jsonify({"status": "logado"})

    return jsonify({"error": "credenciais inválidas"}), 401

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"status": "logout"})

# FEATURES
@app.route("/analyze")
@login_required
def analyze():
    followers = api.get_followers()
    following = api.get_following()

    non_followers = get_non_followers(following, followers)

    return jsonify({
        "followers": len(followers),
        "following": len(following),
        "not_following_back": non_followers
    })

@app.route("/unfollow")
@login_required
def unfollow():
    followers = api.get_followers()
    following = api.get_following()

    non_followers = get_non_followers(following, followers)
    filtered = apply_safe_list(non_followers)

    run_unfollow(filtered)

    return jsonify({"status": "unfollow executado"})

# =========================
if __name__ == "__main__":
    app.run(debug=True)
