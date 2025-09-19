from db import db

class SettlementModel(db.Model):
    __tablename__ = "settlements"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)

    paid_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    paid_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)

    # Relationships
    payer = db.relationship("UserModel", foreign_keys=[paid_by])
    receiver = db.relationship("UserModel", foreign_keys=[paid_to])
    group = db.relationship("GroupModel")
