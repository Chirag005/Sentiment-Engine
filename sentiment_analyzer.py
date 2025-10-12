from transformers import pipeline
from googletrans import Translator
import re
import logging
from typing import Dict
import random

class MultilingualSentimentAnalyzer:
    """
    Multilingual sentiment analyzer with confidence scoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Try to load XLM-RoBERTa model
        self.model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        
        try:
            print("📥 Loading XLM-RoBERTa model... (this may take a moment)")
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                return_all_scores=True
            )
            print("✅ XLM-RoBERTa model loaded successfully!")
        except Exception as e:
            print(f"⚠️ Could not load XLM-RoBERTa model: {e}")
            print("🔄 Using keyword-based analysis instead...")
            self.sentiment_pipeline = None
            
        # Initialize translator
        try:
            self.translator = Translator()
            print("✅ Google Translator initialized")
        except Exception as e:
            print(f"⚠️ Translator failed: {e}")
            self.translator = None
        
        # Supported languages
        self.supported_languages = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 
            'de': 'German', 'it': 'Italian', 'pt': 'Portuguese',
            'ar': 'Arabic', 'hi': 'Hindi'
        }
        
        # Keyword-based analysis (fallback)
        self.positive_keywords = {
            'en': ['love', 'amazing', 'great', 'excellent', 'fantastic', 'perfect', 'wonderful', 'best', 'awesome', 'brilliant'],
            'es': ['amor', 'increíble', 'excelente', 'fantástico', 'perfecto', 'maravilloso', 'mejor', 'genial', 'brillante'],
            'fr': ['amour', 'incroyable', 'excellent', 'fantastique', 'parfait', 'merveilleux', 'meilleur', 'génial'],
            'de': ['liebe', 'erstaunlich', 'ausgezeichnet', 'fantastisch', 'perfekt', 'wunderbar', 'beste', 'toll']
        }
        
        self.negative_keywords = {
            'en': ['hate', 'terrible', 'awful', 'horrible', 'worst', 'bad', 'disappointing', 'disgusting', 'pathetic'],
            'es': ['odio', 'terrible', 'horrible', 'pésimo', 'malo', 'decepcionante', 'asqueroso', 'patético'],
            'fr': ['déteste', 'terrible', 'horrible', 'pire', 'mauvais', 'décevant', 'dégoûtant', 'pathétique'],
            'de': ['hasse', 'schrecklich', 'furchtbar', 'schlimmste', 'schlecht', 'enttäuschend', 'ekelhaft']
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        if self.translator:
            try:
                detected = self.translator.detect(text)
                if detected and detected.confidence > 0.7:
                    return detected.lang
            except:
                pass
        
        # Simple fallback detection
        text_lower = text.lower()
        if any(word in text_lower for word in ['the', 'and', 'is', 'this', 'that']):
            return 'en'
        elif any(word in text_lower for word in ['el', 'la', 'es', 'este', '¡', '¿']):
            return 'es'
        elif any(word in text_lower for word in ['le', 'la', 'est', 'ce', 'ç']):
            return 'fr'
        elif any(word in text_lower for word in ['der', 'die', 'das', 'ist', 'ü', 'ä', 'ö']):
            return 'de'
        else:
            return 'en'
    
    def analyze_with_transformers(self, text: str) -> Dict:
        """Analyze using XLM-RoBERTa"""
        try:
            results = self.sentiment_pipeline(text)
            
            sentiment_scores = {}
            max_score = 0
            predicted_sentiment = 'neutral'
            
            for result in results[0]:
                label = result['label'].upper()
                score = result['score']
                
                if 'NEGATIVE' in label or label == 'LABEL_0':
                    sentiment_scores['negative'] = score
                    if score > max_score:
                        max_score = score
                        predicted_sentiment = 'negative'
                elif 'POSITIVE' in label or label == 'LABEL_2':
                    sentiment_scores['positive'] = score
                    if score > max_score:
                        max_score = score
                        predicted_sentiment = 'positive'
                elif 'NEUTRAL' in label or label == 'LABEL_1':
                    sentiment_scores['neutral'] = score
                    if score > max_score:
                        max_score = score
                        predicted_sentiment = 'neutral'
            
            return {
                'sentiment': predicted_sentiment,
                'confidence': max_score,
                'scores': sentiment_scores,
                'method': 'transformer'
            }
        except Exception as e:
            return None
    
    def analyze_with_keywords(self, text: str, language: str) -> Dict:
        """Keyword-based fallback analysis"""
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        
        positive_count = 0
        negative_count = 0
        
        if language in self.positive_keywords:
            positive_count = sum(1 for word in self.positive_keywords[language] 
                               if word in clean_text)
            negative_count = sum(1 for word in self.negative_keywords[language] 
                               if word in clean_text)
        
        total_keywords = positive_count + negative_count
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.95, 0.65 + (positive_count * 0.1))
        elif negative_count > positive_count:
            sentiment = 'negative'  
            confidence = min(0.95, 0.65 + (negative_count * 0.1))
        else:
            sentiment = 'neutral'
            confidence = 0.6 + random.uniform(0.05, 0.15)
        
        # Create score distribution
        if sentiment == 'positive':
            scores = {
                'positive': confidence,
                'neutral': (1 - confidence) * 0.7,
                'negative': (1 - confidence) * 0.3
            }
        elif sentiment == 'negative':
            scores = {
                'negative': confidence,
                'neutral': (1 - confidence) * 0.7,
                'positive': (1 - confidence) * 0.3
            }
        else:
            scores = {
                'neutral': confidence,
                'positive': (1 - confidence) * 0.5,
                'negative': (1 - confidence) * 0.5
            }
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': scores,
            'method': 'keyword'
        }
    
    def analyze_text(self, text: str) -> Dict:
        """Main analysis function"""
        if not text or not text.strip():
            return {'error': 'Empty text provided'}
        
        # Clean text
        processed_text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        processed_text = ' '.join(processed_text.split())
        
        # Detect language
        detected_lang = self.detect_language(processed_text)
        
        # Try transformer first, fallback to keywords
        analysis_result = None
        if self.sentiment_pipeline:
            analysis_result = self.analyze_with_transformers(processed_text)
        
        if not analysis_result:
            analysis_result = self.analyze_with_keywords(processed_text, detected_lang)
        
        # Calculate confidence level
        confidence = analysis_result['confidence']
        if confidence >= 0.9:
            confidence_level = 'Very High'
        elif confidence >= 0.8:
            confidence_level = 'High'
        elif confidence >= 0.7:
            confidence_level = 'Medium'
        elif confidence >= 0.6:
            confidence_level = 'Low'
        else:
            confidence_level = 'Very Low'
        
        return {
            'text': text,
            'sentiment': analysis_result['sentiment'],
            'confidence': round(analysis_result['confidence'], 3),
            'confidence_level': confidence_level,
            'confidence_percentage': round(analysis_result['confidence'] * 100, 1),
            'scores': {k: round(v, 3) for k, v in analysis_result['scores'].items()},
            'language': detected_lang,
            'language_name': self.supported_languages.get(detected_lang, 'Unknown'),
            'analysis_method': analysis_result['method']
        }
