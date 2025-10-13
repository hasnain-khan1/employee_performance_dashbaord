# Test Strategy

This document outlines the comprehensive testing strategy for the EPMS application, covering unit tests, integration tests, and end-to-end tests.

## Testing Pyramid

```
        /\
       /  \
      / E2E \     End-to-End Tests (Cypress)
     /______\
    /        \
   /Integration\  Integration Tests (pytest + Vitest)
  /____________\
 /              \
/    Unit Tests   \  Unit Tests (pytest + Vitest)
/________________\
```

## Backend Testing (Django + pytest)

### Test Structure
```
backend/
├── tests/
│   ├── unit/                 # Unit tests
│   │   ├── test_models.py
│   │   ├── test_serializers.py
│   │   ├── test_utils.py
│   │   └── test_validators.py
│   ├── integration/          # Integration tests
│   │   ├── test_auth.py
│   │   ├── test_goals.py
│   │   ├── test_feedback.py
│   │   ├── test_reviews.py
│   │   └── test_analytics.py
│   └── e2e/                  # End-to-end tests
│       ├── test_review_cycle.py
│       ├── test_goal_workflow.py
│       └── test_feedback_flow.py
├── conftest.py              # pytest configuration
└── pytest.ini              # pytest settings
```

### Unit Tests

**Test Models (`test_models.py`)**
```python
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.accounts.models import User
from apps.goals.models import Goal

class TestUserModel(TestCase):
    def test_user_creation(self):
        """Test user creation with valid data."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP000001'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.employee_id, 'EMP000001')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_employee_id_validation(self):
        """Test employee ID format validation."""
        with self.assertRaises(ValidationError):
            user = User(
                username='testuser',
                email='test@example.com',
                employee_id='INVALID'
            )
            user.full_clean()

class TestGoalModel(TestCase):
    def test_goal_creation(self):
        """Test goal creation with valid data."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP000001'
        )
        goal = Goal.objects.create(
            title='Test Goal',
            description='Test Description',
            employee=user,
            specific='Specific criteria',
            measurable='Measurable criteria',
            achievable='Achievable criteria',
            relevant='Relevant criteria',
            time_bound='Time-bound criteria',
            start_date='2024-01-01',
            target_date='2024-12-31'
        )
        self.assertEqual(goal.title, 'Test Goal')
        self.assertEqual(goal.employee, user)
        self.assertEqual(goal.status, 'draft')

    def test_goal_progress_update(self):
        """Test goal progress update functionality."""
        # Implementation here
        pass
```

**Test Serializers (`test_serializers.py`)**
```python
import pytest
from rest_framework.test import APITestCase
from rest_framework import status
from apps.accounts.serializers import UserSerializer
from apps.goals.serializers import GoalSerializer

class TestUserSerializer(APITestCase):
    def test_user_serialization(self):
        """Test user data serialization."""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'employee_id': 'EMP000001',
            'role': 'employee'
        }
        serializer = UserSerializer(data=user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')

    def test_user_validation(self):
        """Test user data validation."""
        invalid_data = {
            'username': '',
            'email': 'invalid-email',
            'employee_id': 'INVALID'
        }
        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertIn('email', serializer.errors)
```

### Integration Tests

**Test Authentication (`test_auth.py`)**
```python
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.accounts.models import User

User = get_user_model()

class TestAuthenticationAPI(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP000001'
        )

    def test_login_success(self):
        """Test successful user login."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without authentication."""
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_auth(self):
        """Test accessing protected endpoint with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

**Test Goals API (`test_goals.py`)**
```python
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User
from apps.goals.models import Goal

