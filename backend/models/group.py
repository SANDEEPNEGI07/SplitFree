from db import db
import random
import string

class GroupModel(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(80), nullable=False)
    invite_code = db.Column(db.String(20), unique=True, nullable=False)
    is_public = db.Column(db.Boolean, default=True, nullable=False)

    users = db.relationship("UserModel", back_populates="groups", secondary="group_user")
    expenses = db.relationship(
        "ExpenseModel", 
        back_populates="groups",
        cascade="all, delete" ,
        lazy="dynamic")
    settlements = db.relationship(
        "SettlementModel",
        back_populates="group",
        cascade="all, delete",
        lazy="dynamic")
    
    def __init__(self, **kwargs):
        super(GroupModel, self).__init__(**kwargs)
        if not self.invite_code:
            self.invite_code = self.generate_unique_invite_code()
    
    @classmethod
    def generate_invite_code(cls):
        """Generate a random invite code like SPLIT-ABC123"""
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        numbers = ''.join(random.choices(string.digits, k=3))
        return f"SPLIT-{letters}{numbers}"
    
    @classmethod
    def generate_unique_invite_code(cls):
        """Generate a unique invite code that doesn't exist in database"""
        while True:
            code = cls.generate_invite_code()
            if not cls.query.filter_by(invite_code=code).first():
                return code
    
    def regenerate_invite_code(self):
        """Generate a new invite code for this group"""
        self.invite_code = self.generate_unique_invite_code()
        return self.invite_code