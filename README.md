# ARC Discovery Projects Analysis

A web application for analyzing Australian Research Council (ARC) Discovery Projects by Chief Investigators and Field of Research codes.

## Features

- **Interactive Filtering**: Select specific FoR codes or broad 2-digit categories
- **Top 30 Ranking**: View the top 30 Chief Investigators by number of projects
- **Detailed Project View**: Click on any CI to see their specific projects with links to ARC grant pages
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Updates**: Results update instantly as you change filters

## Data Source

The application uses the `arc_discovery_projects_2010_2025_with_for.csv` file containing ARC Discovery Projects data from 2010-2025 with Field of Research classifications.

## Local Development

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd arc-crawl
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure your data file is in the root directory:
```
arc_discovery_projects_2010_2025_with_for.csv
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Deployment Options

### Option 1: GitHub Pages (Static Site)

Since this is a Flask application, you'll need to convert it to a static site for GitHub Pages. Here are a few approaches:

#### Using Flask-Freeze (Recommended)

1. Install Flask-Freeze:
```bash
pip install Flask-Freeze
```

2. Create a build script (`build.py`):
```python
from flask_frozen import Freezer
from app import app

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()
```

3. Build the static site:
```bash
python build.py
```

4. The static files will be in the `build` directory. Copy them to your repository root.

5. Enable GitHub Pages in your repository settings and point to the root directory.

#### Using Netlify

1. Deploy to Netlify using the Flask-Freeze method above
2. Upload the `build` directory contents to Netlify
3. Configure your domain

### Option 2: Heroku

1. Create a `Procfile`:
```
web: gunicorn app:app
```

2. Add gunicorn to requirements.txt:
```
gunicorn==21.2.0
```

3. Deploy to Heroku:
```bash
heroku create your-app-name
git push heroku main
```

### Option 3: Python Anywhere

1. Upload your files to PythonAnywhere
2. Create a new web app
3. Point to your `app.py` file
4. Configure the WSGI file

### Option 4: Railway

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Flask app
3. Deploy with one click

## File Structure

```
arc-crawl/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── arc_discovery_projects_2010_2025_with_for.csv  # Data file
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        └── app.js        # Frontend JavaScript
```

## API Endpoints

- `GET /` - Main page
- `GET /api/for_codes` - Get available FoR codes
- `POST /api/ranked_cis` - Get ranked CIs based on selected filters
- `POST /api/ci_detail/<ci_name>` - Get detailed project information for a CI

## Customization

### Changing the Data Source

Update the `INPUT_CSV` variable in `app.py` to point to your data file.

### Modifying the Top K Results

Change the `TOP_K` variable in `app.py` to show more or fewer results.

### Styling

Modify `static/css/style.css` to customize the appearance.

### Adding Features

The modular structure makes it easy to add new features:
- Add new API endpoints in `app.py`
- Extend the frontend in `static/js/app.js`
- Update the UI in `templates/index.html`

## Troubleshooting

### Data Loading Issues

- Ensure the CSV file exists and is readable
- Check that the CSV has the expected column names
- Verify the file encoding (should be UTF-8)

### Performance Issues

- The application loads all data into memory on startup
- For very large datasets, consider implementing pagination
- Add caching for frequently accessed data

### Deployment Issues

- Make sure all dependencies are in `requirements.txt`
- Check that the data file is included in your deployment
- Verify that your hosting platform supports Python/Flask

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
