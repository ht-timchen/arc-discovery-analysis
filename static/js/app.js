// ARC Discovery Projects Analysis - Frontend JavaScript

class ARCAnalysisApp {
    constructor() {
        this.selectedCodes = [];
        this.selected2DigitCodes = [];
        this.currentCIs = [];
        this.selectedCI = null;
        
        this.initializeElements();
        this.loadForCodes();
        this.bindEvents();
    }

    initializeElements() {
        this.forSelector = document.getElementById('forSelector');
        this.for2DigitSelector = document.getElementById('for2DigitSelector');
        this.ciSelector = document.getElementById('ciSelector');
        this.clearFiltersBtn = document.getElementById('clearFilters');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsTable = document.getElementById('resultsTable');
        this.ciDetailSection = document.getElementById('ciDetailSection');
        this.ciDetailTitle = document.getElementById('ciDetailTitle');
        this.ciDetailContent = document.getElementById('ciDetailContent');
        this.noResults = document.getElementById('noResults');
    }

    bindEvents() {
        // FoR selectors
        this.forSelector.addEventListener('change', () => this.updateView());
        this.for2DigitSelector.addEventListener('change', () => this.updateView());
        
        // Handle click events for selection/deselection
        this.forSelector.addEventListener('click', (e) => {
            if (e.target.tagName === 'OPTION') {
                const option = e.target;
                
                // If Ctrl/Cmd is not held, clear all selections in both dropdowns
                if (!e.ctrlKey && !e.metaKey) {
                    Array.from(this.forSelector.options).forEach(opt => opt.selected = false);
                    Array.from(this.for2DigitSelector.options).forEach(opt => opt.selected = false);
                }
                
                // Toggle the clicked option
                option.selected = !option.selected;
                this.updateView();
            }
        });
        
        this.for2DigitSelector.addEventListener('click', (e) => {
            if (e.target.tagName === 'OPTION') {
                const option = e.target;
                
                // If Ctrl/Cmd is not held, clear all selections in both dropdowns
                if (!e.ctrlKey && !e.metaKey) {
                    Array.from(this.forSelector.options).forEach(opt => opt.selected = false);
                    Array.from(this.for2DigitSelector.options).forEach(opt => opt.selected = false);
                }
                
                // Toggle the clicked option
                option.selected = !option.selected;
                
                // Filter specific codes based on selected broad categories
                this.filterSpecificCodes();
                
                this.updateView();
            }
        });
        
        // CI selector
        this.ciSelector.addEventListener('change', () => this.onCISelection());
        
        // Clear filters
        this.clearFiltersBtn.addEventListener('click', () => this.clearFilters());
    }

    async loadForCodes() {
        try {
            const response = await fetch('/api/for_codes');
            const data = await response.json();
            
            // Store all codes for filtering later
            this.allSpecificCodes = data.specific_codes;
            this.allTwoDigitCodes = data.two_digit_codes;
            
            // Populate specific FoR codes
            this.populateSpecificCodes(this.allSpecificCodes);
            
            // Populate 2-digit FoR codes
            this.for2DigitSelector.innerHTML = '';
            this.allTwoDigitCodes.forEach(code => {
                const option = document.createElement('option');
                option.value = code.value;
                option.textContent = code.label;
                this.for2DigitSelector.appendChild(option);
            });
            
        } catch (error) {
            console.error('Error loading FoR codes:', error);
            this.showError('Failed to load Field of Research codes');
        }
    }

    populateSpecificCodes(codesToShow) {
        this.forSelector.innerHTML = '';
        codesToShow.forEach(code => {
            const option = document.createElement('option');
            option.value = code.value;
            option.textContent = code.label;
            this.forSelector.appendChild(option);
        });
    }

    filterSpecificCodes() {
        const selectedBroadCodes = Array.from(this.for2DigitSelector.selectedOptions).map(opt => opt.value);
        
        if (selectedBroadCodes.length === 0) {
            // If no broad categories selected, show all specific codes
            this.populateSpecificCodes(this.allSpecificCodes);
        } else {
            // Filter specific codes to only show those that start with selected broad codes
            const filteredCodes = this.allSpecificCodes.filter(code => {
                return selectedBroadCodes.some(broadCode => code.value.startsWith(broadCode));
            });
            this.populateSpecificCodes(filteredCodes);
        }
    }

    async updateView() {
        // Get selected values
        this.selectedCodes = Array.from(this.forSelector.selectedOptions).map(opt => opt.value);
        this.selected2DigitCodes = Array.from(this.for2DigitSelector.selectedOptions).map(opt => opt.value);
        
        // Store current scroll positions
        const forSelectorScroll = this.forSelector.scrollTop;
        const for2DigitSelectorScroll = this.for2DigitSelector.scrollTop;
        
        // Show loading
        this.showLoading();
        
        try {
            // Build query parameters
            const params = new URLSearchParams();
            this.selectedCodes.forEach(code => params.append('selected_codes', code));
            this.selected2DigitCodes.forEach(code => params.append('selected_2digit_codes', code));
            
            const response = await fetch(`/api/ranked_cis?${params.toString()}`);
            
            const data = await response.json();
            
            if (response.ok) {
                this.displayResults(data.ranked_cis, data.is_overall);
                
                // Restore scroll positions after a short delay
                setTimeout(() => {
                    this.forSelector.scrollTop = forSelectorScroll;
                    this.for2DigitSelector.scrollTop = for2DigitSelectorScroll;
                }, 10);
            } else {
                this.showError(data.error || 'Failed to load results');
            }
            
        } catch (error) {
            console.error('Error updating view:', error);
            this.showError('Failed to load results');
        }
    }

