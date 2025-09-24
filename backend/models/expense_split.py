from db import db

class ExpenseSplitModel(db.Model):
    __tablename__ = "expense_splits"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    expense_id = db.Column(db.Integer, db.ForeignKey("expenses.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    expenses = db.relationship("ExpenseModel", back_populates="splits")
    users = db.relationship("UserModel", back_populates="splits")