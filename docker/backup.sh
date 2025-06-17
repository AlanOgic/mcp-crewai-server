#!/bin/bash
# MCP CrewAI Server - Backup Script
# Automated backup for database and agent data

set -euo pipefail

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Database configuration
DB_HOST="postgres"
DB_PORT="5432"
DB_NAME="crewai_db"
DB_USER="crewai"
DB_PASSWORD="${POSTGRES_PASSWORD:-changeme123}"

# Backup directories
DATA_DIR="/app/data"
BACKUP_NAME="mcp_crewai_backup_${TIMESTAMP}"

echo "🔄 Starting MCP CrewAI Server backup: ${BACKUP_NAME}"

# Create backup directory
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

# 1. Backup PostgreSQL database
echo "📊 Backing up PostgreSQL database..."
PGPASSWORD="${DB_PASSWORD}" pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --verbose \
    --no-password \
    --format=custom \
    --file="${BACKUP_DIR}/${BACKUP_NAME}/database.dump"

if [ $? -eq 0 ]; then
    echo "✅ Database backup completed"
else
    echo "❌ Database backup failed"
    exit 1
fi

# 2. Backup agent memory and data
echo "🧠 Backing up agent memory and data..."
if [ -d "${DATA_DIR}" ]; then
    tar -czf "${BACKUP_DIR}/${BACKUP_NAME}/agent_data.tar.gz" \
        -C "${DATA_DIR}" \
        . \
        --exclude="*.tmp" \
        --exclude="*.lock"
    
    if [ $? -eq 0 ]; then
        echo "✅ Agent data backup completed"
    else
        echo "❌ Agent data backup failed"
        exit 1
    fi
else
    echo "⚠️  Data directory not found: ${DATA_DIR}"
fi

# 3. Backup configuration
echo "⚙️  Backing up configuration..."
if [ -f "/app/.env" ]; then
    # Remove sensitive data before backup
    grep -v -E "(API_KEY|PASSWORD|SECRET)" /app/.env > "${BACKUP_DIR}/${BACKUP_NAME}/config.env" || true
    echo "✅ Configuration backup completed (sensitive data excluded)"
fi

# 4. Create metadata file
echo "📝 Creating backup metadata..."
cat > "${BACKUP_DIR}/${BACKUP_NAME}/metadata.json" << EOF
{
    "backup_name": "${BACKUP_NAME}",
    "timestamp": "${TIMESTAMP}",
    "version": "1.0.0",
    "backup_type": "full",
    "components": [
        "postgresql_database",
        "agent_memory",
        "configuration"
    ],
    "size_bytes": $(du -sb "${BACKUP_DIR}/${BACKUP_NAME}" | cut -f1),
    "retention_days": ${RETENTION_DAYS}
}
EOF

# 5. Create compressed archive
echo "🗜️  Creating compressed archive..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}/"
rm -rf "${BACKUP_NAME}/"

# 6. Verify backup integrity
echo "🔍 Verifying backup integrity..."
if tar -tzf "${BACKUP_NAME}.tar.gz" > /dev/null; then
    echo "✅ Backup integrity verified"
else
    echo "❌ Backup integrity check failed"
    exit 1
fi

# 7. Clean old backups
echo "🧹 Cleaning old backups (older than ${RETENTION_DAYS} days)..."
find "${BACKUP_DIR}" -name "mcp_crewai_backup_*.tar.gz" -mtime +${RETENTION_DAYS} -delete

# 8. Generate backup report
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
echo "📊 Backup completed successfully!"
echo "   📁 File: ${BACKUP_NAME}.tar.gz"
echo "   📏 Size: ${BACKUP_SIZE}"
echo "   📅 Timestamp: ${TIMESTAMP}"

# Optional: Upload to cloud storage
if [ "${ENABLE_CLOUD_BACKUP:-false}" = "true" ]; then
    echo "☁️  Uploading to cloud storage..."
    # Add your cloud upload logic here (AWS S3, Google Cloud, etc.)
    # aws s3 cp "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" "s3://your-backup-bucket/"
fi

echo "🎉 Backup process completed successfully!"