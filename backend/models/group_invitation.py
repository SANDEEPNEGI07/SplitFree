from db import db
from datetime import datetime, timedelta
import uuid


class GroupInvitationModel(db.Model):
    __tablename__ = "group_invitations"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    invite_token = db.Column(db.String(36), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    invited_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Relationships
    group = db.relationship("GroupModel", backref="invitations")
    invited_by = db.relationship("UserModel", foreign_keys=[invited_by_user_id])
    
    def __init__(self, group_id, email, invited_by_user_id, **kwargs):
        super(GroupInvitationModel, self).__init__(**kwargs)
        self.group_id = group_id
        self.email = email.lower().strip()  # Normalize email
        self.invited_by_user_id = invited_by_user_id
        self.invite_token = str(uuid.uuid4())
        # Invitations expire after 7 days
        self.expires_at = datetime.utcnow() + timedelta(days=7)
    
    @property
    def is_expired(self):
        """Check if invitation has expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_used(self):
        """Check if invitation has been used"""
        return self.used_at is not None
    
    @property
    def is_valid(self):
        """Check if invitation is still valid (not expired and not used)"""
        return not self.is_expired and not self.is_used
    
    def mark_as_used(self):
        """Mark invitation as used"""
        self.used_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<GroupInvitation {self.email} -> Group {self.group_id}>'