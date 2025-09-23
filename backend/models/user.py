from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    #relationship with groups
    groups = db.relationship("GroupModel", back_populates="users", secondary="group_user")

    #relationship with expense
    expenses_paid = db.relationship("ExpenseModel", back_populates="payer", lazy="dynamic")

    #relationship with splits
    splits = db.relationship("ExpenseSplitModel", back_populates="users", cascade="all, delete, delete-orphan")