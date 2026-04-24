from search.ranking_strategy import ScoreRanking, AlphabeticalRanking, DateRanking

SAMPLE_RESULTS = [
    {"path": "C:/docs/zebra.txt", "extension": ".txt", "preview": "", "score": 1.5, "mtime": 1000},
    {"path": "C:/docs/apple.txt", "extension": ".txt", "preview": "", "score": 3.0, "mtime": 3000},
    {"path": "C:/docs/mango.txt", "extension": ".txt", "preview": "", "score": 2.0, "mtime": 2000},
]

def test_score_ranking():
    ranked = ScoreRanking().rank(SAMPLE_RESULTS)
    assert ranked[0]["score"] == 3.0
    assert ranked[1]["score"] == 2.0
    assert ranked[2]["score"] == 1.5

def test_alphabetical_ranking():
    ranked = AlphabeticalRanking().rank(SAMPLE_RESULTS)
    assert "apple" in ranked[0]["path"]
    assert "mango" in ranked[1]["path"]
    assert "zebra" in ranked[2]["path"]

def test_date_ranking():
    ranked = DateRanking().rank(SAMPLE_RESULTS)
    assert ranked[0]["mtime"] == 3000
    assert ranked[1]["mtime"] == 2000
    assert ranked[2]["mtime"] == 1000