# ⚡ Quick Deployment Steps for Render

## 📋 Prerequisites
- [ ] GitHub account
- [ ] Repository pushed to GitHub

## 🚀 Deployment in 5 Minutes

### 1. Commit & Push Your Code
```bash
cd /Users/macbook/Desktop/Advance\ Computing/TECH004.2/TEC004.2
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Create Render Account
Visit: https://render.com → Sign up with GitHub

### 3. Deploy Your App
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Click **"Deploy an existing repository"**
4. Select your GitHub repo
5. Render auto-reads `render.yaml` configuration ✅
6. Click **"Create Web Service"**

### 4. Wait for Deployment
- Green checkmark = ✅ Success!
- Go to your live URL (e.g., `https://housing-market-dashboard-xxxxx.onrender.com`)

### 5. Connect Custom Domain (Optional)
- Settings → Custom Domains → Enter `Group1.com`
- Follow DNS setup in Render dashboard

---

## 📦 What's Ready for Deployment

✅ **render.yaml** - Deployment config (auto-detected by Render)
✅ **requirements.txt** - Updated with Gunicorn for production
✅ **app.py** - Flask app properly configured
✅ **.gitignore** - Prevents uploading sensitive files

---

## 🔧 Important Notes

### Database
- **SQLite**: Resets when free plan app restarts (~15 min inactivity)
- **Upgrade to PostgreSQL**: If you need persistent data
  - Cost: ~$15/month
  - Add PostgreSQL database in Render
  - Update connection in code

### Scrapers
- Playwright is included in dependencies
- May timeout on free tier (CPU limited)
- Add more workers if needed: Edit `render.yaml`

### Free Plan Limits
- Stops after 15 min inactivity
- First request takes ~30 seconds
- 0.5GB RAM, shared CPU
- **Upgrade to Paid**: For production use

---

## 🛠️ Troubleshooting

### App won't start?
1. Check Render Logs: Dashboard → Service → Logs
2. Look for error messages
3. Verify `requirements.txt` has all imports

### Can't access app?
1. Wait 2-3 minutes for deployment
2. Refresh browser (Ctrl+Shift+R)
3. Check if URL in browser matches Render dashboard

### Database issues?
- SQLite auto-creates on first run
- Check logs for database errors

---

## 🎯 Next: Make Your Domain Custom

Once deployed, connect **Group1.com** to Render:
1. In Render: Service Settings → Custom Domains
2. Add `Group1.com`
3. Update DNS records (Render will show instructions)
4. Wait 24-48 hours for DNS propagation

---

**Deployed URL Format:** `https://[service-name]-xxxxx.onrender.com`
**Example:** `https://housing-market-dashboard-abc123.onrender.com`

Good luck! 🎉
