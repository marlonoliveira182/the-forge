# Deployment Guide for The Forge Web App

This guide provides step-by-step instructions for deploying The Forge Web App to various platforms.

## Quick Start

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**
   ```bash
   streamlit run app.py
   ```

3. **Access the app**
   ```
   http://localhost:8501
   ```

## Deployment Options

### 1. Streamlit Cloud (Recommended)

**Best for**: Quick deployment, free hosting, automatic updates

#### Steps:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy!"

3. **Configuration**
   - **Python version**: 3.11
   - **Main file**: `app.py`
   - **Requirements**: Automatically detected from `requirements.txt`

#### Advantages:
- ✅ Free hosting
- ✅ Automatic deployments
- ✅ Built-in analytics
- ✅ Easy sharing
- ✅ No server management

### 2. Heroku

**Best for**: Custom domains, advanced configuration

#### Steps:

1. **Create Procfile**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Create runtime.txt**
   ```
   python-3.11.18
   ```

3. **Deploy**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### 3. Railway

**Best for**: Simple deployment, good performance

#### Steps:

1. **Connect GitHub repository**
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub account
   - Select your repository

2. **Configure deployment**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

3. **Deploy**
   - Railway will automatically deploy your app

### 4. Render

**Best for**: Reliable hosting, custom domains

#### Steps:

1. **Create render.yaml**
   ```yaml
   services:
     - type: web
       name: the-forge-web-app
       env: python
       plan: free
       buildCommand: pip install -r requirements.txt
       startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
       envVars:
         - key: PYTHON_VERSION
           value: 3.11.18
   ```

2. **Deploy**
   - Connect your GitHub repository
   - Render will automatically deploy

### 5. Vercel

**Best for**: Fast global deployment

#### Steps:

1. **Create vercel.json**
   ```json
   {
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ]
   }
   ```

2. **Deploy**
   - Connect your GitHub repository
   - Vercel will automatically deploy

## Environment Variables

### Required Variables

```bash
# Python version
PYTHON_VERSION=3.11.18

# Streamlit configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Optional Variables

```bash
# Custom configuration
STREAMLIT_THEME_BASE=light
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

## Performance Optimization

### 1. Memory Optimization

```python
# In app.py, add caching
@st.cache_data
def expensive_function():
    # Your expensive computation
    pass
```

### 2. File Size Limits

- **Streamlit Cloud**: 200MB per file
- **Heroku**: 500MB total
- **Railway**: 1GB total
- **Render**: 1GB total

### 3. Processing Time

- **Streamlit Cloud**: 60 seconds timeout
- **Other platforms**: Varies by plan

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Test locally first
python test_app.py
```

#### 2. Memory Issues
- Reduce file sizes
- Use simpler schemas
- Implement caching

#### 3. Timeout Issues
- Optimize processing functions
- Use progress bars
- Break large operations

### Platform-Specific Issues

#### Streamlit Cloud
- **Issue**: Build failures
- **Solution**: Check Python version compatibility

#### Heroku
- **Issue**: H10 errors
- **Solution**: Check Procfile and port configuration

#### Railway
- **Issue**: Build timeouts
- **Solution**: Optimize requirements.txt

## Monitoring

### Built-in Analytics

- **Streamlit Cloud**: Built-in analytics dashboard
- **Other platforms**: Use platform-specific monitoring

### Custom Monitoring

```python
# Add logging to app.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log important events
logger.info("User uploaded file: %s", filename)
```

## Security Considerations

### 1. File Upload Security
- Validate file types
- Check file sizes
- Sanitize file names

### 2. Environment Security
- Use environment variables for secrets
- Don't commit sensitive data
- Use HTTPS in production

### 3. Access Control
- Consider authentication for sensitive operations
- Implement rate limiting
- Monitor usage patterns

## Scaling

### Horizontal Scaling
- **Streamlit Cloud**: Automatic scaling
- **Heroku**: Add dynos
- **Railway**: Upgrade plan
- **Render**: Upgrade plan

### Vertical Scaling
- Increase memory allocation
- Use faster CPU plans
- Optimize code performance

## Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| Streamlit Cloud | ✅ | $10/month | Quick deployment |
| Heroku | ✅ | $7-25/month | Custom domains |
| Railway | ✅ | $5-20/month | Simple deployment |
| Render | ✅ | $7-25/month | Reliable hosting |
| Vercel | ✅ | $20/month | Global performance |

## Support

### Getting Help

1. **Check logs** in your deployment platform
2. **Test locally** with `python test_app.py`
3. **Review documentation** for your platform
4. **Check Streamlit docs** for app-specific issues

### Useful Commands

```bash
# Test the app locally
streamlit run app.py

# Run tests
python test_app.py

# Check dependencies
pip list

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Next Steps

1. **Deploy to Streamlit Cloud** for quick testing
2. **Set up monitoring** for production use
3. **Configure custom domain** if needed
4. **Set up CI/CD** for automatic deployments
5. **Add authentication** for sensitive operations 