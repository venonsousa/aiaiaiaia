from flask import Flask, jsonify, request

import time
import random

app = Flask(__name__)

# =========================
# CONFIG
# =========================
UNFOLLOW_LIMIT = 10
DELAY_MIN = 2
DELAY_MAX = 5
SAFE_LIST = ["amigo1"]

# =========================
# MOCK API (SIMULADO)
# =========================
class APIClient:
    def get_followers(self):
        return ["user1", "user2", "user3"]

    def get_following(self):
        return ["user1", "user2", "user3", "user4", "user5"]

    def unfollow(self, username):
        print(f"[API] Unfollow {username}")

api = APIClient()

# =========================
# LÓGICA
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
        time.sleep(delay)

# =========================
# FRONTEND (HTML INLINE)
# =========================
@app.route("/")
def index():
    return """
    <html>
    <head>
        <title>Unfollow Tool</title>
        <style>
            body {
                font-family: Arial;
                background: #111;
                color: white;
                text-align: center;
            }
            button {
                padding: 10px 20px;
                margin: 10px;
                border: none;
                background: #00ffcc;
                cursor: pointer;
            }
            button:hover {
                background: #00ccaa;
            }
        </style>
    </head>
    <body>
        <h1>Unfollow Tool</h1>

        <button onclick="analyze()">Analisar</button>
        <button onclick="runUnfollow()">Executar Unfollow</button>

        <div id="result"></div>

        <script>
            async function analyze() {
                const res = await fetch('/analyze');
                const data = await res.json();

                document.getElementById('result').innerHTML =
                    "Followers: " + data.followers + "<br>" +
                    "Following: " + data.following + "<br>" +
                    "Não seguem de volta: " + data.not_following_back.length;
            }

            async function runUnfollow() {
                const res = await fetch('/unfollow');
                const data = await res.json();
                alert(data.status);
            }
        </script>
    </body>
    </html>
    """

# =========================
# ROTAS API
# =========================
@app.route("/analyze")
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
def unfollow():
    followers = api.get_followers()
    following = api.get_following()

    non_followers = get_non_followers(following, followers)
    filtered = apply_safe_list(non_followers)

    run_unfollow(filtered)

    return jsonify({"status": "Unfollow executado com sucesso"})

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
