/**
 * Drug Name Autocomplete Functionality
 * Provides autocomplete suggestions for drug name input fields
 */

class DrugAutocomplete {
    constructor(inputElement, options = {}) {
        this.inputElement = inputElement;
        this.options = {
            maxResults: options.maxResults || 10,
            minLength: options.minLength || 1,
            ...options
        };
        this.suggestions = [];
        this.selectedIndex = -1;
        this.suggestionsList = null;
        this.init();
    }

    async init() {
        // Load drug names
        await this.loadDrugNames();
        
        // Create suggestions container
        this.createSuggestionsContainer();
        
        // Add event listeners
        this.addEventListeners();
    }

    async loadDrugNames() {
        try {
            const response = await fetch('/static/data/drug_names.json');
            this.suggestions = await response.json();
        } catch (error) {
            console.error('Failed to load drug names:', error);
            // Fallback to empty array
            this.suggestions = [];
        }
    }

    createSuggestionsContainer() {
        // Create suggestions list container
        this.suggestionsList = document.createElement('ul');
        this.suggestionsList.className = 'drug-autocomplete-suggestions';
        this.suggestionsList.style.cssText = `
            position: absolute;
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 0 0 8px 8px;
            max-height: 200px;
            overflow-y: auto;
            width: 100%;
            z-index: 1000;
            list-style: none;
            margin: 0;
            padding: 0;
            display: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            top: 100%;
            left: 0;
        `;
        
        // Insert after input element in the same container
        this.inputElement.parentNode.appendChild(this.suggestionsList);
    }

    addEventListeners() {
        // Input event for typing
        this.inputElement.addEventListener('input', (e) => {
            this.handleInput(e);
        });
        
        // Keydown for navigation
        this.inputElement.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });
        
        // Blur to hide suggestions
        this.inputElement.addEventListener('blur', () => {
            // Small delay to allow click events on suggestions
            setTimeout(() => {
                this.hideSuggestions();
            }, 150);
        });
        
        // Focus to show suggestions if there's text
        this.inputElement.addEventListener('focus', () => {
            if (this.inputElement.value.trim().length >= this.options.minLength) {
                this.filterSuggestions();
            }
        });
    }

    handleInput(e) {
        const value = e.target.value.trim();
        
        if (value.length >= this.options.minLength) {
            this.filterSuggestions();
        } else {
            this.hideSuggestions();
        }
    }

    handleKeydown(e) {
        if (!this.suggestionsList || this.suggestionsList.style.display === 'none') {
            return;
        }
        
        const items = this.suggestionsList.querySelectorAll('li');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1);
                this.updateSelection(items);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection(items);
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0 && this.selectedIndex < items.length) {
                    this.selectSuggestion(items[this.selectedIndex]);
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }

    filterSuggestions() {
        const value = this.inputElement.value.toLowerCase().trim();
        
        if (!value) {
            this.hideSuggestions();
            return;
        }
        
        // Filter drug names that start with the input value
        const filtered = this.suggestions
            .filter(drug => drug.toLowerCase().startsWith(value))
            .slice(0, this.options.maxResults);
        
        if (filtered.length > 0) {
            this.displaySuggestions(filtered);
        } else {
            this.hideSuggestions();
        }
    }

    displaySuggestions(suggestions) {
        // Clear previous suggestions
        this.suggestionsList.innerHTML = '';
        this.selectedIndex = -1;
        
        // Add new suggestions
        suggestions.forEach((drug, index) => {
            const li = document.createElement('li');
            li.textContent = drug;
            li.style.cssText = `
                padding: 0.5rem 1rem;
                cursor: pointer;
                border-bottom: 1px solid #e5e7eb;
            `;
            
            li.addEventListener('mousedown', (e) => {
                e.preventDefault(); // Prevent blur from happening before selection
                this.selectSuggestion(li);
            });
            
            li.addEventListener('mouseenter', () => {
                this.selectedIndex = index;
                this.updateSelection(this.suggestionsList.querySelectorAll('li'));
            });
            
            this.suggestionsList.appendChild(li);
        });
        
        this.showSuggestions();
    }

    updateSelection(items) {
        // Remove previous selection
        items.forEach(item => {
            item.style.backgroundColor = '';
            item.style.fontWeight = '';
        });
        
        // Highlight selected item
        if (this.selectedIndex >= 0 && this.selectedIndex < items.length) {
            items[this.selectedIndex].style.backgroundColor = '#e5e7eb';
            items[this.selectedIndex].style.fontWeight = '500';
            
            // Scroll to selected item if needed
            const item = items[this.selectedIndex];
            const container = this.suggestionsList;
            
            if (item.offsetTop < container.scrollTop) {
                container.scrollTop = item.offsetTop;
            } else if (item.offsetTop + item.offsetHeight > container.scrollTop + container.offsetHeight) {
                container.scrollTop = item.offsetTop + item.offsetHeight - container.offsetHeight;
            }
        }
    }

    selectSuggestion(li) {
        this.inputElement.value = li.textContent;
        this.inputElement.dispatchEvent(new Event('change'));
        this.hideSuggestions();
        this.inputElement.focus();
    }

    showSuggestions() {
        if (this.suggestionsList) {
            this.suggestionsList.style.display = 'block';
        }
    }

    hideSuggestions() {
        if (this.suggestionsList) {
            this.suggestionsList.style.display = 'none';
            this.selectedIndex = -1;
        }
    }
}

// Initialize autocomplete on specified input elements
function initDrugAutocomplete(selector) {
    const elements = document.querySelectorAll(selector);
    const autocompletes = [];
    
    elements.forEach(element => {
        autocompletes.push(new DrugAutocomplete(element));
    });
    
    return autocompletes;
}

// Auto-initialize on DOMContentLoaded for elements with class 'drug-autocomplete'
document.addEventListener('DOMContentLoaded', () => {
    initDrugAutocomplete('.drug-autocomplete');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DrugAutocomplete, initDrugAutocomplete };
}