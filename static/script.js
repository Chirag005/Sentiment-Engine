class SentimentAnalyzer {
    constructor() {
        this.apiUrl = '/api';
        this.isAnalyzing = false;
        
        // Get DOM elements
        this.textInput = document.getElementById('textInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.languageSelect = document.getElementById('languageSelect');
        
        // Result states
        this.initialState = document.getElementById('initialState');
        this.loadingState = document.getElementById('loadingState');
        this.resultsContent = document.getElementById('resultsContent');
        
        // Result elements
        this.sentimentIcon = document.getElementById('sentimentIcon');
        this.sentimentLabel = document.getElementById('sentimentLabel');
        this.confidenceProgress = document.getElementById('confidenceProgress');
        this.detectedLanguage = document.getElementById('detectedLanguage');
        this.processingTime = document.getElementById('processingTime');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Analyze button
        this.analyzeBtn.addEventListener('click', () => {
            this.analyzeText();
        });
        
        // Clear button
        this.clearBtn.addEventListener('click', () => {
            this.clearAll();
        });
        
        // Keyboard shortcut (Ctrl+Enter)
        this.textInput.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.analyzeText();
            }
        });
        
        // Update button state on text input
        this.textInput.addEventListener('input', () => {
            this.updateAnalyzeButton();
        });
        
        this.updateAnalyzeButton();
    }
    
    updateAnalyzeButton() {
        const hasText = this.textInput.value.trim().length > 0;
        this.analyzeBtn.disabled = !hasText || this.isAnalyzing;
        this.analyzeBtn.textContent = this.isAnalyzing ? 'Analyzing...' : 'Analyze Sentiment';
    }
    
    async analyzeText() {
        const text = this.textInput.value.trim();
        
        if (!text || this.isAnalyzing) return;
        
        this.isAnalyzing = true;
        this.showLoadingState();
        this.updateAnalyzeButton();
        
        try {
            const response = await fetch(`${this.apiUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text })
            });
            
            if (!response.ok) {
                throw new Error('Analysis failed');
            }
            
            const result = await response.json();
            this.displayResults(result);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Failed to analyze text. Please try again.');
        } finally {
            this.isAnalyzing = false;
            this.updateAnalyzeButton();
        }
    }
    
    displayResults(result) {
        // Hide other states
        this.initialState.classList.add('hidden');
        this.loadingState.classList.add('hidden');
        this.resultsContent.classList.remove('hidden');
        
        // Update sentiment display
        const sentiment = result.sentiment;
        this.updateSentimentDisplay(sentiment);
        
        // Update confidence
        const confidence = result.confidence_percentage || (result.confidence * 100);
        this.updateConfidence(confidence);
        
        // Update info
        this.detectedLanguage.textContent = result.language_name || 'Unknown';
        this.processingTime.textContent = `${result.processing_time || 0}s`;
    }
    
    updateSentimentDisplay(sentiment) {
        const sentimentConfig = {
            'positive': { icon: '😊', color: '#10b981' },
            'negative': { icon: '😞', color: '#ef4444' },
            'neutral': { icon: '😐', color: '#f59e0b' }
        };
        
        const config = sentimentConfig[sentiment] || sentimentConfig.neutral;
        
        this.sentimentIcon.textContent = config.icon;
        this.sentimentLabel.textContent = sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
        this.sentimentLabel.className = `sentiment-label ${sentiment}`;
    }
    
    updateConfidence(percentage) {
        // Animate confidence bar
        setTimeout(() => {
            this.confidenceProgress.style.width = `${percentage}%`;
        }, 100);
    }
    
    showLoadingState() {
        this.initialState.classList.add('hidden');
        this.resultsContent.classList.add('hidden');
        this.loadingState.classList.remove('hidden');
    }
    
    showError(message) {
        alert(message);
        this.showInitialState();
    }
    
    showInitialState() {
        this.loadingState.classList.add('hidden');
        this.resultsContent.classList.add('hidden');
        this.initialState.classList.remove('hidden');
    }
    
    clearAll() {
        this.textInput.value = '';
        this.textInput.focus();
        this.languageSelect.value = 'auto';
        this.showInitialState();
        this.updateAnalyzeButton();
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.sentimentAnalyzer = new SentimentAnalyzer();
    document.getElementById('textInput').focus();
    console.log('Sentiment Analyzer initialized! 🌍');
});
