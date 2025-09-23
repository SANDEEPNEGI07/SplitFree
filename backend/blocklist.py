"""
blocklist.py

This file just contain the blocklist of the JWT tokens. It will be imported by app and the logout resourse so that tokens can be added to the bloacklist when the user logs out.
"""

BLOCKLIST = set()