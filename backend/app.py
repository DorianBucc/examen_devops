import os

from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, generate_latest

from config import GAMES
from models import db
from services import (
    add_score,
    get_leaderboard,
    get_player_scores,
)

app = Flask(__name__)


DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "C:/Users/bucch/source/repos/examen_devops/backend/data/database.db"
)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Prometheus
submitted = Counter(
    "scores_submitted_total",
    "Nombre de scores acceptés"
)

rejected = Counter(
    "scores_rejected_total",
    "Nombre de scores rejetés",
    ["reason"]
)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/games")
def games():
    return jsonify(GAMES)


@app.post("/scores")
def post_score():

    data = request.get_json()

    rank, error = add_score(
        data["player"],
        data["game"],
        data["score"]
    )

    if error:
        rejected.labels(reason=error).inc()

        codes = {
            "unknown_game": 400,
            "negative_score": 400,
            "max_score": 422,
            "cooldown": 429,
        }

        return jsonify({"error": error}), codes.get(error, 400)

    submitted.inc()

    return jsonify({"rank": rank}), 201


@app.get("/leaderboard/<game>")
def leaderboard(game):

    limit = min(int(request.args.get("limit", 10)), 100)

    leaderboard = get_leaderboard(game, limit)

    if leaderboard is None:
        return jsonify({"error": "Unknown game"}), 404

    return jsonify(leaderboard)


@app.get("/players/<player>")
def player(player):
    return jsonify(get_player_scores(player))


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype="text/plain"
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )