from engine import AdjudicationEngine

def test_engine_demo():
    engine = AdjudicationEngine()
    result = engine.run_demo()
    assert result["status"] == "OK"
