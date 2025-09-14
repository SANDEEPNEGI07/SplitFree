from db import db

class GroupModel(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(80), nullable=False)

    users = db.relationship("UserModel", back_populates="groups", secondary="group_user")