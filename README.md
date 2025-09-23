# Splitwise - Expense Splitting Application

A full-stack expense splitting application with Flask backend and React frontend, featuring JWT authentication and real-time expense management.

## 🚀 Features

### Backend (Flask API)
- User registration/login with JWT authentication
- Secure group management with auto-membership
- Expense tracking with automatic equal splits
- Settlement recording and balance calculations
- Complete expense history and activity tracking
- Authorization-based data access control

### Frontend (React)
- Modern responsive UI with React 18
- User authentication with JWT tokens
- Dashboard with expense overview and statistics
- Group management with member addition/removal
- Real-time expense creation and tracking
- Modal-based forms for better UX
- Protected routes and authentication context

## 🛠️ Tech Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-JWT-Extended** - JWT authentication
- **Flask-Smorest** - API blueprint and documentation
- **Alembic** - Database migrations
- **SQLite** - Database (development)

### Frontend
- **React 18** - UI library
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **CSS3** - Responsive styling
- **Context API** - State management

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
