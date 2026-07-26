from codepulse.scoring import grade_for_score, overall_score


def test_overall_score_perfect():
    results = {
        cat: {"score": 100}
        for cat in ["structure", "git", "dependencies", "docs", "tests", "smells"]
    }
    assert overall_score(results) == 100


def test_overall_score_missing_categories_still_normalizes():
    results = {"structure": {"score": 80}, "docs": {"score": 40}}
    score = overall_score(results)
    assert 0 <= score <= 100


def test_overall_score_empty():
    assert overall_score({}) == 0


def test_grade_boundaries():
    assert grade_for_score(95) == "A"
    assert grade_for_score(85) == "B"
    assert grade_for_score(75) == "C"
    assert grade_for_score(65) == "D"
    assert grade_for_score(40) == "F"
