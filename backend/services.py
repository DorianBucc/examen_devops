from datetime import datetime, timedelta

from models import db, Score
from config import GAMES

# Cooldown en mémoire (suffisant pour l'exercice)
last_submit = {}


def validate_score(player, game, score):
    """
    Retourne (True, None) si le score est valide.
    Sinon retourne (False, "raison").
    """

    if game not in GAMES:
        return False, "unknown_game"

    if score < 0:
        return False, "negative_score"

    if score > GAMES[game]:
        return False, "max_score"

    key = f"{player}:{game}"

    if key in last_submit:
        if datetime.now() - last_submit[key] < timedelta(seconds=2):
            return False, "cooldown"

    return True, None


def add_score(player, game, score):
    """
    Ajoute un score et retourne son rang.
    """

    valid, reason = validate_score(player, game, score)

    if not valid:
        return None, reason

    last_submit[f"{player}:{game}"] = datetime.now()

    new_score = Score(
        player=player,
        game=game,
        score=score,
        created_at=datetime.now()
    )

    db.session.add(new_score)
    db.session.commit()

    leaderboard = (
        Score.query
        .filter_by(game=game)
        .order_by(Score.score.desc())
        .all()
    )

    for rank, entry in enumerate(leaderboard, start=1):
        if entry.id == new_score.id:
            return rank, None

    return None, "internal_error"

def sort_scores(scores):
    return sorted(
        scores,
        key=lambda s: s["score"],
        reverse=True
    )

def get_leaderboard(game, limit=10):

    if game not in GAMES:
        return None

    scores = (
        Score.query
        .filter_by(game=game)
        .order_by(Score.score.desc())
        .limit(limit)
        .all()
    )

    return sort_scores([
        {
            "player": s.player,
            "score": s.score
        }
        for s in scores
    ])[:limit]


def get_player_scores(player):

    scores = Score.query.filter_by(player=player).all()

    result = {}

    for score in scores:

        if score.game not in result:
            result[score.game] = score.score
        else:
            result[score.game] = max(result[score.game], score.score)

    return {
        "player": player,
        "scores": result
    }


def get_games():
    return GAMES