class TestGoalsAPI(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            employee_id='EMP000001'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_goal(self):
        """Test goal creation via API."""
        data = {
            'title': 'Test Goal',
            'description': 'Test Description',
            'specific': 'Specific criteria',
            'measurable': 'Measurable criteria',
            'achievable': 'Achievable criteria',
            'relevant': 'Relevant criteria',
            'time_bound': 'Time-bound criteria',
            'start_date': '2024-01-01',
            'target_date': '2024-12-31',
            'weight': 10
        }
        response = self.client.post('/api/goals/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Goal.objects.count(), 1)

    def test_list_goals(self):
        """Test listing goals via API."""
        Goal.objects.create(
            title='Test Goal 1',
            description='Test Description 1',
            employee=self.user,
            specific='Specific',
            measurable='Measurable',
            achievable='Achievable',
            relevant='Relevant',
            time_bound='Time-bound',
            start_date='2024-01-01',
            target_date='2024-12-31'
        )
        response = self.client.get('/api/goals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_goal_approval_workflow(self):
        """Test goal approval workflow."""
        # Create goal
        goal = Goal.objects.create(
            title='Test Goal',
            description='Test Description',
            employee=self.user,
            specific='Specific',
            measurable='Measurable',
            achievable='Achievable',
            relevant='Relevant',
            time_bound='Time-bound',
            start_date='2024-01-01',
            target_date='2024-12-31'
        )
        
        # Submit for approval
        goal.status = 'submitted'
        goal.save()
        
        # Manager approves
        manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123',
            employee_id='EMP000002',
            role='manager'
        )
        self.client.force_authenticate(user=manager)
        
        response = self.client.post(f'/api/goals/{goal.id}/approve/', {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        goal.refresh_from_db()
        self.assertEqual(goal.status, 'approved')
```

### End-to-End Tests

**Test Review Cycle (`test_review_cycle.py`)**
```python
import pytest
from django.test import TestCase
from apps.accounts.models import User
from apps.cycles.models import ReviewCycle, CycleParticipant
from apps.goals.models import Goal
from apps.reviews.models import Review

class TestReviewCycleE2E(TestCase):
    def setUp(self):
        self.employee = User.objects.create_user(
            username='employee',
            email='employee@example.com',
            password='testpass123',
            employee_id='EMP000001',
            role='employee'
        )
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123',
            employee_id='EMP000002',
            role='manager'
        )
        self.cycle = ReviewCycle.objects.create(
            name='Q4 2024 Review',
            description='End of year review',
            start_date='2024-10-01',
            end_date='2024-12-31',
            goal_setting_start='2024-10-01',
            goal_setting_end='2024-10-15',
            self_review_start='2024-11-01',
            self_review_end='2024-11-15',
            manager_review_start='2024-11-16',
            manager_review_end='2024-12-15',
            created_by=self.manager
        )

    def test_complete_review_cycle_workflow(self):
        """Test complete review cycle workflow from start to finish."""
        # 1. Add employee to cycle
        participant = CycleParticipant.objects.create(
            cycle=self.cycle,
            employee=self.employee,
            manager=self.manager
        )
        
        # 2. Employee sets goals
        goal = Goal.objects.create(
            title='Complete Project',
            description='Finish the main project',
            employee=self.employee,
            cycle=self.cycle,
            specific='Complete the main project',
            measurable='Project completion percentage',
            achievable='Yes, with current resources',
            relevant='Aligns with company objectives',
            time_bound='By end of Q4',
            start_date='2024-10-01',
            target_date='2024-12-31'
        )
        
        # 3. Manager approves goals
        goal.status = 'submitted'
        goal.save()
        goal.approve(self.manager)
        
        # 4. Employee completes self-review
        self_review = Review.objects.create(
            employee=self.employee,
            reviewer=self.employee,
            cycle=self.cycle,
            review_type='self',
            achievements='Completed all assigned tasks',
            overall_rating=4
        )
        participant.self_review_completed = True
        participant.save()
        
        # 5. Manager completes manager review
        manager_review = Review.objects.create(
            employee=self.employee,
            reviewer=self.manager,
            cycle=self.cycle,
            review_type='manager',
            achievements='Excellent work on the project',
            overall_rating=5
        )
        participant.manager_review_completed = True
        participant.save()
        
        # 6. Verify cycle completion
        self.assertTrue(participant.is_fully_completed)
        self.assertEqual(participant.completion_percentage, 100)
```

## Frontend Testing (Vue.js + Vitest + Cypress)

### Test Structure
```
frontend/
├── src/
│   ├── __tests__/           # Unit tests
│   │   ├── components/
│   │   ├── views/
│   │   ├── store/
│   │   └── api/
│   └── e2e/                 # End-to-end tests
│       ├── specs/
│       └── support/
├── vitest.config.js
└── cypress.config.js
```

### Unit Tests (Vitest)

**Test Components (`components/GoalCard.test.js`)**
```javascript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import GoalCard from '@/components/GoalCard.vue'

describe('GoalCard', () => {
  it('renders goal information correctly', () => {
    const goal = {
      id: 1,
      title: 'Test Goal',
      description: 'Test Description',
      progress_percentage: 75,
      status: 'in_progress',
      priority: 'high'
    }

    const wrapper = mount(GoalCard, {
      props: { goal }
    })

    expect(wrapper.text()).toContain('Test Goal')
    expect(wrapper.text()).toContain('Test Description')
    expect(wrapper.text()).toContain('75%')
  })

  it('emits edit event when edit button is clicked', async () => {
    const goal = {
      id: 1,
      title: 'Test Goal',
      description: 'Test Description',
      progress_percentage: 75,
      status: 'in_progress',
      priority: 'high'
    }

    const wrapper = mount(GoalCard, {
      props: { goal }
    })

    await wrapper.find('[data-testid="edit-button"]').trigger('click')
    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')[0]).toEqual([goal])
  })
})
```

**Test Store (`store/auth.test.js`)**
```javascript
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/store/auth'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with empty user', () => {
    const store = useAuthStore()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('sets user after login', async () => {
    const store = useAuthStore()
    const userData = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      employee_id: 'EMP000001'
    }

    // Mock API call
    vi.spyOn(store, 'login').mockResolvedValue({
      access: 'token',
      refresh: 'refresh_token',
      user: userData
    })

    await store.login({ username: 'testuser', password: 'password' })
    
    expect(store.user).toEqual(userData)
    expect(store.isAuthenticated).toBe(true)
  })
})
```

**Test API (`api/goals.test.js`)**
```javascript
import { describe, it, expect, vi } from 'vitest'
import { goalsAPI } from '@/api/goals'
import api from '@/api/axios'

// Mock axios
vi.mock('@/api/axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  }
}))

