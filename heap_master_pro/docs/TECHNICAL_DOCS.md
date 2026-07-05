# Heap Master Pro - Technical Documentation

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           React Frontend (TypeScript)                 │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │   │
│  │  │  Dashboard  │ │  Pad Mgmt   │ │  3D Viewer  │     │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTPS/REST API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│              FastAPI Backend (Python)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │    Auth     │ │    Pads     │ │   Reports   │            │
│  │   Router    │ │   Router    │ │   Router    │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │  Projects   │ │    Users    │ │   Admin     │            │
│  │   Router    │ │   Router    │ │   Router    │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │   Celery     │
│  Database    │  │    Cache     │  │   Workers    │
│              │  │              │  │              │
│ - Users      │  │ - Sessions   │  │ - Reports    │
│ - Pads       │  │ - Rate Limit │  │ - Exports    │
│ - Projects   │  │ - Cache      │  │ - Calc       │
│ - Audit      │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Company   │───────│    User     │───────│   Project   │
└─────────────┘   1:N └─────────────┘   1:N └─────────────┘
                                              │
                                              │ 1:N
                                              ▼
                                        ┌─────────────┐
                                        │     Pad     │
                                        └─────────────┘
                                              │
                                              │ 1:N
                                              ▼
                                       ┌──────────────┐
                                       │PadCalculation│
                                       └──────────────┘

┌─────────────┐       ┌─────────────┐
│  AuditLog   │       │ProjectMember│
└─────────────┘       └─────────────┘
```

### Table Specifications

#### users
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, INDEX | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email |
| username | VARCHAR(100) | UNIQUE, NOT NULL | Username |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt hash |
| role | VARCHAR(50) | DEFAULT 'user' | user/engineer/manager/admin |
| company_id | INTEGER | FK → companies | Company reference |
| is_active | BOOLEAN | DEFAULT true | Account status |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |

#### pads
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, INDEX | Unique identifier |
| name | VARCHAR(255) | NOT NULL | Pad name |
| length | FLOAT | NOT NULL | Length (meters) |
| width | FLOAT | NOT NULL | Width (meters) |
| height | FLOAT | NOT NULL | Height (meters) |
| slope_degrees | FLOAT | DEFAULT 37.0 | Slope angle |
| project_id | INTEGER | FK → projects | Project reference |
| calculated_volume | FLOAT | NULLABLE | Cached volume |
| created_by | INTEGER | FK → users | Creator reference |

## API Reference

### Authentication Endpoints

#### POST /api/v1/auth/login
```json
// Request
{
  "username": "user@example.com",
  "password": "securepassword"
}

// Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "role": "engineer"
  }
}
```

#### POST /api/v1/auth/register
```json
// Request
{
  "email": "new@example.com",
  "username": "new_user",
  "password": "securepassword123",
  "full_name": "John Doe",
  "company_name": "Mining Corp"
}
```

### Pad Management Endpoints

#### GET /api/v1/pads
```
Query Parameters:
- project_id: Filter by project
- page: Page number (default: 1)
- limit: Items per page (default: 20)
- sort: Sort field (name, created_at, etc.)
- order: asc/desc
```

#### POST /api/v1/pads
```json
// Request
{
  "name": "Pad A-1",
  "length": 200,
  "width": 100,
  "height": 15,
  "slope_degrees": 37,
  "project_id": 1,
  "copper_grade": 0.7,
  "recovery_rate": 80,
  "density": 1.7
}

// Response
{
  "id": 1,
  "name": "Pad A-1",
  "calculated_volume": 45000.5,
  "calculated_tonnage": 76500.85,
  ...
}
```

#### POST /api/v1/pads/{id}/calculate
```json
// Response
{
  "volume": 45000.5,
  "base_area": 20000,
  "top_area": 15000,
  "tonnage": 76500.85,
  "recoverable_copper": 428.61,
  "acid_consumption": 1147.51,
  "corner_heights": {
    "FL": 15.0,
    "FR": 14.5,
    "BL": 14.8,
    "BR": 14.3
  },
  "hip_lengths": {
    "hip_fl": 25.5,
    "hip_fr": 25.2,
    ...
  }
}
```

## Engineering Calculations

### Prismoidal Volume Formula

```
V = (H / 6) × (A_base + A_top + 4 × A_mid)

