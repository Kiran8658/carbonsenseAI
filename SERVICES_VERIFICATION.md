# CarbonSense Services Verification ✓

## Setup Summary
Completed on: March 25, 2026

### 1. PostgreSQL Database ✓
- **Status**: Running
- **Host**: localhost
- **Port**: 5432
- **Database**: carbonsense_db
- **User**: postgres
- **Tables**: AUTO-CREATED via SQLAlchemy
- **Verification**: Successfully created on startup

```bash
# Verify PostgreSQL connection:
/opt/homebrew/opt/postgresql@15/bin/psql -U postgres -d carbonsense_db -c "\dt"
```

### 2. Backend API Server ✓
- **Status**: RUNNING
- **Framework**: FastAPI
- **Host**: 0.0.0.0
- **Port**: 8000
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Process**: Python venv with uvicorn

**Start Command:**
```bash
cd /Users/kiran/vnr_hackathon/carbonsense/carbonsense/backend && \
/Users/kiran/vnr_hackathon/carbonsense/carbonsense/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Features:**
- 8 ML/AI Models:
  - ✓ LSTM Forecasting
  - ✓ Anomaly Detection  
  - ✓ Alert System
  - ✓ Advanced Reports
  - ✓ Monte Carlo Simulation
  - ✓ CSV Upload
  - ✓ AI Chatbot
  - ✓ Benchmark/ESG

- Database Integration:
  - ✓ PostgreSQL with psycopg2
  - ✓ Connection Pooling Configured
  - ✓ SQLAlchemy ORM (database-agnostic)

### 3. Frontend Web Application ✓
- **Status**: RUNNING
- **Framework**: Next.js 14+
- **Language**: TypeScript 5.0+
- **Host**: 0.0.0.0
- **Port**: 3001 (Port 3000 was in use, auto-switched)
- **URL**: http://localhost:3001
- **Process**: Node.js with npm

**Start Command:**
```bash
cd /Users/kiran/vnr_hackathon/carbonsense/carbonsense/frontend && npm run dev
```

**Page Access:**
- Dashboard: http://localhost:3001/dashboard
- Analytics: http://localhost:3001/analytics
- Emissions: http://localhost:3001/emissions
- Reports: http://localhost:3001/reports

---

## Environment Configuration

### Backend .env
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=carbonsense_db

GEMINI_API_KEY=[configured]
OPENAI_API_KEY=[configured]
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=INFO
```

### Frontend Configuration
- API_URL: Points to http://localhost:8000
- Environment: Development (with hot-reload)

---

## Service Port Status

| Service | Port | Status | URL |
|---------|------|--------|-----|
| Backend API | 8000 | ✓ RUNNING | http://localhost:8000 |
| Frontend | 3001 | ✓ RUNNING | http://localhost:3001 |
| PostgreSQL | 5432 | ✓ RUNNING | postgres://postgres@localhost:5432/carbonsense_db |

---

## Quick Testing

### Test Backend API
```bash
# Get API status
curl http://localhost:8000/

# View health check
curl http://localhost:8000/health

# Access API documentation
open http://localhost:8000/docs
```

### Test Frontend
```bash
# Open in browser
open http://localhost:3001
```

### Test Database Connection
```bash
psql -U postgres -d carbonsense_db -c "SELECT count(*) FROM user_input_data;"
```

---

## Troubleshooting

### If Backend Is Not Running:
```bash
cd /Users/kiran/vnr_hackathon/carbonsense/carbonsense/backend

# Check if venv exists
ls -la venv/

# Activate venv and start server
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### If Frontend Is Not Running:
```bash
cd /Users/kiran/vnr_hackathon/carbonsense/carbonsense/frontend

# Check node_modules
ls -la node_modules/

# Start dev server
npm run dev

# If port 3000 is in use, it will auto-switch to 3001
```

### If PostgreSQL Is Not Running:
```bash
# Start PostgreSQL service
brew services start postgresql@15

# Verify it's running
brew services list | grep postgresql

# Check database
psql -U postgres -l
```

---

## Next Steps

1. **Test the application**: Visit http://localhost:3001 to interact with the frontend
2. **Submit test data**: Use the dashboard to submit carbon emissions data
3. **View API docs**: Visit http://localhost:8000/docs for complete API documentation
4. **Monitor database**: Tables are automatically created on first startup
5. **Deploy to cloud**: Follow deployment guides in README.md for production deployment

---

## Production Deployment

When ready to deploy to production:

1. **Database**: Use managed PostgreSQL on Render.com or AWS RDS
2. **Backend**: Deploy to Render.com, Railway.app, or AWS ECS
3. **Frontend**: Deploy to Vercel, Netlify, or AWS S3+CloudFront
4. **Environment Variables**: Update credentials for cloud databases and APIs

See POSTGRESQL_SETUP.md and README.md for detailed deployment instructions.

---

**All services are running and fully operational!** 🚀
