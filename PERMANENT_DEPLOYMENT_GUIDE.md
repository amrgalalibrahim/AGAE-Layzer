# AGEA-Layzer V2.0 - Permanent Deployment Guide

This guide provides step-by-step instructions for deploying AGEA-Layzer V2.0 permanently on various hosting platforms.

## 🚀 Quick Deploy Options

Your application is now ready for permanent deployment on any of these platforms:

### Option 1: Railway (Recommended - Easiest)
### Option 2: Render (Free tier available)
### Option 3: Heroku (Popular choice)
### Option 4: Docker (Any platform)
### Option 5: PythonAnywhere (Python-specific)

---

## 🎯 Option 1: Railway (RECOMMENDED)

Railway offers free hosting with automatic deployments from GitHub.

### Steps:

1. **Create GitHub Repository**
   ```bash
   # Push your code to GitHub
   cd /home/ubuntu/AGAE_Layzer_V2
   git remote add origin https://github.com/YOUR_USERNAME/agea-layzer.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to https://railway.app
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect the configuration from `railway.json`
   - Click "Deploy"

3. **Access Your Site**
   - Railway will provide a URL like: `https://agea-layzer-production.up.railway.app`
   - Your site will be live in ~2 minutes!

### Railway Features:
- ✅ **Free tier**: 500 hours/month, $5 credit
- ✅ **Auto-deploy**: Pushes to GitHub trigger deployments
- ✅ **HTTPS**: Automatic SSL certificates
- ✅ **Custom domain**: Add your own domain
- ✅ **Zero configuration**: Works out of the box

---

## 🎨 Option 2: Render

Render offers generous free tier with automatic SSL.

### Steps:

1. **Push to GitHub** (same as Railway)

2. **Deploy on Render**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically
   - Click "Create Web Service"

3. **Configuration** (if not auto-detected):
   - Build Command: `pip install -r requirements_deploy.txt`
   - Start Command: `gunicorn app_production:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120`
   - Python Version: 3.11.0

### Render Features:
- ✅ **Free tier**: 750 hours/month
- ✅ **Auto-deploy**: Git push triggers deployment
- ✅ **HTTPS**: Free SSL certificates
- ✅ **Custom domain**: Free
- ✅ **Sleep after inactivity**: Wakes up on request

---

## 🔷 Option 3: Heroku

Classic platform with extensive documentation.

### Steps:

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login and Create App**
   ```bash
   cd /home/ubuntu/AGAE_Layzer_V2
   heroku login
   heroku create agea-layzer
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **Open Your Site**
   ```bash
   heroku open
   ```

### Heroku Features:
- ✅ **Free tier**: 550 dyno hours/month
- ✅ **Easy CLI**: Simple commands
- ✅ **Add-ons**: Extensive marketplace
- ✅ **Custom domain**: Available
- ✅ **Logs**: `heroku logs --tail`

---

## 🐳 Option 4: Docker Deployment

Deploy anywhere that supports Docker containers.

### Build and Run Locally:
```bash
cd /home/ubuntu/AGAE_Layzer_V2

# Build image
docker build -t agea-layzer:latest .

# Run container
docker run -d -p 5000:5000 --name agea-layzer agea-layzer:latest

# Access at http://localhost:5000
```

### Deploy to Cloud Platforms:

#### Google Cloud Run:
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/agea-layzer

# Deploy
gcloud run deploy agea-layzer \
  --image gcr.io/PROJECT_ID/agea-layzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### AWS ECS/Fargate:
```bash
# Build and push to ECR
aws ecr create-repository --repository-name agea-layzer
docker tag agea-layzer:latest AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/agea-layzer
docker push AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/agea-layzer

# Deploy via ECS console or CLI
```

#### DigitalOcean App Platform:
- Go to https://cloud.digitalocean.com/apps
- Click "Create App"
- Select "Docker Hub" or "GitHub"
- Configure and deploy

---

## 🐍 Option 5: PythonAnywhere

Python-specific hosting with free tier.

### Steps:

1. **Create Account**
   - Go to https://www.pythonanywhere.com
   - Sign up for free account

2. **Upload Code**
   ```bash
   # Create tar.gz package
   cd /home/ubuntu
   tar -czf agea-layzer.tar.gz AGAE_Layzer_V2/
   
   # Upload via PythonAnywhere web interface
   ```

3. **Setup Web App**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Flask"
   - Set working directory: `/home/YOUR_USERNAME/AGAE_Layzer_V2`
   - Set WSGI file to point to `app_production:app`

4. **Install Dependencies**
   ```bash
   # In PythonAnywhere console
   cd AGAE_Layzer_V2
   pip3 install -r requirements_deploy.txt
   ```

5. **Reload Web App**
   - Click "Reload" button
   - Access at: `https://YOUR_USERNAME.pythonanywhere.com`

