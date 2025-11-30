# Deployment Guide

## Deploy to Streamlit Cloud

### Step 1: Push to GitHub

1. Make sure all changes are committed:

```bash
git add .
git commit -m "Modern UI and deployment ready"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `research-paper-chat`
5. Branch: `main`
6. Main file path: `app.py`
7. Click "Deploy"

### Step 3: Configure Secrets

In your app settings on Streamlit Cloud:

1. Go to "Settings" > "Secrets"
2. Add the following:

```toml
GOOGLE_API_KEY = "your-actual-api-key-here"
APP_MODE = "live"
```

3. Save and the app will restart automatically

### Step 4: Test Your Deployment

1. Wait for deployment to complete (2-5 minutes)
2. Visit your app URL: `https://your-app-name.streamlit.app`
3. Upload a PDF and test all features

## Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your API key

# Run the app
streamlit run app.py
```

## Environment Variables

- `GOOGLE_API_KEY`: Your Google AI Studio API key (required)
- `APP_MODE`: Set to "live" (default)

## Troubleshooting

### App won't start

- Check that all dependencies are in `requirements.txt`
- Verify `app.py` is in the root directory
- Check Streamlit Cloud logs for errors

### API errors

- Verify your API key is correct in Secrets
- Check you haven't exceeded rate limits
- Ensure the key has proper permissions

### PDF upload issues

- Streamlit Cloud has file size limits
- Large PDFs may take longer to process
- Try with smaller PDFs first

## Monitoring

- Check usage at: https://ai.dev/usage
- Monitor app health in Streamlit Cloud dashboard
- View logs in Streamlit Cloud for debugging

## Support

For issues:

1. Check Streamlit Cloud logs
2. Verify API key is working
3. Test locally first
4. Check GitHub issues

---

**Your app is ready to deploy!**
