# Heap Master Pro - Industrial Heap Leach Pad Management System

## 🏭 Professional Industrial Solution for Mining Operations

Heap Master Pro is a comprehensive, enterprise-grade software solution designed for mining companies to design, manage, and optimize heap leach pads. Built with modern technologies including Python (FastAPI), React, and Three.js for 3D visualization.

---

## ✨ Key Features

### 🎯 Core Capabilities
- **Multi-Pad Management**: Create, configure, and manage multiple leach pads with complex geometries
- **3D Visualization**: Interactive three-dimensional rendering using Three.js
- **Engineering Calculations**: Prismoidal volume, tonnage, recoverable copper, acid consumption
- **Irrigation System Design**: Emitter spacing, lateral design, flow rate calculations
- **Terrain Modeling**: Support for sloped terrain with X/Y gradient adjustments
- **Pad Connectivity**: Intelligent handling of adjacent pads with shared boundaries

### 🔐 Enterprise Features
- **User Authentication & Authorization**: Role-based access control (RBAC)
- **Multi-Tenant Architecture**: Support for multiple organizations/companies
- **Project Management**: Organize pads into projects with team collaboration
- **Audit Logging**: Complete history of all changes and operations
- **Data Export**: PDF reports, Excel exports, CAD file generation (DXF/DWG)

### 📊 Dashboard & Analytics
- **Real-time KPIs**: Live metrics for production, recovery, and operational efficiency
- **Historical Trends**: Time-series analysis with interactive charts
- **Predictive Analytics**: ML-powered recovery predictions
- **Custom Reports**: Configurable report templates

### ⚙️ Customization
- **User Preferences**: Theme (dark/light), language, units (metric/imperial)
- **Company Branding**: Logo, colors, custom report headers
- **Calculation Parameters**: Configurable formulas and constants
- **Workflow Templates**: Pre-configured settings for common scenarios

---

## 🛠 Technology Stack

### Backend (Python/FastAPI)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with OAuth2
- **Caching**: Redis for session management and caching
- **Task Queue**: Celery for background jobs (reports, exports)
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### Frontend (React + Vite)
- **Framework**: React 18 with TypeScript
- **State Management**: Redux Toolkit / Zustand
- **UI Components**: Material-UI / Ant Design
- **3D Engine**: Three.js with React Three Fiber
- **Charts**: Recharts / Chart.js
- **Build Tool**: Vite for fast development and optimized builds

### DevOps & Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions / GitLab CI
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Deployment**: Kubernetes-ready

---

## 📁 Project Structure

```
heap_master_pro/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core utilities, config, security
│   │   ├── models/            # SQLAlchemy database models
│   │   ├── services/          # Business logic layer
│   │   ├── routers/           # API route definitions
│   │   └── schemas/           # Pydantic schemas
│   ├── tests/                 # Unit and integration tests
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── store/             # State management
│   │   ├── utils/             # Utility functions
│   │   └── styles/            # CSS/Tailwind styles
│   ├── public/                # Static assets
│   └── package.json          # Node dependencies
│
├── docs/                       # Documentation
├── scripts/                    # Deployment & utility scripts
├── docker-compose.yml         # Docker orchestration
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker (optional, for containerized deployment)

### Development Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd heap_master_pro
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Docker Deployment
```bash
docker-compose up -d
```

---

## 📖 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout

### Pads
- `GET /api/v1/pads` - List all pads
- `POST /api/v1/pads` - Create new pad
- `GET /api/v1/pads/{id}` - Get pad details
- `PUT /api/v1/pads/{id}` - Update pad
- `DELETE /api/v1/pads/{id}` - Delete pad
- `POST /api/v1/pads/{id}/calculate` - Trigger calculations

### Projects
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project with pads
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Reports
- `GET /api/v1/reports` - List available reports
- `POST /api/v1/reports/generate` - Generate custom report
- `GET /api/v1/reports/{id}/download` - Download report (PDF/Excel)

### Users & Admin
- `GET /api/v1/users` - List users (admin)
- `POST /api/v1/users` - Create user (admin)
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user (admin)

---

## 🔒 Security Features

- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Short-lived access tokens + refresh tokens
- **Rate Limiting**: Protection against brute force attacks
- **CORS Configuration**: Strict origin policies
- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Protection**: Content Security Policy headers
- **HTTPS Enforcement**: SSL/TLS in production

---

## 📈 Performance Optimizations

- **Database Indexing**: Optimized queries with proper indexes
- **Connection Pooling**: Efficient database connection management
- **Caching Strategy**: Redis caching for frequently accessed data
- **Lazy Loading**: On-demand loading of 3D models and large datasets
- **Code Splitting**: Frontend bundle optimization
- **CDN Integration**: Static asset delivery via CDN

---

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# End-to-end tests
npm run e2e
```

### Test Coverage
- Unit Tests: Business logic, utilities, helpers
- Integration Tests: API endpoints, database operations
- E2E Tests: Complete user workflows
- Load Tests: Performance under stress

---

## 📦 Deployment

### Production Checklist
- [ ] Set strong secret keys
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up database backups
- [ ] Configure monitoring and alerting
- [ ] Enable logging aggregation
- [ ] Set up CDN for static assets
- [ ] Configure auto-scaling rules
- [ ] Implement disaster recovery plan

### Environment Variables
See `.env.example` for required configuration.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Backend: Black, Flake8, MyPy
- Frontend: ESLint, Prettier
- Commit Messages: Conventional Commits

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 📞 Support

For commercial licensing, support, or customization requests:
- Email: support@heapmasterpro.com
- Website: www.heapmasterpro.com
- Documentation: docs.heapmasterpro.com

---

## 🏢 Commercial Use

Heap Master Pro is available under commercial license for industrial use. Contact us for:
- Enterprise licensing
- Custom feature development
- On-premise deployment
- Training and onboarding
- Priority support

---

**Built with ❤️ for the Mining Industry**
