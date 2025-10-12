from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from sentiment_analyzer import MultilingualSentimentAnalyzer
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize sentiment analyzer
try:
    sentiment_analyzer = MultilingualSentimentAnalyzer()
    logger.info("Sentiment analyzer initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize sentiment analyzer: {e}")
    sentiment_analyzer = None

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze sentiment of text with confidence scoring"""
    try:
        if not sentiment_analyzer:
            return jsonify({'error': 'Sentiment analyzer not available'}), 500
            
        data = request.json
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        # Analyze the text
        start_time = datetime.now()
        result = sentiment_analyzer.analyze_text(text)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Add processing time to result
        result['processing_time'] = round(processing_time, 3)
        result['timestamp'] = datetime.now().isoformat()
        
        logger.info(f"Analyzed text: {text[:50]}... -> {result.get('sentiment', 'unknown')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'analyzer_ready': sentiment_analyzer is not None,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🌍 Starting Multilingual Sentiment Analyzer...")
    print("📊 Interface will be available at: http://localhost:5000")
    print("⚡ First analysis may take 5-10 seconds (model loading)")
    print("🔥 Press Ctrl+C to stop")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
