# PostgreSQL Setup Guide for CarbonSense

## Installation

### macOS (Homebrew)
```bash
brew install postgresql
brew services start postgresql
```

### Windows
Download and install from: https://www.postgresql.org/download/windows/

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

## Create Database & User

### Method 1: Command Line

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE carbonsense_db;

# Create user with password
CREATE USER carbonsense WITH ENCRYPTED PASSWORD 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE carbonsense_db TO carbonsense;

# Connect to new database
\c carbonsense_db

# Grant schema privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO carbonsense;

# Verify
\l                    # List databases
\du                   # List users
```

### Method 2: Using psql Script

```bash
# Create setup.sql
cat > setup.sql << 'EOF'
CREATE DATABASE carbonsense_db;
CREATE USER carbonsense WITH ENCRYPTED PASSWORD 'your_password';
ALTER ROLE carbonsense SET client_encoding TO 'utf8';
ALTER ROLE carbonsense SET default_transaction_isolation TO 'read committed';
ALTER ROLE carbonsense SET default_transaction_deferrable TO on;
ALTER ROLE carbonsense SET default_transaction_level TO 'read committed';
ALTER ROLE carbonsense SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE carbonsense_db TO carbonsense;
EOF

# Run the script
psql -U postgres -f setup.sql
```

---

## Environment Setup

Update your `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=carbonsense
DB_PASSWORD=your_password
DB_NAME=carbonsense_db
```

---

## Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The new driver is: **psycopg2-binary** (PostgreSQL native driver)

---

## Initialize Database Tables

Tables are automatically created on first backend startup via SQLAlchemy:

```bash
# Option 1: Start backend (auto-creates tables)
python3 -c "from models.db_models import Base, engine; Base.metadata.create_all(bind=engine)"
uvicorn main:app --reload --port 8005
```

---

## Verify Connection

```bash
# Test database connection
psql -U carbonsense -d carbonsense_db -h localhost

# List tables
\dt

# Exit
\q
```

---

## Troubleshooting

### "FATAL: database does not exist"
```bash
# Create database
createdb -U postgres carbonsense_db
```

### "FATAL: role does not exist"
```bash
# Create user
createuser -U postgres -P carbonsense
```

### "Permission denied"
```bash
# Grant privileges again
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE carbonsense_db TO carbonsense;
```

### "psycopg2 connection error"
```bash
# Reinstall driver
pip install --upgrade psycopg2-binary
```

---

## Cloud Deployment Setup

### Render.com (Recommended)
1. Create PostgreSQL database on Render
2. Copy connection string: `postgresql://user:password@host:port/dbname`
3. Set in environment variables

### Railway.app
Similar process - they provide PostgreSQL databases

### AWS RDS PostgreSQL
1. Create RDS PostgreSQL instance
2. Update security groups for access
3. Use connection string in `.env`

---

## Migration from MySQL (if needed)

If you had existing MySQL data:

```bash
# Dump MySQL
mysqldump -u root -p carbonsense_db > backup.sql

# Modify SQL for PostgreSQL (change data types)
# Then import to PostgreSQL
psql -U carbonsense -d carbonsense_db < backup.sql
```

---

## Performance Tuning

Edit `/etc/postgresql/14/main/postgresql.conf` (Linux):

```ini
# Connection pooling
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
```

Then restart: `sudo systemctl restart postgresql`

---

## Backup & Restore

```bash
# Backup
pg_dump -U carbonsense -d carbonsense_db > backup.sql

# Restore
psql -U carbonsense -d carbonsense_db < backup.sql

# Automated backup (cron)
0 2 * * * pg_dump -U carbonsense carbonsense_db | gzip > /backups/$(date +\%Y\%m\%d).sql.gz
```

---

## Monitoring

```bash
# Check database size
psql -U postgres

SELECT pg_database.datname,
       pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = 'carbonsense_db';

# List active connections
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;
```

---

✅ PostgreSQL is ready! Start your CarbonSense backend.
