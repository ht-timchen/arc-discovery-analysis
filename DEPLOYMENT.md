# Quick Deployment Guide

## For GitHub Pages (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Enable GitHub Pages**
   - Go to your repository settings
   - Scroll down to "Pages" section
   - Select "Deploy from a branch"
   - Choose "gh-pages" branch
   - Save

3. **The GitHub Action will automatically:**
   - Build the static site
   - Deploy to GitHub Pages
   - Your site will be available at: `https://yourusername.github.io/your-repo-name`

## For Local Testing

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask app**
   ```bash
   python app.py
   ```

3. **Open your browser to** `http://localhost:5000`

## For Other Platforms

### Heroku
1. Create a `Procfile`:
   ```
   web: gunicorn app:app
   ```
2. Add `gunicorn` to requirements.txt
3. Deploy with Heroku CLI

### Netlify
1. Build the static site: `python build.py`
2. Upload the `build` folder contents to Netlify

### Railway
1. Connect your GitHub repo to Railway
2. Railway will auto-detect and deploy

## Troubleshooting

- **Data file missing**: Ensure `arc_discovery_projects_2010_2025_with_for.csv` is in the root directory
- **Build fails**: Check that all dependencies are installed
- **GitHub Pages not working**: Verify the gh-pages branch was created and contains the build files
