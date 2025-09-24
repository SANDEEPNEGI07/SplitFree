# 💰 SplitFree - Expense Splitting Application

A modern, full-stack expense splitting application built with Flask and React, designed to help friends and groups manage shared expenses with ease.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)

## 🌟 Overview

SplitFree simplifies expense management for groups by automatically calculating who owes whom and how much. Whether you're splitting restaurant bills, shared apartment expenses, or travel costs, SplitFree handles the complex calculations and keeps everyone informed about their financial obligations.

## 🚀 Features

## 📱 Key Features

| Feature | Description |
|---------|-------------|
| 🔐 **Authentication** | Secure login/signup with JWT tokens |
| 👥 **Group Management** | Create groups, add/remove members |
| 💳 **Expense Tracking** | Add expenses, automatic equal splitting |
| 💰 **Balance Calculation** | Real-time who-owes-whom calculations |
| 📊 **Settlement System** | Record payments between members |
| 📱 **Responsive Design** | Works on desktop and mobile |

- 👥 **Create Groups** - Organize expenses with roommates, friends, or travel buddies
- 💳 **Add Expenses** - Record shared costs and automatically split them equally
- 💰 **Track Balances** - See who owes what at a glance
- 📊 **Settle Up** - Record payments and keep balances updated
- 🔒 **Stay Secure** - JWT authentication keeps your data safe

## 🛠️ Tech Stack

### Backend
- 🐍 **Python** - Programming language
- 🌶️ **Flask** - Web framework
- 🗄️ **SQLAlchemy** - Database ORM
- 🔐 **JWT** - Authentication
- 📚 **Swagger** - API documentation
- 🐳 **Docker** - Containerization

### Frontend  
- ⚛️ **React 18** - UI library
- 🎨 **CSS3** - Styling
- 🌐 **Axios** - HTTP client
- 🛣️ **React Router** - Navigation

### Database
- 💾 **SQLite** - Development database
- 🐘 **PostgreSQL** - Production ready

## ⚠️ Limitations

- Equal splits only (no custom percentages)
- No expense categories
- Manual payment recording

## 🚀 Coming Soon

- 📊 Custom split ratios
- 🏷️ Expense categories  
- 📸 Receipt photos
- 🔔 Push notifications

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup
1. Clone the repository
   ```bash
   git clone <repository-url>
   cd splitwise
   ```

2. Create and activate virtual environment
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install Python dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional)
   ```bash
   # Create .env file for custom configurations
   echo "JWT_SECRET_KEY=your-secret-key" > .env
   ```

5. Initialize database
   ```bash
   flask db upgrade
   ```

6. Start the backend server
   ```bash
   python app.py
   ```
   Backend will run on `http://localhost:5000`

### Frontend Setup
1. Navigate to frontend directory
   ```bash
   cd frontend
   ```

2. Install dependencies
   ```bash
   npm install
   ```

3. Start the development server
   ```bash
   npm start
   ```
   Frontend will run on `http://localhost:3000`

## 🚦 Quick Start
1. Start the backend server (`python app.py`)
2. Start the frontend server (`cd frontend && npm start`)
3. Open `http://localhost:3000` in your browser
4. Register a new account or login
5. Create groups and start splitting expenses!

## 📋 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /refresh` - Refresh JWT token

### Groups
- `GET /group` - Get user's groups
- `POST /group` - Create new group
- `GET /group/{id}` - Get group details
- `DELETE /group/{id}` - Delete group
- `POST /group/{id}/user` - Add user to group
- `DELETE /group/{id}/user/{user_id}` - Remove user from group

### Expenses
- `GET /group/{id}/expense` - Get group expenses
- `POST /group/{id}/expense` - Create new expense
- `GET /group/{id}/expense/{expense_id}` - Get expense details
- `DELETE /group/{id}/expense/{expense_id}` - Delete expense

### Users
- `GET /user` - Search users
- `GET /user/{id}` - Get user details

## 🔐 Security Features
- JWT-based authentication with refresh tokens
- Authorization checks for all group/expense operations
- Users can only access groups they are members of
- Password hashing with secure algorithms
- Protected API endpoints with role-based access

## 🏗️ Project Structure
```
splitwise/
├── app.py                 # Flask application entry point
├── db.py                  # Database configuration
├── requirements.txt       # Python dependencies
├── migrations/           # Database migration files
├── models/              # SQLAlchemy models
│   ├── user.py
│   ├── group.py
│   ├── expense.py
│   └── ...
├── resources/           # API route handlers
│   ├── user.py
│   ├── group.py
│   ├── expense.py
│   └── ...
├── schemas.py           # Marshmallow schemas
└── frontend/           # React application
    ├── src/
    │   ├── components/    # Reusable UI components
    │   ├── pages/        # Page components
    │   ├── services/     # API service layer
    │   ├── contexts/     # React contexts
    │   ├── hooks/        # Custom hooks
    │   └── utils/        # Utility functions
    ├── public/           # Static assets
    └── package.json      # Frontend dependencies
```

## 🚀 Development Scripts

### Backend
```bash
python app.py              # Start development server
flask db migrate           # Create new migration
flask db upgrade           # Apply migrations
```

### Frontend
```bash
npm start                  # Start development server
npm run build             # Build for production
npm test                  # Run tests
```

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License
This project is licensed under the MIT License.


## 📞 Support
For issues and questions, please open an issue on GitHub.
