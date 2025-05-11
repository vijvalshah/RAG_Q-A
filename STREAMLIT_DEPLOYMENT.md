# Streamlit Cloud Deployment Guide

This guide will help you deploy the RAG Q-A system to Streamlit Cloud.

## Pre-deployment Steps

1. **Push your code to GitHub**:
   Make sure your code is in a GitHub repository.

2. **Set up your API key in Streamlit Secrets**:
   - In the Streamlit Cloud dashboard, go to your app settings
   - Under "Secrets", add your Google Gemini API key:
   ```
   GOOGLE_API_KEY = "your_api_key_here"
   ```

## Deployment Steps

1. **Log in to Streamlit Cloud**: https://share.streamlit.io/

2. **Create a new app**:
   - Click "New app"
   - Connect to your GitHub repository
   - Set the main file path to: `streamlit_cloud.py`
   - Select branch: `main`

3. **Advanced Settings**:
   - Python version: 3.9
   - Packages: Use requirements-streamlit.txt (this is configured automatically)

## Troubleshooting Installation Errors

If you encounter dependency errors during installation:

1. **Specific version errors**:
   - Edit `requirements-streamlit.txt` to use more compatible versions
   - Avoid newer versions that might not be supported by Streamlit Cloud

2. **System dependencies**:
   - The `packages.txt` file should handle system dependencies needed for FAISS

3. **Memory errors**:
   - If you hit memory limits during installation, simplify your requirements
   - Consider removing heavy dependencies if not essential

## Using the Deployed App

The deployed app has two modes:

1. **Full Mode**: Requires a valid Google Gemini API key in Streamlit Secrets
   - Access at: `https://your-app.streamlit.app`

2. **Lightweight Mode**: Works without an API key
   - Access at: `https://your-app.streamlit.app?lightweight=true`

Switch between modes using the links provided in the app interface.

## Advanced Configuration

For more advanced configuration:
- Check the `.streamlit/config.toml` file
- Adjust maximum upload size, theme, and other settings there 