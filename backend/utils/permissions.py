"""
Permission utilities for group-based access control.
"""

from flask_smorest import abort
from models import GroupUserModel

def check_group_membership(group_id, user_id):
    """Check if user is a member of the group."""
    group_user = GroupUserModel.query.filter_by(
        group_id=group_id, 
        user_id=user_id
    ).first()
    
    if not group_user:
        abort(403, message="Access denied. You are not a member of this group.")
    
    return group_user

def check_group_admin(group_id, user_id):
    """Check if user is an admin of the group."""
    group_user = check_group_membership(group_id, user_id)
    
    if not group_user.is_admin:
        abort(403, message="Access denied. Only group admins can perform this action.")
    
    return group_user

def check_expense_permission(expense, user_id):
    """Check if user can modify/delete an expense (admin or expense creator)."""
    group_user = check_group_membership(expense.group_id, user_id)
    
    # Allow action if user is admin or the one who created the expense
    if not (group_user.is_admin or expense.paid_by == user_id):
        abort(403, message="Access denied. Only group admins or expense creators can perform this action.")
    
    return group_user