describe('Goals API', () => {
  it('fetches goals successfully', async () => {
    const mockGoals = [
      { id: 1, title: 'Goal 1', status: 'in_progress' },
      { id: 2, title: 'Goal 2', status: 'completed' }
    ]

    api.get.mockResolvedValue({ data: { results: mockGoals } })

    const result = await goalsAPI.getGoals()
    
    expect(api.get).toHaveBeenCalledWith('/goals/', { params: {} })
    expect(result.data.results).toEqual(mockGoals)
  })

  it('creates goal successfully', async () => {
    const goalData = {
      title: 'New Goal',
      description: 'Goal Description',
      specific: 'Specific criteria'
    }

    const mockResponse = { data: { id: 1, ...goalData } }
    api.post.mockResolvedValue(mockResponse)

    const result = await goalsAPI.createGoal(goalData)
    
    expect(api.post).toHaveBeenCalledWith('/goals/', goalData)
    expect(result.data).toEqual(mockResponse.data)
  })
})
```

### End-to-End Tests (Cypress)

**Test User Workflow (`e2e/goal-management.cy.js`)**
```javascript
describe('Goal Management Workflow', () => {
  beforeEach(() => {
    // Login before each test
    cy.login('testuser@example.com', 'password')
  })

  it('should create a new goal', () => {
    cy.visit('/employee/goals')
    
    // Click create goal button
    cy.get('[data-testid="create-goal-button"]').click()
    
    // Fill goal form
    cy.get('[data-testid="goal-title"]').type('Test Goal')
    cy.get('[data-testid="goal-description"]').type('Test Description')
    cy.get('[data-testid="goal-specific"]').type('Specific criteria')
    cy.get('[data-testid="goal-measurable"]').type('Measurable criteria')
    cy.get('[data-testid="goal-achievable"]').type('Achievable criteria')
    cy.get('[data-testid="goal-relevant"]').type('Relevant criteria')
    cy.get('[data-testid="goal-time-bound"]').type('Time-bound criteria')
    
    // Set dates
    cy.get('[data-testid="goal-start-date"]').type('2024-01-01')
    cy.get('[data-testid="goal-target-date"]').type('2024-12-31')
    
    // Submit form
    cy.get('[data-testid="save-goal-button"]').click()
    
    // Verify goal was created
    cy.get('[data-testid="goal-list"]').should('contain', 'Test Goal')
    cy.get('[data-testid="success-message"]').should('be.visible')
  })

  it('should update goal progress', () => {
    // Create a goal first
    cy.createGoal({
      title: 'Test Goal',
      description: 'Test Description',
      specific: 'Specific',
      measurable: 'Measurable',
      achievable: 'Achievable',
      relevant: 'Relevant',
      time_bound: 'Time-bound'
    })

    cy.visit('/employee/goals')
    
    // Click on goal to view details
    cy.get('[data-testid="goal-item"]').first().click()
    
    // Update progress
    cy.get('[data-testid="progress-slider"]').invoke('val', 75).trigger('input')
    cy.get('[data-testid="progress-comments"]').type('Making good progress')
    cy.get('[data-testid="update-progress-button"]').click()
    
    // Verify progress was updated
    cy.get('[data-testid="progress-percentage"]').should('contain', '75%')
  })

  it('should complete review cycle workflow', () => {
    // This test would cover the complete review cycle
    // from goal setting to final review completion
    cy.visit('/employee/self-review')
    
    // Complete self-review
    cy.get('[data-testid="achievements"]').type('Completed all goals')
    cy.get('[data-testid="challenges"]').type('Faced some technical challenges')
    cy.get('[data-testid="development-areas"]').type('Want to learn new technologies')
    cy.get('[data-testid="overall-rating"]').click()
    
    // Submit review
    cy.get('[data-testid="submit-review-button"]').click()
    
    // Verify submission
    cy.get('[data-testid="success-message"]').should('be.visible')
    cy.get('[data-testid="review-status"]').should('contain', 'Submitted')
  })
})
```

## Test Configuration

### pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = epms.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=apps
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

### Vitest Configuration (`vitest.config.js`)
```javascript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/main.js',
        'src/router/index.js',
        '**/*.config.js'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

