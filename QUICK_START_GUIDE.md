# 🚀 EPMS - Quick Start Guide

## How to Access Admin & HR Dashboards

### 📊 System Overview

The Employee Performance Management System (EPMS) has **role-based access control** with four user roles:

1. **Employee** - Basic user with personal goals and reviews
2. **Manager** - Manages team goals and reviews
3. **HR** - Full HR analytics and employee management
4. **Admin** - Complete system administration access

---

## 🔐 Test User Credentials

Use these pre-created accounts to test different roles:

| Role | Username | Password | Employee ID |
|------|----------|----------|-------------|
| **Employee** | `employee1` | `Employee123!` | EMP000100 |
| **Manager** | `manager1` | `Manager123!` | EMP000200 |
| **HR** | `hr1` | `HR123!` | EMP000300 |
| **Admin** | `admin1` | `Admin123!` | EMP000400 |

---

## 🌐 Accessing the Application

### Step 1: Open the Frontend
Navigate to: **http://localhost:5173**

### Step 2: Login
1. Click on "Login" or you'll be redirected automatically
2. Enter one of the credentials above
3. Click "Sign In"

---

## 🎯 HR Dashboard Access

### Method 1: Via Navigation Menu

1. **Log in** with HR or Admin credentials:
   - Username: `hr1`
   - Password: `HR123!`

2. **Click the hamburger menu** (☰) in the top-left corner

3. You'll see HR-specific menu items:
   - 📊 **Analytics** - Main HR analytics dashboard
   - 👥 **All Employees** - Employee management
   - 📅 **Review Cycles** - Performance cycle management
   - 📈 **Reports** - Generate reports

4. **Click "Analytics"** to access the HR Dashboard

### Method 2: Direct URL Access

After logging in as HR/Admin, navigate directly to:

```
http://localhost:5173/hr/analytics       # HR Analytics Dashboard
http://localhost:5173/hr/employees       # Employee Management
http://localhost:5173/hr/cycles          # Review Cycles
http://localhost:5173/hr/reports         # Reports
```

---

## 👨‍💼 Admin Dashboard Access

### Django Admin Panel

1. Navigate to: **http://localhost:8000/admin**

2. Login with admin credentials:
   - Username: `admin1`
   - Password: `Admin123!`

3. You'll have full backend access to:
   - User management
   - All models (Goals, Reviews, Feedback, etc.)
   - System configuration

### Frontend Admin Access

Admins have access to **all** HR features plus:
- Same routes as HR role
- Can access any employee/manager routes
- Full system visibility

---

## 📱 Role-Specific Features

### Employee Role (`employee1`)
**Navigation Menu Shows:**
- 🏠 Dashboard
- 🎯 My Goals
- 📝 Self Review
- 💬 Feedback

**Routes:**
- `/dashboard`
- `/employee/goals`
- `/employee/self-review`
- `/employee/feedback`

---

### Manager Role (`manager1`)
**Navigation Menu Shows:**
- 🏠 Dashboard
- 👥 Team Goals
- 📋 Team Reviews
- 💭 Feedback Requests

**Routes:**
- `/dashboard`
- `/manager/team-goals`
- `/manager/team-reviews`
- `/manager/feedback-requests`

---

### HR Role (`hr1`)
**Navigation Menu Shows:**
- 🏠 Dashboard
- 👨‍👩‍👧‍👦 All Employees
- 📅 Review Cycles
- 📊 **Analytics** ← Main HR Dashboard
- 📈 Reports

**Routes:**
- `/dashboard`
- `/hr/employees`
- `/hr/cycles`
- `/hr/analytics` ← **HR Dashboard**
- `/hr/reports`

**Key Features:**
- View organization-wide analytics
- Manage all employees
- Create and manage review cycles
- Generate reports
- Department performance tracking
- Goal completion metrics
- Performance trends

---

### Admin Role (`admin1`)
**Has access to:**
- All HR routes
- All Manager routes
- All Employee routes
- Django Admin panel (`/admin`)
- System configuration

---

## 🛠️ Server Information

### Backend API
- **URL:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs/
- **API Docs (ReDoc):** http://localhost:8000/redoc/
- **Admin Panel:** http://localhost:8000/admin/

### Frontend
- **URL:** http://localhost:5173
- **Framework:** Vue 3 + Vuetify

---

## 🔄 Testing the HR Dashboard

1. **Login as HR:**
   ```
   Username: hr1
   Password: HR123!
   ```

2. **Navigate to Analytics:**
   - Click hamburger menu (☰)
   - Click "Analytics"
   - Or go directly to: http://localhost:5173/hr/analytics

3. **You'll see:**
   - Key Metrics Cards (Total Employees, Active Goals, Completed Reviews, Avg Performance)
   - Performance Trends Chart
   - Goal Distribution Chart
   - Department Performance Table
   - Recent Activity Timeline
   - Alerts & Notifications

---

## 🐛 Troubleshooting

### "Access Denied" or redirected to Dashboard
- Make sure you're logged in with HR (`hr1`) or Admin (`admin1`) credentials
- Regular employees and managers don't have access to HR routes

### Can't see HR menu items
- Check your user role in the top-right user menu
- Log out and log back in with HR credentials

### Backend API not responding
- Make sure backend server is running: `cd backend && python manage.py runserver`
- Check: http://localhost:8000/docs/

### Frontend not loading
- Make sure frontend server is running: `cd frontend && npm run dev`
- Check: http://localhost:5173

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs/
- **Source Code:** `/home/azm/PycharmProjects/employee_performance_dashbaord/`
- **Backend:** `backend/` directory
- **Frontend:** `frontend/` directory

---

## 💡 Quick Tips

1. **Role Hierarchy:** Admin > HR > Manager > Employee
2. **Higher roles can access lower-level routes**
3. **Navigation menu adapts based on your role**
4. **All API endpoints require JWT authentication**
5. **Use browser DevTools (F12) to debug API calls**

---

## 🎉 Success!

You should now be able to access the HR Analytics Dashboard!

If you encounter any issues, check:
1. Backend server is running on port 8000
2. Frontend server is running on port 5173
3. You're logged in with the correct credentials
4. Your browser console for any errors (F12)

