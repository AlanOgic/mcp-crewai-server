# 🐳 MCP CrewAI Server - Docker Deployment Guide

## 🚀 **Déploiement Docker Complet avec Sécurité**

Votre MCP CrewAI Server est maintenant prêt pour un déploiement Docker professionnel avec accès externe sécurisé.

---

## 📋 **Configuration Rapide**

### **1. Préparation**
```bash
cd /Users/alanogic/dev/mcp-crewai-server

# Copier la configuration Docker
cp .env.docker .env

# Éditer avec vos API keys
nano .env
```

### **2. Générer les Certificats SSL**
```bash
# Générer les certificats pour HTTPS
./docker/generate-certs.sh

# Ou avec domaine personnalisé
SSL_DOMAIN=your-domain.com ./docker/generate-certs.sh
```

### **3. Déploiement**
```bash
# Production complète avec sécurité
docker-compose up -d

# Développement simplifié
docker-compose -f docker-compose.dev.yml up -d

# Avec monitoring complet
docker-compose --profile monitoring up -d
```

---

## 🏗 **Architecture de Déploiement**

```
Internet (Port 443/80)
    ↓
🔒 Nginx Proxy (SSL/TLS)
    ↓
🚀 MCP CrewAI Server (Port 8765)
    ↓
┌─────────────┬─────────────┬─────────────┐
│  📊 Redis    │ 🗄️ PostgreSQL │ 📈 Monitoring │
│  (Cache)    │  (Database)  │ (Prometheus) │
└─────────────┴─────────────┴─────────────┘
```

### **Services Inclus:**
- **🚀 MCP CrewAI Server** - Serveur principal avec évolution autonome
- **🔒 Nginx** - Reverse proxy avec SSL/TLS
- **📊 Redis** - Cache haute performance 
- **🗄️ PostgreSQL** - Base de données persistante
- **📈 Prometheus** - Monitoring et métriques
- **📊 Grafana** - Visualisation des métriques
- **🔍 Elasticsearch** - Logs centralisés (optionnel)
- **💾 Backup** - Sauvegarde automatisée

---

## 🔒 **Sécurité & Accès Externe**

### **Fonctionnalités de Sécurité:**

#### **1. Chiffrement TLS/SSL**
- ✅ HTTPS obligatoire (port 443)
- ✅ Certificats SSL auto-générés
- ✅ Perfect Forward Secrecy
- ✅ TLS 1.2+ uniquement

#### **2. Authentification Multi-Niveau**
- ✅ API Keys pour clients MCP
- ✅ Rate limiting (10 req/sec par IP)
- ✅ Headers de sécurité
- ✅ Protection CORS

#### **3. Isolation Réseau**
- ✅ Réseaux Docker privés
- ✅ Exposition minimale des ports
- ✅ Proxy reverse sécurisé

#### **4. Audit & Monitoring**
- ✅ Logs structurés
- ✅ Métriques Prometheus
- ✅ Health checks automatiques
- ✅ Alertes de sécurité

---

## 🎯 **Méthodes de Déploiement**

### **Option 1: Docker Compose (Recommandé) ✅**

**Avantages:**
- 🏗️ **Orchestration complète** - Tous les services coordonnés
- 🔒 **Sécurité intégrée** - SSL, auth, rate limiting
- 📊 **Monitoring inclus** - Prometheus + Grafana
- 💾 **Persistence** - Données sauvegardées automatiquement
- 🔄 **Scaling facile** - `docker-compose up --scale mcp-crewai-server=3`

**Commandes:**
```bash
# Production sécurisée
docker-compose up -d

# Scaling horizontal
docker-compose up -d --scale mcp-crewai-server=3

# Logs en temps réel
docker-compose logs -f mcp-crewai-server

# Redémarrage
docker-compose restart

# Arrêt propre
docker-compose down
```

### **Option 2: Docker Run Simple**

**Pour tests ou déploiements minimaux:**
```bash
# Build de l'image
docker build -t mcp-crewai-server .

# Run simple (sans sécurité)
docker run -d \
  --name mcp-crewai \
  -p 8765:8765 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env \
  mcp-crewai-server

# Run sécurisé avec SSL
docker run -d \
  --name mcp-crewai \
  -p 8765:8765 \
  -p 8443:8443 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/certs:/app/certs \
  -v $(pwd)/.env:/app/.env \
  -e ENABLE_TLS=true \
  mcp-crewai-server
```

---

## 🌐 **Accès Externe Sécurisé**

### **Configuration DNS & Firewall**

#### **1. DNS (si domaine public)**
```bash
# Pointer votre domaine vers le serveur
your-domain.com.    A    YOUR_SERVER_IP
api.your-domain.com A    YOUR_SERVER_IP
```

#### **2. Firewall (recommandé)**
```bash
# Ubuntu/Debian avec ufw
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP (redirections)
sudo ufw allow 443   # HTTPS
sudo ufw deny 8765   # Bloquer accès direct
sudo ufw enable
```

### **URLs d'Accès:**

#### **Production (HTTPS):**
- **API MCP**: `https://your-domain.com/mcp`
- **Health Check**: `https://your-domain.com/health`
- **Metrics**: `https://your-domain.com/metrics` (restreint)
- **Grafana**: `https://your-domain.com:3000`