### PythonAnywhere Features:
- ✅ **Free tier**: Always free for one app
- ✅ **Python-focused**: Optimized for Python apps
- ✅ **Easy setup**: Web-based configuration
- ✅ **Scheduled tasks**: Cron jobs available

---

## 📦 Files Included for Deployment

Your repository includes all necessary configuration files:

```
AGAE_Layzer_V2/
├── Procfile                    # Heroku/Railway process definition
├── runtime.txt                 # Python version specification
├── requirements_deploy.txt     # Production dependencies
├── Dockerfile                  # Docker container definition
├── .dockerignore              # Docker build exclusions
├── railway.json               # Railway configuration
├── render.yaml                # Render configuration
├── .gitignore                 # Git exclusions
├── app_production.py          # Production Flask app
└── [all other application files]
```

---

## 🔧 Environment Variables

Some platforms may require environment variables:

```bash
PORT=5000                      # Auto-set by most platforms
PYTHON_VERSION=3.11.0         # Python version
```

---

## 🌐 Custom Domain Setup

### Railway:
1. Go to your project settings
2. Click "Domains"
3. Add custom domain
4. Update DNS records as instructed

### Render:
1. Go to service settings
2. Click "Custom Domain"
3. Add domain and update DNS

### Heroku:
```bash
heroku domains:add www.yourdomain.com
# Update DNS to point to Heroku
```

---

## 📊 Monitoring & Logs

### Railway:
```bash
# View logs in web dashboard
# Or use CLI: railway logs
```

### Render:
```bash
# View logs in web dashboard
# Real-time streaming available
```

### Heroku:
```bash
heroku logs --tail
heroku logs --source app
```

### Docker:
```bash
docker logs -f agea-layzer
```

---

## 🔄 Continuous Deployment

All platforms support automatic deployment:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```

2. **Automatic Deploy**:
   - Railway, Render, and Heroku automatically detect changes
   - New version deployed within 2-5 minutes
   - Zero downtime deployment

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Plans Start At |
|----------|-----------|---------------------|
| Railway | $5 credit/month | $5/month |
| Render | 750 hours/month | $7/month |
| Heroku | 550 hours/month | $7/month |
| PythonAnywhere | 1 app always free | $5/month |
| Google Cloud Run | 2M requests/month | Pay-as-you-go |
| DigitalOcean | - | $5/month |

---

## ✅ Recommended Deployment Path

For **easiest permanent deployment**:

1. **Create GitHub account** (if you don't have one)
2. **Create new repository** named "agea-layzer"
3. **Push code to GitHub**:
   ```bash
   cd /home/ubuntu/AGAE_Layzer_V2
   git remote add origin https://github.com/YOUR_USERNAME/agea-layzer.git
   git branch -M main
   git push -u origin main
   ```
4. **Deploy on Railway**:
   - Visit https://railway.app
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub"
   - Select your repository
   - Wait 2 minutes
   - Done! 🎉

Your permanent URL will be: `https://agea-layzer-production.up.railway.app`

---

## 🆘 Troubleshooting

### Port Issues:
- Most platforms set `PORT` environment variable automatically
- App is configured to use `$PORT` from environment

### Memory Issues:
- Free tiers typically have 512MB RAM
- App uses ~100MB, should be fine
- If issues occur, upgrade to paid tier

### Timeout Issues:
- Gunicorn timeout set to 120 seconds
- Adjust in `Procfile` if needed: `--timeout 180`

### Build Failures:
- Check Python version matches `runtime.txt`
- Verify all dependencies in `requirements_deploy.txt`
- Check platform logs for specific errors

---

## 📞 Support

**Creator**: Amr G. A. Ibrahim  
**Email**: amrgalalibrahim@gmail.com

**Citation**:
```
Ibrahim, A. G. A. & Adriano, E. A. (2025). 
AGEA-Layzer: An in-silico tool for predicting lysine lactylation sites.
```

---

## 🎉 You're Ready!

Your AGEA-Layzer V2.0 application is fully prepared for permanent deployment. Choose your preferred platform and follow the steps above. Within minutes, you'll have a permanent, publicly accessible website!

**Good luck with your deployment! 🚀**