    displayResults(rankedCIs, isOverall = false) {
        this.hideLoading();
        this.currentCIs = rankedCIs;
        
        if (rankedCIs.length === 0) {
            this.showNoResults();
            return;
        }
        
        // Update CI selector
        this.ciSelector.innerHTML = '';
        rankedCIs.forEach((ci, index) => {
            const option = document.createElement('option');
            option.value = ci.ci_name;
            option.textContent = `${index + 1}. ${ci.ci_name} (${ci.num_projects} projects)`;
            this.ciSelector.appendChild(option);
        });
        
        // Update results table header
        const cardHeader = document.querySelector('#resultsSection .card-header h5');
        if (isOverall) {
            cardHeader.innerHTML = '<i class="fas fa-trophy"></i> Overall Top 30 Chief Investigators (All Fields)';
        } else {
            cardHeader.innerHTML = '<i class="fas fa-trophy"></i> Top 30 Chief Investigators (Filtered)';
        }
        
        // Update results table
        const tbody = this.resultsTable.querySelector('tbody');
        tbody.innerHTML = '';
        
        rankedCIs.forEach((ci, index) => {
            const row = document.createElement('tr');
            row.className = 'fade-in';
            row.innerHTML = `
                <td><strong>${index + 1}</strong></td>
                <td>${ci.ci_name}</td>
                <td><span class="badge bg-primary">${ci.num_projects}</span></td>
            `;
            tbody.appendChild(row);
        });
        
        // Show results
        this.resultsSection.classList.remove('d-none');
        this.ciDetailSection.classList.add('d-none');
        this.noResults.classList.add('d-none');
        
        // Auto-select first CI
        if (rankedCIs.length > 0) {
            this.ciSelector.value = rankedCIs[0].ci_name;
            this.onCISelection();
        }
    }

    async onCISelection() {
        const selectedCI = this.ciSelector.value;
        if (!selectedCI) {
            this.ciDetailSection.classList.add('d-none');
            return;
        }
        
        this.selectedCI = selectedCI;
        this.showLoading();
        
        try {
            // Build query parameters
            const params = new URLSearchParams();
            this.selectedCodes.forEach(code => params.append('selected_codes', code));
            this.selected2DigitCodes.forEach(code => params.append('selected_2digit_codes', code));
            
            const response = await fetch(`/api/ci_detail/${encodeURIComponent(selectedCI)}?${params.toString()}`);
            
            const data = await response.json();
            
            if (response.ok) {
                this.displayCIDetail(data);
            } else {
                this.showError(data.error || 'Failed to load CI details');
            }
            
        } catch (error) {
            console.error('Error loading CI detail:', error);
            this.showError('Failed to load CI details');
        }
    }

    displayCIDetail(data) {
        this.hideLoading();
        
        this.ciDetailTitle.textContent = `Project Details: ${data.ci_name}`;
        
        if (data.projects.length === 0) {
            this.ciDetailContent.innerHTML = '<p class="text-muted">No projects found for this CI with the current filters.</p>';
        } else {
            let html = `<p class="text-muted mb-3">Found ${data.projects.length} project(s):</p>`;
            
            data.projects.forEach((project, index) => {
                html += `
                    <div class="project-item fade-in">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <a href="${project.url}" target="_blank" class="project-code">
                                    ${project.code}
                                </a>
                                <div class="project-meta">
                                    ${project.year} • ${project.org}
                                </div>
                                <div class="project-for">
                                    ${project.for_primary}
                                </div>
                            </div>
                            <span class="badge bg-secondary">${index + 1}</span>
                        </div>
                    </div>
                `;
            });
            
            this.ciDetailContent.innerHTML = html;
        }
        
        this.ciDetailSection.classList.remove('d-none');
    }

    clearFilters() {
        // Clear selections
        this.forSelector.selectedIndex = -1;
        this.for2DigitSelector.selectedIndex = -1;
        this.ciSelector.innerHTML = '<option value="">Select FoR codes first...</option>';
        
        // Reset state
        this.selectedCodes = [];
        this.selected2DigitCodes = [];
        this.currentCIs = [];
        this.selectedCI = null;
        
        // Reset specific codes to show all
        this.populateSpecificCodes(this.allSpecificCodes);
        
        // Show overall ranking
        this.updateView();
    }

    showLoading() {
        this.loadingIndicator.classList.remove('d-none');
        this.resultsSection.classList.add('d-none');
        this.ciDetailSection.classList.add('d-none');
        this.noResults.classList.add('d-none');
    }

    hideLoading() {
        this.loadingIndicator.classList.add('d-none');
    }

    showNoResults() {
        this.hideLoading();
        this.resultsSection.classList.add('d-none');
        this.ciDetailSection.classList.add('d-none');
        this.noResults.classList.remove('d-none');
    }

    showError(message) {
        this.hideLoading();
        this.resultsSection.classList.add('d-none');
        this.ciDetailSection.classList.add('d-none');
        this.noResults.classList.remove('d-none');
        this.noResults.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Error:</strong> ${message}
            </div>
        `;
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ARCAnalysisApp();
});
