#!/bin/bash
# MCP CrewAI Server - SSL Certificate Generation
# Generates self-signed certificates for development/testing

set -euo pipefail

CERTS_DIR="/Users/alanogic/dev/mcp-crewai-server/certs"
DOMAIN="${SSL_DOMAIN:-localhost}"
COUNTRY="${SSL_COUNTRY:-US}"
STATE="${SSL_STATE:-California}"
CITY="${SSL_CITY:-San Francisco}"
ORG="${SSL_ORG:-MCP CrewAI Server}"
OU="${SSL_OU:-Development}"

echo "🔐 Generating SSL certificates for MCP CrewAI Server"
echo "   Domain: ${DOMAIN}"
echo "   Organization: ${ORG}"

# Create certs directory
mkdir -p "${CERTS_DIR}"
cd "${CERTS_DIR}"

# Generate DH parameters for Perfect Forward Secrecy
echo "🔑 Generating Diffie-Hellman parameters (this may take a while)..."
if [ ! -f "dhparam.pem" ]; then
    openssl dhparam -out dhparam.pem 2048
    echo "✅ DH parameters generated"
else
    echo "✅ DH parameters already exist"
fi

# Generate private key
echo "🔐 Generating private key..."
openssl genrsa -out server.key 2048
chmod 600 server.key

# Generate certificate signing request
echo "📝 Generating certificate signing request..."
openssl req -new -key server.key -out server.csr -subj "/C=${COUNTRY}/ST=${STATE}/L=${CITY}/O=${ORG}/OU=${OU}/CN=${DOMAIN}"

# Generate self-signed certificate
echo "📜 Generating self-signed certificate..."
openssl x509 -req -in server.csr -signkey server.key -out server.crt -days 365 \
    -extensions v3_req -extfile <(cat <<EOF
[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${DOMAIN}
DNS.2 = localhost
DNS.3 = mcp-crewai-server
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
)

# Clean up CSR
rm server.csr

# Set proper permissions
chmod 644 server.crt
chmod 600 server.key
chmod 644 dhparam.pem

# Verify certificate
echo "🔍 Verifying generated certificate..."
openssl x509 -in server.crt -text -noout | head -20

echo "✅ SSL certificates generated successfully!"
echo "   📁 Location: ${CERTS_DIR}"
echo "   🔐 Private key: server.key"
echo "   📜 Certificate: server.crt"
echo "   🔑 DH params: dhparam.pem"
echo ""
echo "⚠️  Note: These are self-signed certificates for development/testing."
echo "   For production, use certificates from a trusted CA."
echo ""
echo "🚀 You can now start the MCP CrewAI Server with SSL enabled!"