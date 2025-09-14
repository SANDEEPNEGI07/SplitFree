from db import db

class GroupUserModel(db.Model):
    __tablename__ = "group_user"

    id = db.Column(db.Integer(), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=False, nullable=False)