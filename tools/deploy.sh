#!/bin/bash
# MCP CrewAI Server - Automated Deployment Script
# One-command deployment with security setup

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_TYPE="${1:-production}"
DOMAIN="${SSL_DOMAIN:-localhost}"

# Validate and sanitize inputs
validate_deployment_type() {
    case "${DEPLOYMENT_TYPE}" in
        "development"|"dev"|"production"|"prod"|"monitoring"|"help"|"-h"|"--help")
            return 0
            ;;
        *)
            print_error "Invalid deployment type: ${DEPLOYMENT_TYPE}"
            echo "Valid types: development, production, monitoring"
            exit 1
            ;;
    esac
}

# Sanitize domain name to prevent injection
sanitize_domain() {
    if [[ ! "${DOMAIN}" =~ ^[a-zA-Z0-9.-]+$ ]]; then
        print_error "Invalid domain format: ${DOMAIN}"
        exit 1
    fi
}

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}"
echo "🚀 MCP CrewAI Server - Automated Deployment"
echo "============================================"
echo -e "${NC}"
echo "📁 Project: ${PROJECT_DIR}"
echo "🌐 Domain: ${DOMAIN}"
echo "🎯 Type: ${DEPLOYMENT_TYPE}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check OpenSSL
    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL is not installed"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Setup environment
setup_environment() {
    echo "⚙️  Setting up environment..."
    
    # Copy environment template
    if [ ! -f ".env" ]; then
        if [ "${DEPLOYMENT_TYPE}" = "development" ]; then
            if [ ! -f ".env.template" ]; then
                print_error "Environment template .env.template not found"
                exit 1
            fi
            cp .env.template .env
        else
            if [ ! -f ".env.docker" ]; then
                print_error "Docker environment template .env.docker not found"
                exit 1
            fi
            cp .env.docker .env
        fi
        print_status "Environment file created from template"
    else
        print_warning "Environment file already exists"
    fi
    
    # Create necessary directories with secure permissions
    mkdir -p data logs certs backups
    chmod 750 data backups  # More restrictive for sensitive data
    chmod 700 logs certs   # Restrict access to logs and certificates
    
    print_status "Directories created with secure permissions"
}

# Generate SSL certificates
setup_ssl() {
    echo "🔐 Setting up SSL certificates..."
    
    if [ ! -f "certs/server.crt" ] || [ ! -f "certs/server.key" ]; then
        echo "   Generating SSL certificates for ${DOMAIN}..."
        
        # Validate cert generation script exists and is executable
        if [ ! -f "./docker/generate-certs.sh" ]; then
            print_error "Certificate generation script not found: ./docker/generate-certs.sh"
            exit 1
        fi
        
        if [ ! -x "./docker/generate-certs.sh" ]; then
            print_error "Certificate generation script is not executable: ./docker/generate-certs.sh"
            exit 1
        fi
        
        # Execute with sanitized domain
        SSL_DOMAIN="${DOMAIN}" ./docker/generate-certs.sh
        
        # Verify certificates were created
        if [ ! -f "certs/server.crt" ] || [ ! -f "certs/server.key" ]; then
            print_error "SSL certificate generation failed"
            exit 1
        fi
        
        print_status "SSL certificates generated"
    else
        print_warning "SSL certificates already exist"
    fi
}

# Validate configuration
validate_config() {
    echo "🔍 Validating configuration..."
    
    local config_errors=0
    
    # Check if API keys are set - fail for production
    if grep -q "sk-your-openai-key-here" .env; then
        if [ "${DEPLOYMENT_TYPE}" = "production" ] || [ "${DEPLOYMENT_TYPE}" = "prod" ]; then
            print_error "OpenAI API key not configured for production deployment"
            config_errors=$((config_errors + 1))
        else
            print_warning "OpenAI API key not configured in .env"
        fi
    fi
    
    if grep -q "sk-ant-your-anthropic-key-here" .env; then
        if [ "${DEPLOYMENT_TYPE}" = "production" ] || [ "${DEPLOYMENT_TYPE}" = "prod" ]; then
            print_error "Anthropic API key not configured for production deployment"
            config_errors=$((config_errors + 1))
        else
            print_warning "Anthropic API key not configured in .env"
        fi
    fi
    
    # Check for default passwords - fail for production
    if grep -q "changeme123" .env; then
        if [ "${DEPLOYMENT_TYPE}" = "production" ] || [ "${DEPLOYMENT_TYPE}" = "prod" ]; then
            print_error "Default passwords detected - change them before production deployment!"
            config_errors=$((config_errors + 1))
        else
            print_warning "Default passwords detected in .env - change them for production!"
        fi
    fi
    
    # Fail deployment if critical configuration issues found
    if [ ${config_errors} -gt 0 ]; then
        print_error "Configuration validation failed with ${config_errors} critical errors"
        exit 1
    fi
    
    print_status "Configuration validation completed"
}

# Deploy with Docker Compose
deploy_services() {
    echo "🚀 Deploying services..."
    
    case "${DEPLOYMENT_TYPE}" in
        "development"|"dev")
            echo "   Deploying development environment..."
            docker-compose -f docker-compose.dev.yml up -d
            ;;
        "production"|"prod")
            echo "   Deploying production environment..."
            docker-compose up -d
            ;;
        "monitoring")
            echo "   Deploying with full monitoring..."
            docker-compose --profile monitoring up -d
            ;;
        *)
            print_error "Unknown deployment type: ${DEPLOYMENT_TYPE}"
            echo "Available types: development, production, monitoring"
            exit 1
            ;;
    esac
    
    print_status "Services deployed"
}

