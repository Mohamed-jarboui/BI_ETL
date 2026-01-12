# MERN Application Integration Guide

## Power BI Dashboard Integration

This guide shows how to integrate the Power BI dashboard into your MERN application.

---

## Option 1: Power BI Service Embed (Recommended for Production)

### Prerequisites
- Power BI Pro or Premium account
- Dashboard published to Power BI Service
- Power BI Embedded REST API access

### Step 1: Create React Component

Create `frontend/src/components/BIDashboard.jsx`:

```jsx
import React, { useEffect, useState } from 'react';
import './BIDashboard.css';

const BIDashboard = () => {
  const [embedUrl, setEmbedUrl] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get embed URL from environment or backend API
    const url = process.env.REACT_APP_POWERBI_EMBED_URL;
    
    if (url) {
      setEmbedUrl(url);
      setLoading(false);
    } else {
      // Fetch from backend API
      fetchEmbedToken();
    }
  }, []);

  const fetchEmbedToken = async () => {
    try {
      const response = await fetch('/api/powerbi/embed-token');
      const data = await response.json();
      setEmbedUrl(data.embedUrl);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching embed token:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading Business Intelligence Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="bi-dashboard-container">
      <div className="dashboard-header">
        <h1>Business Intelligence Dashboard</h1>
        <p>E-commerce Performance Analytics</p>
      </div>
      
      <div className="dashboard-iframe-wrapper">
        <iframe
          title="E-commerce BI Dashboard"
          width="100%"
          height="100%"
          src={embedUrl}
          frameBorder="0"
          allowFullScreen={true}
        />
      </div>
    </div>
  );
};

export default BIDashboard;
```

### Step 2: Create Stylesheet

Create `frontend/src/components/BIDashboard.css`:

```css
.bi-dashboard-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.dashboard-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.dashboard-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
}

.dashboard-header p {
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
  font-size: 1rem;
}

.dashboard-iframe-wrapper {
  flex: 1;
  padding: 1rem;
  overflow: hidden;
}

.dashboard-iframe-wrapper iframe {
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  height: calc(100% - 2rem);
}

.dashboard-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-header h1 {
    font-size: 1.5rem;
  }
  
  .dashboard-header p {
    font-size: 0.9rem;
  }
  
  .dashboard-iframe-wrapper {
    padding: 0.5rem;
  }
}
```

### Step 3: Add Route

In `frontend/src/App.jsx`:

```jsx
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import BIDashboard from './components/BIDashboard';

function App() {
  return (
    <Router>
      <Routes>
        {/* Existing routes */}
        <Route path="/dashboard" element={<BIDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
```

### Step 4: Add Navigation Link

Add to your navigation menu:

```jsx
<NavLink to="/dashboard">
  <i className="fas fa-chart-line"></i>
  Analytics Dashboard
</NavLink>
```

### Step 5: Configure Environment Variables

In `frontend/.env`:

```env
REACT_APP_POWERBI_EMBED_URL=https://app.powerbi.com/view?r=YOUR_EMBED_CODE
```

---

## Option 2: Public Embed (Simple, No Auth Required)

### Step 1: Publish to Web in Power BI

1. Open your dashboard in Power BI Desktop
2. Click **File** → **Publish to Web**
3. Click **Create embed code**
4. **⚠ WARNING**: This makes your data publicly accessible
5. Copy the embed code

### Step 2: Use Embed URL Directly

```jsx
const BIDashboard = () => {
  // Direct embed URL from Publish to Web
  const embedUrl = "https://app.powerbi.com/view?r=YOUR_PUBLIC_EMBED_CODE";

  return (
    <div className="bi-dashboard-container">
      <iframe
        title="E-commerce BI Dashboard"
        width="100%"
        height="800"
        src={embedUrl}
        frameBorder="0"
        allowFullScreen={true}
      />
    </div>
  );
};
```

---

## Option 3: PDF Export (Offline Alternative)

### Step 1: Export Dashboard as PDF

1. In Power BI Desktop, click **File** → **Export to PDF**
2. Save as `ecommerce_bi_dashboard.pdf`

### Step 2: Serve PDF from MERN App

```jsx
import React from 'react';

const BIDashboard = () => {
  return (
    <div className="bi-dashboard-container">
      <div className="dashboard-header">
        <h1>Business Intelligence Dashboard</h1>
        <a 
          href="/assets/ecommerce_bi_dashboard.pdf" 
          download
          className="download-btn"
        >
          Download PDF Report
        </a>
      </div>
      
      <div className="pdf-viewer">
        <iframe
          src="/assets/ecommerce_bi_dashboard.pdf"
          width="100%"
          height="800"
          title="BI Dashboard PDF"
        />
      </div>
    </div>
  );
};
```

