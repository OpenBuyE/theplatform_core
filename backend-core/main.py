from engine import AdjudicationEngine

def run_demo():
    """
    Simple demo function to test the adjudication engine.
    """
    engine = AdjudicationEngine()
    result = engine.run_demo()
    print("Adjudication Engine Demo Result:")
    print(result)

if __name__ == "__main__":
    run_demo()