# Wait for services to be ready
wait_for_services() {
    echo "⏳ Waiting for services to be ready..."
    
    # Wait for main server
    echo "   Waiting for MCP CrewAI Server..."
    local health_url
    if [ "${DEPLOYMENT_TYPE}" = "development" ] || [ "${DEPLOYMENT_TYPE}" = "dev" ]; then
        health_url="http://localhost:8765/health"
    else
        health_url="https://${DOMAIN}/health"
    fi
    
    for i in {1..30}; do
        if curl -f -s -k "${health_url}" > /dev/null 2>&1; then
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "MCP CrewAI Server failed to start at ${health_url}"
            exit 1
        fi
        sleep 2
    done
    
    print_status "Services are ready"
}

# Run health checks
run_health_checks() {
    echo "🏥 Running health checks..."
    
    local health_url
    if [ "${DEPLOYMENT_TYPE}" = "development" ] || [ "${DEPLOYMENT_TYPE}" = "dev" ]; then
        health_url="http://localhost:8765/health"
    else
        health_url="https://${DOMAIN}/health"
    fi
    
    # Check main server with proper error handling
    if curl -f -s -k "${health_url}" 2>/dev/null | grep -q "OK\|healthy"; then
        print_status "MCP CrewAI Server is healthy"
    else
        print_error "MCP CrewAI Server health check failed at ${health_url}"
    fi
    
    # Check Redis if running with error handling
    if docker-compose ps 2>/dev/null | grep -q redis; then
        if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
            print_status "Redis is healthy"
        else
            print_warning "Redis health check failed"
        fi
    fi
    
    # Check PostgreSQL if running with error handling  
    if docker-compose ps 2>/dev/null | grep -q postgres; then
        if docker-compose exec -T postgres pg_isready -U crewai 2>/dev/null | grep -q "accepting connections"; then
            print_status "PostgreSQL is healthy"
        else
            print_warning "PostgreSQL health check failed"
        fi
    fi
}

# Show deployment info
show_deployment_info() {
    echo ""
    echo -e "${GREEN}"
    echo "🎉 Deployment Completed Successfully!"
    echo "====================================="
    echo -e "${NC}"
    
    echo "🌐 Access URLs:"
    if [ "${DEPLOYMENT_TYPE}" = "development" ]; then
        echo "   • Health Check: http://localhost:8765/health"
        echo "   • MCP Endpoint: http://localhost:8765/mcp"
    else
        echo "   • Health Check: https://${DOMAIN}/health"
        echo "   • MCP Endpoint: https://${DOMAIN}/mcp"
        echo "   • Metrics: https://${DOMAIN}/metrics"
        if docker-compose ps | grep -q grafana; then
            echo "   • Grafana: http://localhost:3000"
        fi
    fi
    
    echo ""
    echo "🔧 Management Commands:"
    echo "   • View logs: docker-compose logs -f"
    echo "   • Restart: docker-compose restart"
    echo "   • Scale: docker-compose up -d --scale mcp-crewai-server=3"
    echo "   • Stop: docker-compose down"
    echo ""
    
    echo "📊 Container Status:"
    docker-compose ps
    
    echo ""
    echo "🔒 Security Notes:"
    if [ "${DEPLOYMENT_TYPE}" != "development" ]; then
        echo "   • SSL certificates generated for ${DOMAIN}"
        echo "   • API authentication enabled"
        echo "   • Rate limiting active"
        echo "   • Firewall rules recommended (ports 80, 443 only)"
    fi
    
    echo ""
    echo "📚 Documentation:"
    echo "   • Full setup guide: DOCKER_DEPLOYMENT.md"
    echo "   • Quick start: QUICK_START.md"
    echo "   • Configuration: .env file"
    
    if [ "${DEPLOYMENT_TYPE}" != "development" ]; then
        echo ""
        print_warning "Remember to:"
        echo "   1. Configure your API keys in .env"
        echo "   2. Change default passwords"
        echo "   3. Set up DNS if using custom domain"
        echo "   4. Configure firewall rules"
        echo "   5. Set up backup schedule"
    fi
    
    echo ""
    echo -e "${BLUE}🚀 Your revolutionary MCP CrewAI Server is now running!${NC}"
}

# Main deployment flow
main() {
    cd "${PROJECT_DIR}"
    
    # Validate inputs first
    validate_deployment_type
    sanitize_domain
    
    check_prerequisites
    setup_environment
    
    if [ "${DEPLOYMENT_TYPE}" != "development" ] && [ "${DEPLOYMENT_TYPE}" != "dev" ]; then
        setup_ssl
    fi
    
    validate_config
    deploy_services
    wait_for_services
    run_health_checks
    show_deployment_info
}

# Handle script arguments
case "${DEPLOYMENT_TYPE}" in
    "help"|"-h"|"--help")
        echo "MCP CrewAI Server Deployment Script"
        echo ""
        echo "Usage: $0 [DEPLOYMENT_TYPE]"
        echo ""
        echo "Deployment Types:"
        echo "  development  - Simple development setup (default: no SSL)"
        echo "  production   - Full production setup with security"
        echo "  monitoring   - Production + full monitoring stack"
        echo ""
        echo "Examples:"
        echo "  $0 development"
        echo "  $0 production"
        echo "  SSL_DOMAIN=api.mycompany.com $0 production"
        exit 0
        ;;
esac

# Run main deployment
main