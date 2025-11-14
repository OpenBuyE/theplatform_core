from models.purchase import Purchase
from models.user import User

def test_purchase_model():
    p = Purchase(
        id="123",
        user_id="u1",
        amount=10.5
    )
    assert p.amount == 10.5

def test_user_model():
    u = User(
        id="u1",
        email="test@example.com"
    )
    assert u.email == "test@example.com"
