# Splitwise Frontend

A React-based frontend for the Splitwise expense splitting application. This frontend connects to the Flask backend API to provide a responsive and user-friendly interface for managing shared expenses.

## Features

- 🔐 **Authentication**: Login and register with JWT token management
- 📊 **Dashboard**: Overview of expenses, groups, and balances
- 👥 **Group Management**: Create and manage expense groups
- 💸 **Expense Tracking**: Add, edit, and split expenses
- 💰 **Settlement System**: Track who owes what and settle payments
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🎨 **Modern UI**: Clean and intuitive user interface

## Tech Stack

- **React 18** - Frontend framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **CSS3** - Styling with modern features
- **Context API** - State management
- **JWT** - Authentication tokens

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── Auth/          # Login/Register components
│   │   ├── Layout/        # Header, Footer, Navigation
│   │   └── UI/           # Reusable UI components
│   ├── contexts/
│   │   └── AuthContext.js # Authentication context
│   ├── hooks/
│   │   └── useApi.js     # Custom API hooks
│   ├── pages/
│   │   └── Dashboard.jsx # Main dashboard page
│   ├── services/
│   │   ├── api.js        # Axios configuration
│   │   ├── auth.js       # Authentication service
│   │   ├── groups.js     # Groups API service
│   │   └── expenses.js   # Expenses API service
│   ├── utils/
│   │   ├── constants.js  # API endpoints and constants
│   │   └── helpers.js    # Utility functions
│   ├── App.jsx          # Main App component
│   ├── App.css          # App styles
│   ├── index.js         # Entry point
│   └── index.css        # Global styles
└── package.json
```

## Installation & Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm start
   ```

The app will open at `http://localhost:3000` and automatically proxy API requests to `http://localhost:5000` (your Flask backend).

## Backend Integration

The frontend is configured to work with the Flask backend API. Make sure your backend is running on `http://localhost:5000` before starting the frontend.

### API Integration Features:
- **Automatic token refresh** when access tokens expire
- **Request/Response interceptors** for error handling
- **Loading states** for better UX
- **Error handling** with user-friendly messages

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Key Components

### Authentication
- `Login.jsx` - User login form
- `Register.jsx` - User registration form
- `AuthContext.js` - Global authentication state

### Layout
- `Header.jsx` - Top navigation with user menu
- `Footer.jsx` - Footer component
- Protected route wrapper for authenticated pages

### UI Components
- `LoadingSpinner.jsx` - Loading indicator
- `Modal.jsx` - Reusable modal component
- `Button.jsx` - Styled button component

### Services
- Axios instance with interceptors
- JWT token management
- API error handling
- Service methods for all backend endpoints

## Styling

The project uses modern CSS with:
- **CSS Grid** and **Flexbox** for layouts
- **CSS Variables** for consistent theming
- **Responsive design** with mobile-first approach
- **Smooth animations** and transitions
- **Modern card-based** design system

## Environment Variables

Create a `.env` file in the frontend directory if you need to customize:

```env
REACT_APP_API_URL=http://localhost:5000
```

## Deployment

To build for production:

```bash
npm run build
```

This creates a `build` folder with optimized production files ready for deployment.

## Current Status

✅ **Completed**:
- Authentication system
- Responsive layout and navigation
- Dashboard with statistics
- API service layer
- Error handling and loading states
- Mobile-responsive design

🚧 **In Development**:
- Groups management pages
- Expense creation and editing
- Settlement system
- History and reporting
- Profile management

## Contributing

1. Follow the existing code structure and naming conventions
2. Use functional components with hooks
3. Implement responsive design for all new components
4. Add proper error handling and loading states
5. Write clean, commented code

## API Documentation

The backend provides Swagger documentation at `http://localhost:5000/swagger-ui` when running locally.