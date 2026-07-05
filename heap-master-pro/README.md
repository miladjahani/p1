# Heap Master Pro - Professional Metallurgical Engineering Platform

A state-of-the-art heap leaching simulation and management system built with modern Python (FastAPI) and React (TypeScript).

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI** - Modern async web framework
- **Pydantic v2** - Data validation
- **SQLModel** - Database ORM
- **NumPy** - Scientific calculations
- **pytest** - Testing framework

### Frontend (React/TypeScript)
- **React 18** - With hooks and concurrent features
- **TypeScript** - Type safety
- **Vite** - Build tooling
- **TailwindCSS** - Styling
- **Zustand** - State management
- **React Query** - Data fetching
- **Three.js** - 3D visualization
- **Recharts** - Charts and graphs

## 📁 Project Structure

```
heap-master-pro/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core configurations
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   └── tests/            # Test files
└── frontend/
    ├── src/
    │   ├── components/   # React components
    │   ├── hooks/        # Custom hooks
    │   ├── services/     # API services
    │   ├── store/        # State management
    │   ├── utils/        # Utilities
    │   └── types/        # TypeScript types
    └── public/           # Static assets
```

## 🚀 Features

### Metallurgical Engine
- Advanced recovery calculations using multivariate regression
- OPEX estimation with detailed cost breakdown
- PLS (Pregnant Leach Solution) analysis
- Production scheduling
- Pad volume calculation with terrain correction
- Acid optimization for pH control

### 3D Visualization
- Interactive pad design with Three.js
- Multi-layer representation (geomembrane, GCL, ore)
- Irrigation system visualization
- Real-time animations (rain/fluid flow)
- Terrain modeling

### Dashboard & Analytics
- Real-time KPI tracking
- Production charts
- Acid consumption monitoring
- Recovery optimization curves
- Export/Import project data

## 🛠️ Setup Instructions

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📊 API Endpoints

- `POST /api/calculate/recovery` - Calculate copper recovery
- `POST /api/calculate/opex` - Calculate operational expenses
- `POST /api/calculate/pls` - Calculate PLS properties
- `POST /api/calculate/schedule` - Generate production schedule
- `POST /api/calculate/volume` - Calculate pad volume
- `POST /api/optimize/acid` - Optimize acid addition

## 🎯 Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend Framework | FastAPI | Async API server |
| Frontend Framework | React 18 | UI components |
| Language | TypeScript | Type safety |
| Styling | TailwindCSS | Utility-first CSS |
| State Management | Zustand | Lightweight state |
| 3D Engine | Three.js | Visualization |
| Charts | Recharts | Data visualization |
| Database | SQLite/PostgreSQL | Data persistence |
| Validation | Pydantic v2 | Data validation |

## 📝 License

MIT License - See LICENSE file for details

## 👥 Authors

Professional Metallurgical Engineering Team
