#!/usr/bin/env python3
"""
Build script to convert Flask app to static site for GitHub Pages deployment.
"""

import os
import shutil
from flask_frozen import Freezer
from app import app

# Configure Flask app for static generation
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_DESTINATION'] = 'build'

freezer = Freezer(app)

def clean_build():
    """Remove existing build directory"""
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("Cleaned existing build directory")

def copy_static_files():
    """Copy static files to build directory"""
    if os.path.exists('static'):
        if os.path.exists('build/static'):
            shutil.rmtree('build/static')
        shutil.copytree('static', 'build/static')
        print("Copied static files")

def copy_data_file():
    """Copy the data file to build directory"""
    data_file = 'arc_discovery_projects_2010_2025_with_for.csv'
    if os.path.exists(data_file):
        shutil.copy2(data_file, 'build/')
        print(f"Copied {data_file} to build directory")
    else:
        print(f"Warning: {data_file} not found")

def create_404_page():
    """Create a 404 page for GitHub Pages"""
    html_404 = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Page Not Found</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        h1 { color: #333; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>404 - Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <p><a href="/">Return to Home</a></p>
</body>
</html>"""
    
    with open('build/404.html', 'w') as f:
        f.write(html_404)
    print("Created 404.html")

def main():
    """Main build process"""
    print("Starting static site generation...")
    
    # Clean existing build
    clean_build()
    
    # Generate static site
    try:
        freezer.freeze()
        print("Generated static site successfully")
    except Exception as e:
        print(f"Error generating static site: {e}")
        return
    
    # Copy additional files
    copy_static_files()
    copy_data_file()
    create_404_page()
    
    print("\nBuild completed successfully!")
    print("Static files are in the 'build' directory")
    print("You can now deploy the contents of 'build' to GitHub Pages")

if __name__ == '__main__':
    main()
