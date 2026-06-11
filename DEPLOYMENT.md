# 🚀 Deployment Guide - Render

## Step 1: Prepare Your Repository

Your repository is already set up! ✅

## Step 2: Create Render Account
1. Go to [https://render.com](https://render.com)
2. Sign up with GitHub (recommended) or email
3. Authorize Render to access your GitHub repositories

## Step 3: Connect Your GitHub Repository to Render
1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Select **"Deploy an existing repository"**
3. Search for your repository: **"housing-market-dashboard"** (or your repo name)
4. Connect it

## Step 4: Configure Your Web Service
Render will auto-detect settings from `render.yaml`. If not:

**Manual Configuration:**
- **Name:** `housing-market-dashboard` (or your preferred name)
- **Region:** `Oregon` (closest to most users)
- **Branch:** `main`
- **Runtime:** `Python`
- **Build Command:** 
  ```
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```
  gunicorn --workers 2 --worker-class sync --timeout 30 --bind 0.0.0.0:$PORT app:app
  ```
- **Plan:** `Free` (optional - upgrade later if needed)

## Step 5: Environment Variables (Important!)
If your app uses `.env` file, add environment variables in Render:

1. Go to **Environment** in Render dashboard
2. Add any variables from your `.env` file
3. Example variables:
   - `FLASK_ENV` = `production`
   - `DATABASE_URL` (if applicable)

## Step 6: Deploy!
1. Click **"Create Web Service"**
2. Render will automatically deploy when you:
   - Push to your main branch
   - Or click **"Manual Deploy"** in Render dashboard

3. Monitor deployment in the **Logs** tab
4. Once complete, you'll get a URL: `https://housing-market-dashboard-xxxxx.onrender.com`

## Step 7: Set Custom Domain (Optional)
1. In Render dashboard, go to your service
2. Click **"Settings"** → **"Custom Domains"**
3. Enter your domain (e.g., `Group1.com`)
4. Follow DNS instructions from Render

## ⚠️ Important Considerations for Your App

### Database (SQLite)
- **Free plan limitation:** SQLite database resets when app restarts
- **Solution options:**
  - Use PostgreSQL (add to Render for ~$15/month)
  - Or accept data loss on restart
  - To add PostgreSQL:
    1. Create new PostgreSQL database in Render
    2. Update `db_connection.py` to use PostgreSQL connection string
    3. Add `psycopg2>=2.9.0` to requirements.txt

### Web Scraper (Playwright)
- **Free plan limitation:** Playwright needs system dependencies
- **Solution:** Already handled by Render's Python buildpack
- **Important:** Scrapers might timeout on free plan (limited CPU)

### Cold Starts
- Free plan: App sleeps after 15 min inactivity
- First request takes ~30 seconds
- Click **"Keep Alive"** to prevent sleep

## Troubleshooting

### Deployment Fails
1. Check **Logs** tab in Render dashboard
2. Common issues:
   - Missing dependencies → Update `requirements.txt`
   - Wrong start command → Check `render.yaml`
   - Port binding → Ensure using `$PORT` environment variable

### App Crashes After Deploy
1. Click **"Logs"** to see error messages
2. Common issues:
   - Database not initialized → Check `create_tables()` call
   - Missing environment variables → Add to Render dashboard
   - Import errors → Verify all modules in `requirements.txt`

### Can't Access Database
- SQLite resets on restart; switch to PostgreSQL for production
- Or implement database restoration logic

## Next Steps
1. **Test locally first:** `python app.py` or `flask run`
2. **Push to GitHub:** Make sure all files are committed
3. **Monitor in production:** Check Render Logs regularly
4. **Setup error alerts:** Configure in Render settings

---
📝 **Note:** Update this file if you make changes to deployment!
