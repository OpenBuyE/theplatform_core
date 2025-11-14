from .database import DatabaseService
from models.purchase import Purchase
from models.supplier import Supplier
from models.adjudication import AdjudicationResult
from engine import AdjudicationEngine

class AdjudicationService:
    def __init__(self):
        self.db = DatabaseService()
        self.engine = AdjudicationEngine()

    def run_for_purchase(self, purchase_id: str):
        """
        Runs the adjudication process for a specific purchase.
        """

        # Load purchase
        purchase_data = self.db.fetch_by_id("purchases", purchase_id)
        if not purchase_data.data:
            raise ValueError("Purchase not found.")
        purchase = Purchase(**purchase_data.data[0])

        # Load all suppliers
        suppliers_data = self.db.fetch_all("suppliers")
        suppliers = [Supplier(**s) for s in suppliers_data.data]

        # Run engine
        result = self.engine.adjudicate(purchase, suppliers)

        # Save result
        result_model = AdjudicationResult(
            purchase_id=purchase.id,
            chosen_supplier_id=result["supplier_id"],
            score=result["score"],
            explanations=result.get("explanations", [])
        )

        self.db.insert("adjudications", result_model.dict())
        return result_model
