from db import db

class GroupUserModel(db.Model):
    __tablename__ = "group_user"

    id = db.Column(db.Integer(), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False) 
    
    # Ensure unique group-user combinations
    __table_args__ = (db.UniqueConstraint('group_id', 'user_id', name='unique_group_user'),)
    
