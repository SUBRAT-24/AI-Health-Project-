1. AWS Deployment
2. Google Cloud Deployment
3. Azure Deployment
4. Heroku Deployment

## AWS Deployment Guide

### Prerequisites
- AWS Account with active credentials
- AWS CLI installed and configured
- Docker image pushed to ECR

### Steps

1. **Create EC2 Instance**
   - Instance type: t3.medium or higher
   - OS: Ubuntu 20.04 LTS
   - Security group: Allow ports 22, 80, 443

2. **Install Software**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install docker.io docker-compose -y
   sudo usermod -aG docker $USER
   ```

3. **Clone and Deploy**
   ```bash
   git clone <repo-url>
   cd Project1
   docker-compose -f docker/docker-compose.yml up -d
   ```

4. **Setup Database**
   - Use AWS RDS for MySQL
   - Update connection string in .env

5. **Enable HTTPS**
   - Use AWS Certificate Manager (ACM)
   - Configure with Route53

6. **Setup Monitoring**
   - CloudWatch for logs
   - Auto-scaling groups

### Cost Optimization
- Use t3.micro for dev/test
- Use RDS reserved instances
- Enable S3 lifecycle policies

---

## Google Cloud Deployment

### Prerequisites
- Google Cloud Account
- gcloud CLI installed
- Project created

### Steps

1. **Create Compute Engine Instance**
   - Machine type: n1-standard-1
   - OS: Ubuntu 20.04 LTS
   - Zone: Choose closest to users

2. **Setup Cloud SQL**
   - Create MySQL instance
   - Create database
   - Configure firewall

3. **Deploy Application**
   ```bash
   # SSH into instance
   gcloud compute ssh <instance-name>
   
   # Clone and run
   git clone <repo-url>
   cd Project1
   docker-compose up -d
   ```

4. **Configure Cloud Storage**
   - Create bucket for file uploads
   - Set lifecycle policies

5. **Setup Load Balancer**
   - Create HTTP(S) load balancer
   - Configure SSL certificate

---

## Heroku Deployment

### Prerequisites
- Heroku Account
- Heroku CLI installed
- Git repository

### Steps

1. **Create Procfile**
   ```
   web: gunicorn backend.flask_app:app
   worker: python backend/fastapi_app/main.py
   ```

2. **Deploy**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

3. **Configure Database**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set JWT_SECRET_KEY=your-key
   heroku config:set MYSQL_PASSWORD=your-password
   ```

---

## Environment-Specific Settings

### Development
- DEBUG=True
- Log level: DEBUG
- Database: Local MySQL

### Staging
- DEBUG=False
- Log level: INFO
- Database: Staging RDS

### Production
- DEBUG=False
- Log level: WARNING
- Database: Production RDS
- CDN: Enabled
- Caching: Redis
- HTTPS: Required