#### **Développement (HTTP):**
- **API MCP**: `http://localhost:8765/mcp`
- **Health Check**: `http://localhost:8765/health`

### **Configuration Client MCP:**

#### **Claude Desktop/Code:**
```json
{
  "mcpServers": {
    "mcp-crewai-server": {
      "command": ["curl"],
      "args": [
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-H", "X-API-Key: YOUR_API_KEY",
        "https://your-domain.com/mcp"
      ],
      "description": "Revolutionary MCP CrewAI Server"
    }
  }
}
```

#### **Client Custom:**
```python
import httpx

client = httpx.Client(
    base_url="https://your-domain.com",
    headers={"X-API-Key": "your-api-key"},
    verify=True  # Vérification SSL
)

# Appel MCP
response = client.post("/mcp", json={
    "method": "create_evolving_crew",
    "params": {
        "crew_name": "remote_team",
        "agents_config": [...]
    }
})
```

---

## 📊 **Monitoring & Maintenance**

### **Health Checks:**
```bash
# Vérifier tous les services
docker-compose ps

# Health check détaillé
curl -k https://localhost/health

# Métriques système
curl -k https://localhost/metrics
```

### **Logs:**
```bash
# Logs du serveur principal
docker-compose logs -f mcp-crewai-server

# Logs de tous les services
docker-compose logs -f

# Logs par service
docker-compose logs nginx
docker-compose logs postgres
```

### **Backup Automatique:**
```bash
# Déclencher backup manuel
docker-compose exec backup /backup.sh

# Vérifier les sauvegardes
ls -la ./backups/

# Restaurer depuis backup
./docker/restore.sh backup_20240615_143022.tar.gz
```

### **Scaling & Performance:**
```bash
# Scaler horizontalement
docker-compose up -d --scale mcp-crewai-server=5

# Monitoring des ressources
docker stats

# Optimisation mémoire
docker system prune -a
```

---

## 🔧 **Configuration Avancée**

### **Variables d'Environnement Clés:**

#### **Sécurité:**
```bash
ENABLE_TLS=true
API_KEY_REQUIRED=true
MASTER_API_KEY=your_secure_api_key
RATE_LIMIT_ENABLED=true
MAX_REQUESTS_PER_MINUTE=60
```

#### **Performance:**
```bash
MAX_WORKERS=4
MAX_AGENT_EXECUTION_TIME=300
MAX_AGENT_MEMORY_MB=512
REDIS_URL=redis://redis:6379
DATABASE_URL=postgresql://user:pass@postgres/db
```

#### **Monitoring:**
```bash
MONITORING_ENABLED=true
PROMETHEUS_METRICS=true
LOG_LEVEL=INFO
HEALTH_CHECK_INTERVAL=60
```

### **Certificates SSL Production:**

#### **Let's Encrypt (recommandé):**
```bash
# Installer certbot
sudo apt install certbot

# Générer certificat
sudo certbot certonly --standalone -d your-domain.com

# Copier dans le projet
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./certs/server.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./certs/server.key
```

#### **Renouvellement automatique:**
```bash
# Crontab pour renouvellement
0 0 * * * certbot renew --quiet && docker-compose restart nginx
```

---

## 🚨 **Sécurité Production**

### **Checklist de Sécurité:**

- ✅ **SSL/TLS activé** avec certificats valides
- ✅ **API Keys uniques** et sécurisées
- ✅ **Rate limiting** configuré
- ✅ **Firewall** configuré (ports 80, 443 uniquement)
- ✅ **Mots de passe forts** pour bases de données
- ✅ **Logs d'audit** activés
- ✅ **Backup automatique** configuré
- ✅ **Monitoring** en place
- ✅ **Accès admin restreint**
- ✅ **Headers de sécurité** configurés

### **Hardening Supplémentaire:**
```bash
# Changer les mots de passe par défaut
POSTGRES_PASSWORD=super_secure_password_123
REDIS_PASSWORD=redis_secure_password_456
GRAFANA_PASSWORD=grafana_admin_password_789

# Restricter l'accès admin
ALLOWED_ADMIN_IPS=192.168.1.100,10.0.0.5

# Audit avancé
AUDIT_LOGGING=true
SECURITY_HEADERS=true
INTRUSION_DETECTION=true
```

---

## 🎉 **Déploiement Complet!**

Votre **MCP CrewAI Server** est maintenant:

✅ **Déployé avec Docker Compose**  
✅ **Sécurisé avec SSL/TLS**  
✅ **Accessible depuis l'externe**  
✅ **Monitoré avec Prometheus**  
✅ **Sauvegardé automatiquement**  
✅ **Prêt pour la production**  

### **Prochaines Étapes:**
1. **Tester l'accès externe** depuis un client MCP
2. **Configurer le monitoring** avec alertes
3. **Mettre en place CI/CD** pour les mises à jour
4. **Documenter l'API** pour votre équipe

**Félicitations! Vous avez un système d'IA collaborative révolutionnaire déployé de façon professionnelle! 🚀**