### Cypress Configuration (`cypress.config.js`)
```javascript
import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    supportFile: 'cypress/support/e2e.js',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    setupNodeEvents(on, config) {
      // implement node event listeners here
    }
  }
})
```

## Test Commands

### Backend Tests
```bash
# Run all tests
pytest

# Run specific test type
pytest -m unit
pytest -m integration
pytest -m e2e

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::TestUserModel::test_user_creation
```

### Frontend Tests
```bash
# Run unit tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch

# Run E2E tests
npm run e2e

# Run E2E tests headlessly
npm run e2e:run
```

## Continuous Integration

### GitHub Actions Workflow (`.github/workflows/test.yml`)
```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    - name: Run migrations
      run: |
        cd backend
        python manage.py migrate
    - name: Run tests
      run: |
        cd backend
        pytest --cov=apps --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    - name: Run unit tests
      run: |
        cd frontend
        npm run test:coverage
    - name: Run E2E tests
      run: |
        cd frontend
        npm run e2e:run
```

## Test Data Management

### Fixtures and Factories

**Backend (`conftest.py`)**
```python
import pytest
from django.contrib.auth import get_user_model
from apps.accounts.models import User
from apps.goals.models import Goal
from apps.cycles.models import ReviewCycle

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        employee_id='EMP000001'
    )

@pytest.fixture
def manager():
    return User.objects.create_user(
        username='manager',
        email='manager@example.com',
        password='testpass123',
        employee_id='EMP000002',
        role='manager'
    )

@pytest.fixture
def review_cycle(manager):
    return ReviewCycle.objects.create(
        name='Test Cycle',
        description='Test Description',
        start_date='2024-01-01',
        end_date='2024-12-31',
        created_by=manager
    )

@pytest.fixture
def goal(user, review_cycle):
    return Goal.objects.create(
        title='Test Goal',
        description='Test Description',
        employee=user,
        cycle=review_cycle,
        specific='Specific',
        measurable='Measurable',
        achievable='Achievable',
        relevant='Relevant',
        time_bound='Time-bound',
        start_date='2024-01-01',
        target_date='2024-12-31'
    )
```

