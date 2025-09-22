# Splitwise API

A Flask-based expense splitting application with JWT authentication.

## Features
- User registration/login with email
- Group management with auto-membership
- Expense tracking with equal splits
- Settlement recording
- Balance calculations
- Complete expense history

## Installation
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run migrations: `flask db upgrade`
5. Start app: `python app.py`

## API Endpoints
- Authentication: `/register`, `/login`, `/logout`
- Groups: `/group` (CRUD operations)
- Expenses: `/group/{id}/expense`
- Settlements: `/group/{id}/settlement`
- Balances: `/group/{id}/balances`
- History: `/group/{id}/history`