Where:
- H = Height of pad
- A_base = Base area (L × W)
- A_top = Top area considering slopes
- A_mid = Mid-section area
```

### Corner Height Calculation

```
H_FL = H (reference)
H_FR = H - (slope_x% × L)
H_BL = H - (slope_y% × W)
H_BR = H - (slope_x% × L) - (slope_y% × W)
```

### Irrigation Design

```
Number of Laterals = W / lateral_spacing + 1
Emitters per Lateral = L / emitter_spacing + 1
Total Emitters = Laterals × Emitters_per_Lateral

Flow Rate (m³/h) = Total_Emitters × (emitter_flow_mL_min / 1000) × 60 / 1000
```

### Metallurgical Estimates

```
Tonnage = Volume × Density
Recoverable Copper = Tonnage × (Grade% / 100) × (Recovery% / 100)
Acid Consumption = Tonnage × acid_rate_kg_ton / 1000
```

## Security Implementation

### Authentication Flow

```
1. User submits credentials
2. Server validates against bcrypt hash
3. JWT access token generated (30 min expiry)
4. JWT refresh token generated (7 day expiry)
5. Client stores tokens securely
6. Access token sent with each request
7. Refresh token used to obtain new access token
```

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(password)  # bcrypt with 12 rounds
verified = pwd_context.verify(password, hashed)
```

### JWT Token Structure

```json
{
  "sub": 1,
  "exp": 1704067200,
  "iat": 1704065400,
  "type": "access"
}
```

## Deployment Guide

### Production Checklist

- [ ] Set strong SECRET_KEY (min 32 characters)
- [ ] Configure SSL/TLS certificates
- [ ] Set up database backups (daily)
- [ ] Configure monitoring (Prometheus + Grafana)
- [ ] Set up log aggregation (ELK Stack)
- [ ] Enable rate limiting
- [ ] Configure CORS for production domains
- [ ] Set up CDN for static assets
- [ ] Configure auto-scaling rules
- [ ] Implement disaster recovery plan

### Environment Variables (Production)

```bash
# Security
SECRET_KEY=your-super-secret-min-32-characters-random-string
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://password@host:6379/0

# CORS
ALLOWED_ORIGINS=https://heapmasterpro.com,https://app.heapmasterpro.com
```

## Performance Optimization

### Database Indexes

```sql
CREATE INDEX idx_pads_project ON pads(project_id);
CREATE INDEX idx_pads_created ON pads(created_at DESC);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_users_email ON users(email);
```

### Caching Strategy

```python
# Redis cache keys pattern
cache_key = f"pad:{pad_id}:calculations"
cache.setex(cache_key, 3600, result)  # 1 hour TTL
```

### Query Optimization

```python
# Use eager loading to prevent N+1 queries
pads = db.query(Pad).options(
    joinedload(Pad.project),
    joinedload(Pad.creator)
).all()
```

## Testing Strategy

### Test Coverage Goals

- Unit Tests: >80% coverage
- Integration Tests: All API endpoints
- E2E Tests: Critical user workflows

### Running Tests

```bash
# Backend tests
cd backend
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test -- --coverage
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL format
   - Verify PostgreSQL is running
   - Check network connectivity

2. **Authentication Failures**
   - Verify SECRET_KEY matches
   - Check token expiration
   - Ensure clock synchronization

3. **3D Visualization Issues**
   - Check Three.js version compatibility
   - Verify WebGL support in browser
   - Clear browser cache

## Support

For technical support and enterprise licensing:
- Email: support@heapmasterpro.com
- Documentation: https://docs.heapmasterpro.com
- Status Page: https://status.heapmasterpro.com