**Frontend (`cypress/support/commands.js`)**
```javascript
// Custom commands for Cypress
Cypress.Commands.add('login', (email, password) => {
  cy.visit('/login')
  cy.get('[data-testid="username"]').type(email)
  cy.get('[data-testid="password"]').type(password)
  cy.get('[data-testid="login-button"]').click()
  cy.url().should('include', '/dashboard')
})

Cypress.Commands.add('createGoal', (goalData) => {
  cy.visit('/employee/goals')
  cy.get('[data-testid="create-goal-button"]').click()
  
  cy.get('[data-testid="goal-title"]').type(goalData.title)
  cy.get('[data-testid="goal-description"]').type(goalData.description)
  cy.get('[data-testid="goal-specific"]').type(goalData.specific)
  cy.get('[data-testid="goal-measurable"]').type(goalData.measurable)
  cy.get('[data-testid="goal-achievable"]').type(goalData.achievable)
  cy.get('[data-testid="goal-relevant"]').type(goalData.relevant)
  cy.get('[data-testid="goal-time-bound"]').type(goalData.time_bound)
  
  cy.get('[data-testid="save-goal-button"]').click()
})
```

## Performance Testing

### Load Testing with Locust

**Load Test (`load_test.py`)**
```python
from locust import HttpUser, task, between

class EPMSUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login/", {
            "username": "testuser",
            "password": "testpass123"
        })
        self.token = response.json()["access"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    def view_goals(self):
        self.client.get("/api/goals/")
    
    @task(2)
    def view_profile(self):
        self.client.get("/api/auth/profile/")
    
    @task(1)
    def create_goal(self):
        self.client.post("/api/goals/", {
            "title": "Load Test Goal",
            "description": "Created during load test",
            "specific": "Specific",
            "measurable": "Measurable",
            "achievable": "Achievable",
            "relevant": "Relevant",
            "time_bound": "Time-bound",
            "start_date": "2024-01-01",
            "target_date": "2024-12-31"
        })
```

## Test Reporting

### Coverage Reports
- HTML coverage reports generated in `htmlcov/` directory
- Coverage thresholds enforced (80% minimum)
- Coverage reports uploaded to Codecov

### Test Results
- JUnit XML reports for CI/CD integration
- Screenshots and videos for failed E2E tests
- Detailed logging for debugging test failures

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Use clear, descriptive test names
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Mock External Dependencies**: Don't rely on external services
5. **Test Edge Cases**: Cover error conditions and boundary cases
6. **Maintain Test Data**: Keep test data consistent and minimal
7. **Regular Maintenance**: Update tests when requirements change
8. **Performance Awareness**: Monitor test execution time
9. **Documentation**: Document complex test scenarios
10. **Code Coverage**: Aim for high but meaningful coverage