from services import validate_score, sort_scores

def test_valid_score():
    valid, error = validate_score(
        "AAA",
        "pacman",
        1000
    )

    assert valid is True
    assert error is None

def test_score_too_high():
    valid, error = validate_score(
        "AAA",
        "pacman",
        10000000
    )

    assert valid is False
    assert error == "max_score"


def test_leaderboard_sorted():

    scores = [
        {"player": "A", "score": 50},
        {"player": "B", "score": 100},
        {"player": "C", "score": 75},
    ]

    result = sort_scores(scores)

    assert result[0]["player"] == "B"
    assert result[1]["player"] == "C"
    assert result[2]["player"] == "A"