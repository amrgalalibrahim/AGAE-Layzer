# 🚀 Quick Deploy - AGEA-Layzer V2.0

## Fastest Way to Deploy Permanently (5 Minutes)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `agea-layzer`
3. Description: `AGEA-Layzer V2.0 - Lysine Lactylation Site Prediction Tool`
4. Make it **Public**
5. Click "Create repository"

### Step 2: Push Your Code

Copy these commands (replace YOUR_USERNAME):

```bash
cd /home/ubuntu/AGAE_Layzer_V2

# Set your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/agea-layzer.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

You'll be asked for GitHub credentials. Use a **Personal Access Token** as password:
- Go to https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Select "repo" scope
- Copy the token and use it as password

### Step 3: Deploy on Railway

1. Go to https://railway.app
2. Click "Login" → Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose `agea-layzer` repository
6. Click "Deploy Now"

**That's it!** ✨

Railway will:
- Auto-detect configuration from `railway.json`
- Install dependencies from `requirements_deploy.txt`
- Start the server with Gunicorn
- Provide a permanent HTTPS URL

### Your Permanent URL:

Railway will give you a URL like:
```
https://agea-layzer-production.up.railway.app
```

This URL is **permanent** and will work 24/7!

---

## Alternative: Deploy on Render (Also Free)

If Railway doesn't work, try Render:

1. Go to https://render.com
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect `agea-layzer` repository
5. Click "Create Web Service"

Your URL will be:
```
https://agea-layzer.onrender.com
```

---

## What You Get

✅ **Permanent HTTPS URL**  
✅ **Automatic SSL certificate**  
✅ **24/7 uptime**  
✅ **Auto-deploy on git push**  
✅ **Free hosting**  
✅ **Custom domain support**  

---

## Verify Deployment

Once deployed, test your site:

```bash
# Check health
curl https://YOUR-URL.up.railway.app/api/health

# Should return:
# {"service":"AGEA-Layzer","status":"healthy","version":"2.0"}
```

Open in browser:
```
https://YOUR-URL.up.railway.app
```

---

## Update Your Site Later

To make changes:

```bash
# Edit files
nano app_production.py

# Commit and push
git add .
git commit -m "Update application"
git push origin main

# Railway/Render auto-deploys in 2 minutes!
```

---

## Need Help?

See full guide: `PERMANENT_DEPLOYMENT_GUIDE.md`

**Creator**: Amr G. A. Ibrahim  
**Email**: amrgalalibrahim@gmail.com

---

**Time to deploy**: ~5 minutes  
**Cost**: $0 (Free tier)  
**Difficulty**: Easy ⭐⭐☆☆☆

