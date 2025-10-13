# Employee Performance Management System (EPMS) - MVP

A comprehensive full-stack application for managing employee performance, goals, reviews, and feedback within an organization.

## 🚀 Features

### Core Functionality
- **User Management**: Role-based access control (Employee, Manager, HR, Admin)
- **Goal Management**: SMART goals creation, tracking, and approval workflow
- **Performance Reviews**: Self-reviews, manager reviews, and 360-degree feedback
- **Peer Feedback**: Request and provide feedback from colleagues
- **Review Cycles**: Configurable performance review periods
- **Analytics & Reporting**: Comprehensive dashboards and reports
- **Organizational Structure**: Department and team management

### Technical Features
- **Backend**: Django 5.0 + Django REST Framework 3.15
- **Frontend**: Vue 3 + Vite + Vuetify 3
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **Authentication**: JWT with refresh tokens
- **API Documentation**: Swagger/OpenAPI with drf-spectacular
- **Testing**: pytest (backend) + Vitest + Cypress (frontend)
- **Containerization**: Docker + Docker Compose

## 📁 Project Structure

```
epms-mvp/
├── backend/                 # Django backend
│   ├── apps/               # Django applications
│   │   ├── accounts/       # User management & authentication
│   │   ├── org/           # Organizational structure
│   │   ├── cycles/        # Review cycles
│   │   ├── goals/         # Goals management
│   │   ├── feedback/      # Peer feedback
│   │   ├── reviews/       # Performance reviews
│   │   └── analytics/     # Analytics & reporting
│   ├── epms/              # Django project settings
│   ├── tests/             # Backend tests
│   ├── manage.py
│   └── requirements.txt
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/    # Reusable Vue components
│   │   ├── views/         # Page components
│   │   │   ├── Employee/  # Employee-specific views
│   │   │   ├── Manager/   # Manager-specific views
│   │   │   └── HR/        # HR-specific views
│   │   ├── store/         # Pinia state management
│   │   ├── router/        # Vue Router configuration
│   │   ├── api/           # API client functions
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
├── infra/                  # Infrastructure & deployment
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
└── docs/                   # Documentation
    ├── README.md
    ├── API_REFERENCE.md
    ├── TEST_STRATEGY.md
    ├── DEPLOYMENT_GUIDE.md
    └── SECURITY_GUIDE.md
```

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd epms-mvp
   ```

2. **Start the services**
   ```bash
   cd infra
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/api/
   - API Documentation: http://localhost:8000/docs/
   - Admin Panel: http://localhost:8000/admin/

### Local Development

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🔐 Default Credentials

After running migrations, create a superuser:
```bash
python manage.py createsuperuser
```

## 📚 API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/docs/
- ReDoc: http://localhost:8000/redoc/

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### End-to-End Tests
```bash
cd frontend
npm run e2e
```

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

## 📖 Documentation

- [API Reference](API_REFERENCE.md)
- [Test Strategy](TEST_STRATEGY.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Security Guide](SECURITY_GUIDE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions, please contact the development team or create an issue in the repository.