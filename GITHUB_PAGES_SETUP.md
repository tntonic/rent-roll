# GitHub Pages Setup Guide

## 🚀 Enabling GitHub Pages for the BI Dashboard

Your static BI dashboard has been pushed to GitHub and is ready to be hosted on GitHub Pages. Follow these steps to enable it:

### 1. Go to Repository Settings
1. Visit your repository: https://github.com/tntonic/rent-roll
2. Click the **Settings** tab at the top of the repository

### 2. Configure GitHub Pages
1. Scroll down to the **Pages** section in the left sidebar
2. Click on **Pages**

### 3. Set Source
1. Under **Source**, select **Deploy from a branch**
2. Choose **main** branch
3. Select **/ (root)** folder
4. Click **Save**

### 4. Wait for Deployment
- GitHub will build and deploy your site (usually takes 5-10 minutes)
- You'll see a checkmark when it's ready

### 5. Access Your Dashboard
Your dashboard will be available at:
**https://tntonic.github.io/rent-roll/**

---

## 📊 Dashboard Features

Once deployed, your dashboard will include:

### Main Features
- **Fund 2 Dashboard**: Complete performance analysis with critical occupancy alerts
- **Fund 3 Dashboard**: Comprehensive metrics with strategic insights  
- **Fund Comparison**: Side-by-side performance analysis

### Interactive Visualizations
- Occupancy rate trends
- Revenue waterfall analysis
- Lease expiration timelines
- Risk assessment gauges
- Tenant concentration charts
- Top property performance tables

### Key Insights Available
- **Fund 2**: 88.0% occupancy (HIGH RISK) - requires immediate intervention
- **Fund 3**: 91.8% occupancy (MEDIUM-HIGH RISK) - concerning but manageable
- **Combined**: $20.7M revenue opportunity from vacant space

---

## 🔧 Updating the Dashboard

To update the dashboard with new data:

1. **Replace Excel files** with new rent roll data
2. **Run export script**:
   ```bash
   python3 export_data_for_web.py
   ```
3. **Commit and push changes**:
   ```bash
   git add docs/data/dashboard_data.json
   git commit -m "Update Q3 2025 data"
   git push
   ```
4. **Wait 5-10 minutes** for GitHub Pages to rebuild

---

## 📱 Mobile Support

The dashboard is fully responsive and works on:
- Desktop computers
- Tablets (iPad, Android tablets)
- Mobile phones (iPhone, Android)

---

## 🎯 Success Metrics

The dashboard tracks these critical KPIs:
- **Occupancy Rate** (Target: 95%+)
- **WALT** (Target: 48+ months) 
- **Revenue Growth** (Target: 3-5% annually)
- **Risk Score** (Target: <30)
- **Leasing Velocity** (Target: 20+ leases/month)

---

## 🆘 Troubleshooting

### If the dashboard doesn't load:
1. Check that GitHub Pages is enabled in Settings
2. Verify the `docs` folder contains all files
3. Check browser console for JavaScript errors
4. Ensure `dashboard_data.json` is accessible

### If charts don't appear:
1. Check browser console for errors
2. Verify Plotly.js is loading correctly
3. Test with a different browser

### For data issues:
1. Verify Excel files are in the correct format
2. Re-run the export script
3. Check JSON file structure

---

## 📞 Support

If you need to update the dashboard or add new features:
1. Modify the source files
2. Run the export script
3. Commit and push changes
4. GitHub Pages will automatically rebuild

The dashboard is now ready for executive presentations and board meetings!

---

*Setup completed: July 22, 2025*