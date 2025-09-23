# Splitwise Development Setup Guide

## 🚀 Running Frontend and Backend Together

Follow these steps to run both your Flask backend and React frontend simultaneously:

### Prerequisites ✅
- Python 3.x installed
- Node.js and npm installed
- Virtual environment set up (✅ You have .venv)

---

## 🔧 Backend Setup (Flask API)

### 1. Activate Virtual Environment
```powershell
# In your main Splitwise directory
.\.venv\Scripts\Activate.ps1
```

### 2. Install Backend Dependencies (if needed)
```powershell
pip install -r requirements.txt
```

### 3. Set Environment Variables
Create a `.env` file in your main directory (you already have one):
```env
DATABASE_URL=sqlite:///data.db
JWT_SECRET=your-secret-key-here
FLASK_APP=app.py
FLASK_ENV=development
```

### 4. Run Database Migrations
```powershell
flask db upgrade
```

### 5. Start Backend Server
```powershell
flask run
```
**Backend will run on:** `http://localhost:5000`

---

## 🎨 Frontend Setup (React App)

### 1. Open New Terminal Window
Keep the backend terminal running and open a new PowerShell window

### 2. Navigate to Frontend Directory
```powershell
cd frontend
```

### 3. Install Frontend Dependencies (already done)
```powershell
npm install
```

### 4. Start Frontend Development Server
```powershell
npm start
```
**Frontend will run on:** `http://localhost:3000`

---

## 🔗 How They Connect

### Automatic Proxy Configuration
The frontend is configured with a proxy in `package.json`:
```json
"proxy": "http://localhost:5000"
```

This means:
- Frontend runs on `http://localhost:3000`
- Backend API calls are automatically forwarded to `http://localhost:5000`
- No CORS issues!

### API Endpoints Available
- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /group` - Get all groups
- `POST /group` - Create new group
- `GET /expense` - Get all expenses
- `POST /expense` - Create new expense
- And more...

---

## 🧪 Testing the Setup

### 1. Backend Test
Visit `http://localhost:5000/swagger-ui` to see your API documentation

### 2. Frontend Test
Visit `http://localhost:3000` to see your React app

### 3. Full Integration Test
1. Go to `http://localhost:3000`
2. Try to register a new account
3. Login with your credentials
4. Navigate through the dashboard

---

## 🐛 Troubleshooting

### Backend Issues
- **Port already in use**: Change port in `.flaskenv` file
- **Database errors**: Run `flask db upgrade`
- **Import errors**: Activate virtual environment first

### Frontend Issues
- **Port 3000 busy**: React will offer to use a different port
- **API errors**: Make sure backend is running on port 5000
- **Build errors**: Delete `node_modules` and run `npm install` again

### CORS Issues
- The proxy should handle this, but if you get CORS errors:
  ```python
  # Add to your Flask app
  from flask_cors import CORS
  CORS(app)
  ```

---

## 📁 Development Workflow

### Terminal Setup (Recommended)
1. **Terminal 1**: Backend
   ```powershell
   .\.venv\Scripts\Activate.ps1
   flask run
   ```

2. **Terminal 2**: Frontend
   ```powershell
   cd frontend
   npm start
   ```

### File Watching
- **Backend**: Flask auto-reloads on Python file changes
- **Frontend**: React auto-reloads on JavaScript/CSS changes

---

## 🔧 Quick Start Commands

### Start Backend:
```powershell
.\.venv\Scripts\Activate.ps1
flask run
```

### Start Frontend (in new terminal):
```powershell
cd frontend
npm start
```

---

## 📊 What You'll See

### Frontend (localhost:3000)
- ✅ Login/Register forms
- ✅ Dashboard with statistics
- ✅ Navigation header
- ✅ Responsive design
- 🚧 Groups, Expenses, History (placeholders ready)

### Backend (localhost:5000)
- ✅ REST API endpoints
- ✅ JWT authentication
- ✅ Database operations
- ✅ Swagger documentation at `/swagger-ui`

### Integration
- ✅ Authentication flow works end-to-end
- ✅ Token management and refresh
- ✅ Error handling and loading states
- ✅ Responsive design on all devices

---

## 🎯 Next Steps

Once everything is running:
1. Test user registration and login
2. Explore the dashboard
3. Check the API documentation
4. Start building additional features

Happy coding! 🚀