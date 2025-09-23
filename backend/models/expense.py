from db import db

class ExpenseModel(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    paid_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    date = db.Column(db.Date, nullable=True)

    groups = db.relationship("GroupModel", back_populates="expenses")
    payer = db.relationship("UserModel", back_populates="expenses_paid")
    splits = db.relationship(
        "ExpenseSplitModel",
        back_populates="expenses",
        cascade="all, delete, delete-orphan",
        order_by="ExpenseSplitModel.id"
    )