---

## Option 4: Backend API with Embed Tokens (Advanced)

### Step 1: Create Backend Endpoint

In `backend/routes/powerbi.js`:

```javascript
const express = require('express');
const router = express.Router();
const axios = require('axios');

// Get Power BI Embed Token
router.get('/embed-token', async (req, res) => {
  try {
    // Get Azure AD token
    const tokenResponse = await axios.post(
      `https://login.microsoftonline.com/${process.env.TENANT_ID}/oauth2/v2.0/token`,
      new URLSearchParams({
        'grant_type': 'client_credentials',
        'client_id': process.env.CLIENT_ID,
        'client_secret': process.env.CLIENT_SECRET,
        'scope': 'https://analysis.windows.net/powerbi/api/.default'
      })
    );

    const accessToken = tokenResponse.data.access_token;

    // Get embed token
    const embedResponse = await axios.post(
      `https://api.powerbi.com/v1.0/myorg/groups/${process.env.WORKSPACE_ID}/reports/${process.env.REPORT_ID}/GenerateToken`,
      {
        accessLevel: 'View'
      },
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      }
    );

    res.json({
      embedUrl: embedResponse.data.embedUrl,
      embedToken: embedResponse.data.token,
      reportId: process.env.REPORT_ID
    });

  } catch (error) {
    console.error('Error generating embed token:', error);
    res.status(500).json({ error: 'Failed to generate embed token' });
  }
});

module.exports = router;
```

### Step 2: Register Route

In `backend/server.js`:

```javascript
const powerbiRoutes = require('./routes/powerbi');
app.use('/api/powerbi', powerbiRoutes);
```

---

## Testing the Integration

### Checklist

- [ ] Dashboard loads without errors
- [ ] All visuals are interactive
- [ ] Filters work correctly
- [ ] Dashboard is responsive on mobile
- [ ] Loading state displays properly
- [ ] Error handling works

### Test Commands

```bash
# Start backend
cd backend
npm start

# Start frontend
cd frontend
npm start

# Visit dashboard
# http://localhost:3000/dashboard
```

---

## Security Considerations

### Best Practices

1. **Never expose credentials in frontend code**
2. **Use environment variables for sensitive data**
3. **Implement Row-Level Security in Power BI for multi-tenant apps**
4. **Use HTTPS in production**
5. **Set CORS properly on backend**
6. **Validate embed tokens server-side**

### Example Security Configuration

```javascript
// backend/middleware/auth.js
const verifyToken = (req, res, next) => {
  const token = req.headers.authorization;
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  // Verify JWT token
  jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
    if (err) {
      return res.status(401).json({ error: 'Invalid token' });
    }
    req.user = decoded;
    next();
  });
};

// Protect Power BI route
router.get('/embed-token', verifyToken, async (req, res) => {
  // Generate token only for authenticated users
});
```

---

## Deployment Considerations

### Frontend Deployment (Netlify/Vercel)

```bash
# Build frontend
cd frontend
npm run build

# Deploy to Netlify
netlify deploy --prod
```

### Backend Deployment (Heroku/Railway)

```bash
# Deploy to Heroku
cd backend
git push heroku main
```

### Power BI Service

- Ensure scheduled refresh is configured
- Monitor refresh failures
- Set up alerts for data quality issues

---

## Troubleshooting

### Common Issues

**Issue**: iframe not loading

**Solution**: Check browser console for CORS errors, verify embed URL

**Issue**: "Embed token expired"

**Solution**: Implement token refresh logic using Power BI REST API

**Issue**: Dashboard not responsive

**Solution**: Use Power BI mobile layout feature

---

## Alternative: External Link

If embedding is complex, simply add a link:

```jsx
const BIDashboard = () => {
  return (
    <div className="dashboard-link-container">
      <h2>Business Intelligence Dashboard</h2>
      <p>View our interactive analytics dashboard</p>
      <a 
        href="https://app.powerbi.com/view?r=YOUR_CODE"
        target="_blank"
        rel="noopener noreferrer"
        className="view-dashboard-btn"
      >
        Open Dashboard in New Tab
      </a>
    </div>
  );
};
```

---

## Next Steps

1. Choose integration method based on your Power BI account type
2. Implement the React component
3. Test thoroughly
4. Document for your academic presentation
5. Prepare demo for your defense

**Good luck with your integration! 🚀**
