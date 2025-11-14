from engine import AdjudicationEngine
from models.adjudication import AdjudicationResult


def test_engine_demo():
    engine = AdjudicationEngine()
    result = engine.run_demo()
    assert isinstance(result, AdjudicationResult)
    assert result.winner_index >= 0
    assert result.winner_participant_id is not None

