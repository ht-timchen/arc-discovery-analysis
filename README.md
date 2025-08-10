# ARC Discovery Projects Analysis

A modern, minimalist web application for analyzing Australian Research Council (ARC) Discovery Projects by Chief Investigators and Field of Research codes. Built as a single-page static website with embedded data for optimal performance.

## ✨ Features

- **Interactive Filtering**: Select specific FoR codes, broad 2-digit categories, or starting years
- **Comprehensive Rankings**: View top Chief Investigators across all FoR categories
- **Year-based Analysis**: Filter projects from specific years onwards
- **Detailed Project View**: Click on any CI to see their specific projects with links to ARC grant pages
- **Modern Minimalist Design**: Clean, professional interface with smooth interactions
- **Single File Deployment**: Complete application in one optimized HTML file
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## 📊 Data Coverage

- **All FoR Codes**: 2,683 specific codes and 52 broad categories
- **Top 2,000 CIs**: Comprehensive ranking of leading researchers
- **15 Projects per CI**: Detailed project information for each investigator
- **Temporal Analysis**: Projects from 2010-2025 with year-based filtering

## 🚀 Live Demo

Visit the live application: [https://ht-timchen.github.io/arc-discovery-analysis/](https://ht-timchen.github.io/arc-discovery-analysis/)

## 🛠️ Local Development

### Prerequisites

- Python 3.8 or higher
- pandas and numpy libraries

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ht-timchen/arc-discovery-analysis.git
cd arc-discovery-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure your data file is in the root directory:
```
arc_discovery_projects_2010_2025_with_for.csv
```

4. Generate the static website:
```bash
python static_analysis_optimized.py
```

5. Open the generated file in your browser:
```bash
open arc_analysis_optimized.html
```

## 📁 Project Structure

```
arc-discovery-analysis/
├── static_analysis_optimized.py    # Main generation script
├── arc_analysis_optimized.html     # Generated static website
├── arc_dp_crawler.py               # Data crawler (optional)
├── arc_discovery_projects_2010_2025_with_for.csv  # Source data
├── requirements.txt                # Python dependencies
├── README.md                      # This file
└── .github/workflows/             # GitHub Actions deployment
    └── deploy.yml
```

## 🎯 Key Features Explained

### **FoR Code Filtering**
- **Broad Categories**: Select 2-digit FoR codes (e.g., "01 Mathematical Sciences")
- **Specific Codes**: Choose detailed 6-digit codes (e.g., "010101 Pure Mathematics")
- **Smart Filtering**: Specific codes automatically filter based on broad category selection

### **Year-based Analysis**
- **Starting Year Filter**: Select projects from any year onwards
- **Temporal Trends**: Analyze research patterns over time
- **Combined Filtering**: Use year filters with FoR codes for precise analysis

### **Interactive Rankings**
- **Real-time Updates**: Rankings update instantly as you change filters
- **Project Counts**: See how many projects each CI has in selected categories
- **Detailed Views**: Click "View Projects" to see individual project details

## 🌐 Deployment

### GitHub Pages (Automatic)

The application is automatically deployed to GitHub Pages via GitHub Actions:

1. Push changes to the `main` branch
2. GitHub Actions builds the static site
3. Deploys to `https://ht-timchen.github.io/arc-discovery-analysis/`

### Manual Deployment

For other static hosting platforms:

1. Generate the static file:
```bash
python static_analysis_optimized.py
```

2. Upload `arc_analysis_optimized.html` to your hosting provider
3. Rename to `index.html` if needed

## 🎨 Design Philosophy

- **Minimalist**: Clean, uncluttered interface focusing on data
- **Modern**: Contemporary typography and spacing
- **Accessible**: High contrast and readable fonts
- **Responsive**: Optimized for all screen sizes
- **Fast**: Single file with embedded data for instant loading

## 🔧 Customization

### Modifying Rankings

Edit `static_analysis_optimized.py` to change:
- Number of top CIs displayed
- Projects per CI shown
- Ranking criteria

### Styling Changes

The CSS is embedded in the HTML file. Modify the `<style>` section in `static_analysis_optimized.py` to customize:
- Colors and typography
- Layout and spacing
- Interactive effects

### Adding Features

Extend the JavaScript in the HTML template to add:
- New filter types
- Additional visualizations
- Export functionality

## 📈 Performance

- **File Size**: ~4.4MB optimized HTML file
- **Load Time**: Instant loading with embedded data
- **No Server**: Completely static, no backend required
- **Caching**: Browser-friendly for optimal performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the generated HTML file
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Tim Chen** - Senior Lecturer at the School of Computer Science, University of Adelaide

- Website: [https://ht-timchen.github.io/](https://ht-timchen.github.io/)
- Research: Human-Computer Interaction, Computer Graphics, and AI/ML

## 🆘 Support

If you encounter any issues or have questions, please open an issue on GitHub.
