"""
NLP Features Module for Text Processing and Analysis
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import spacy
import nltk
from dataclasses import dataclass
from enum import Enum
import re
from collections import Counter
import json

from app.core.logging import agent_logger

logger = logging.getLogger(__name__)

class NLPTask(Enum):
    """Types of NLP tasks"""
    NAMED_ENTITY_RECOGNITION = "ner"
    TEXT_SUMMARIZATION = "summarization"
    SENTIMENT_ANALYSIS = "sentiment"
    KEYWORD_EXTRACTION = "keywords"
    TEXT_CLASSIFICATION = "classification"
    LANGUAGE_DETECTION = "language_detection"

@dataclass
class NamedEntity:
    """Named entity structure"""
    text: str
    label: str
    start: int
    end: int
    confidence: float

@dataclass
class TextSummary:
    """Text summary structure"""
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    key_sentences: List[str]

@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    polarity: float  # -1 to 1
    subjectivity: float  # 0 to 1
    sentiment_label: str
    confidence: float

@dataclass
class KeywordExtraction:
    """Keyword extraction result"""
    keywords: List[Tuple[str, float]]  # (keyword, score)
    key_phrases: List[str]
    named_entities: List[NamedEntity]

class NLPProcessor:
    """Main NLP processing class"""
    
    def __init__(self):
        self.nlp = None
        self.initialized = False
        self._initialize_nlp()
    
    def _initialize_nlp(self):
        """Initialize NLP models and resources"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            # Load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
                # Use a basic model or fallback
                self.nlp = None
            
            self.initialized = True
            logger.info("NLP Processor initialized")
            
        except Exception as e:
            logger.error(f"Error initializing NLP processor: {e}")
            self.initialized = False
    
    async def process_text(self, text: str, tasks: List[NLPTask]) -> Dict[str, Any]:
        """Process text with specified NLP tasks"""
        if not self.initialized:
            raise RuntimeError("NLP processor not initialized")
        
        results = {}
        
        for task in tasks:
            try:
                if task == NLPTask.NAMED_ENTITY_RECOGNITION:
                    results["ner"] = await self.extract_named_entities(text)
                elif task == NLPTask.TEXT_SUMMARIZATION:
                    results["summary"] = await self.summarize_text(text)
                elif task == NLPTask.SENTIMENT_ANALYSIS:
                    results["sentiment"] = await self.analyze_sentiment(text)
                elif task == NLPTask.KEYWORD_EXTRACTION:
                    results["keywords"] = await self.extract_keywords(text)
                elif task == NLPTask.TEXT_CLASSIFICATION:
                    results["classification"] = await self.classify_text(text)
                elif task == NLPTask.LANGUAGE_DETECTION:
                    results["language"] = await self.detect_language(text)
                    
            except Exception as e:
                logger.error(f"Error processing task {task.value}: {e}")
                results[task.value] = {"error": str(e)}
        
        return results
    
    async def extract_named_entities(self, text: str) -> List[NamedEntity]:
        """Extract named entities from text"""
        if not self.nlp:
            return await self._fallback_ner(text)
        
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                entities.append(NamedEntity(
                    text=ent.text,
                    label=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.8  # spaCy doesn't provide confidence scores
                ))
            
            # Log extraction
            agent_logger.log_agent_decision(
                "nlp_processor",
                f"Named entity extraction completed",
                f"Found {len(entities)} entities in {len(text)} characters"
            )
            
            return entities
            
        except Exception as e:
            logger.error(f"Error in named entity extraction: {e}")
            return await self._fallback_ner(text)
    
    async def _fallback_ner(self, text: str) -> List[NamedEntity]:
        """Fallback NER using regex patterns"""
        entities = []
        
        # Common patterns for renewable energy entities
        patterns = {
            "LOCATION": r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized words
            "ORGANIZATION": r'\b[A-Z][a-z]+\s+(?:Inc|Corp|LLC|Ltd|Company|Energy|Solar|Wind)\b',
            "MONEY": r'\$[\d,]+(?:\.\d{2})?',
            "PERCENT": r'\d+(?:\.\d+)?%',
            "DATE": r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            "MEASUREMENT": r'\d+(?:\.\d+)?\s*(?:MW|GW|kWh|MWh|GWh|m/s|km/h|km²|acres|hectares)\b'
        }
        
        for label, pattern in patterns.items():
            for match in re.finditer(pattern, text):
                entities.append(NamedEntity(
                    text=match.group(),
                    label=label,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.6
                ))
        
        return entities
    
    async def summarize_text(self, text: str, max_sentences: int = 5) -> TextSummary:
        """Summarize text using extractive summarization"""
        try:
            if not self.nlp:
                return await self._fallback_summarization(text, max_sentences)
            
            doc = self.nlp(text)
            sentences = [sent.text for sent in doc.sents]
            
            if len(sentences) <= max_sentences:
                return TextSummary(
                    summary=text,
                    original_length=len(text),
                    summary_length=len(text),
                    compression_ratio=1.0,
                    key_sentences=sentences
                )
            
            # Score sentences based on word frequency and position
            word_freq = Counter()
            for token in doc:
                if not token.is_stop and not token.is_punct and token.is_alpha:
                    word_freq[token.text.lower()] += 1
            
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                score = 0
                sentence_tokens = self.nlp(sentence)
                
                for token in sentence_tokens:
                    if not token.is_stop and not token.is_punct and token.is_alpha:
                        score += word_freq[token.text.lower()]
                
                # Boost score for sentences at the beginning
                if i < len(sentences) * 0.3:
                    score *= 1.2
                
                sentence_scores.append((score, i, sentence))
            
            # Select top sentences
            sentence_scores.sort(reverse=True)
            selected_sentences = sentence_scores[:max_sentences]
            selected_sentences.sort(key=lambda x: x[1])  # Sort by original order
            
            key_sentences = [sent[2] for sent in selected_sentences]
            summary = " ".join(key_sentences)
            
            return TextSummary(
                summary=summary,
                original_length=len(text),
                summary_length=len(summary),
                compression_ratio=len(summary) / len(text),
                key_sentences=key_sentences
            )
            
        except Exception as e:
            logger.error(f"Error in text summarization: {e}")
            return await self._fallback_summarization(text, max_sentences)
    
    async def _fallback_summarization(self, text: str, max_sentences: int) -> TextSummary:
        """Fallback summarization using simple sentence splitting"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return TextSummary(
                summary=text,
                original_length=len(text),
                summary_length=len(text),
                compression_ratio=1.0,
                key_sentences=sentences
            )
        
        # Simple selection of first and last sentences
        selected_sentences = sentences[:max_sentences//2] + sentences[-(max_sentences//2):]
        summary = ". ".join(selected_sentences) + "."
        
        return TextSummary(
            summary=summary,
            original_length=len(text),
            summary_length=len(summary),
            compression_ratio=len(summary) / len(text),
            key_sentences=selected_sentences
        )
    
    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment of text"""
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            
            sia = SentimentIntensityAnalyzer()
            scores = sia.polarity_scores(text)
            
            polarity = scores['compound']
            subjectivity = scores['neu']  # Use neutrality as proxy for subjectivity
            
            # Determine sentiment label
            if polarity >= 0.05:
                sentiment_label = "positive"
            elif polarity <= -0.05:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            confidence = abs(polarity)
            
            return SentimentResult(
                polarity=polarity,
                subjectivity=subjectivity,
                sentiment_label=sentiment_label,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return SentimentResult(
                polarity=0.0,
                subjectivity=0.5,
                sentiment_label="neutral",
                confidence=0.0
            )
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> KeywordExtraction:
        """Extract keywords and key phrases from text"""
        try:
            if not self.nlp:
                return await self._fallback_keyword_extraction(text, max_keywords)
            
            doc = self.nlp(text)
            
            # Extract keywords using TF-IDF-like scoring
            word_freq = Counter()
            word_pos = Counter()
            
            for token in doc:
                if not token.is_stop and not token.is_punct and token.is_alpha and len(token.text) > 2:
                    word_freq[token.text.lower()] += 1
                    word_pos[token.text.lower()] = token.pos_
            
            # Score keywords
            keywords = []
            for word, freq in word_freq.items():
                score = freq
                # Boost score for important POS tags
                if word_pos[word] in ['NOUN', 'PROPN']:
                    score *= 1.5
                elif word_pos[word] in ['ADJ']:
                    score *= 1.2
                
                keywords.append((word, score))
            
            # Sort by score and take top keywords
            keywords.sort(key=lambda x: x[1], reverse=True)
            top_keywords = keywords[:max_keywords]
            
            # Extract key phrases (noun phrases)
            key_phrases = []
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:  # Limit phrase length
                    key_phrases.append(chunk.text)
            
            # Extract named entities
            named_entities = await self.extract_named_entities(text)
            
            return KeywordExtraction(
                keywords=top_keywords,
                key_phrases=key_phrases[:max_keywords//2],
                named_entities=named_entities
            )
            
        except Exception as e:
            logger.error(f"Error in keyword extraction: {e}")
            return await self._fallback_keyword_extraction(text, max_keywords)
    
    async def _fallback_keyword_extraction(self, text: str, max_keywords: int) -> KeywordExtraction:
        """Fallback keyword extraction using simple frequency counting"""
        # Simple word frequency analysis
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = Counter(words)
        
        # Remove common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'}
        
        filtered_words = {word: freq for word, freq in word_freq.items() if word not in stop_words}
        keywords = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
        
        return KeywordExtraction(
            keywords=keywords,
            key_phrases=[],
            named_entities=[]
        )
    
    async def classify_text(self, text: str) -> Dict[str, Any]:
        """Classify text into categories (simplified implementation)"""
        try:
            # Simple rule-based classification for renewable energy content
            categories = {
                "solar_energy": 0,
                "wind_energy": 0,
                "hydro_energy": 0,
                "geothermal_energy": 0,
                "project_finance": 0,
                "environmental_impact": 0,
                "technical_specifications": 0,
                "regulatory_compliance": 0
            }
            
            text_lower = text.lower()
            
            # Solar energy keywords
            solar_keywords = ['solar', 'photovoltaic', 'pv', 'panel', 'irradiance', 'sunlight']
            categories["solar_energy"] = sum(1 for keyword in solar_keywords if keyword in text_lower)
            
            # Wind energy keywords
            wind_keywords = ['wind', 'turbine', 'windfarm', 'wind farm', 'windmill', 'wind speed']
            categories["wind_energy"] = sum(1 for keyword in wind_keywords if keyword in text_lower)
            
            # Hydro energy keywords
            hydro_keywords = ['hydro', 'hydropower', 'dam', 'water', 'river', 'reservoir']
            categories["hydro_energy"] = sum(1 for keyword in hydro_keywords if keyword in text_lower)
            
            # Geothermal energy keywords
            geo_keywords = ['geothermal', 'geothermal energy', 'heat pump', 'ground source']
            categories["geothermal_energy"] = sum(1 for keyword in geo_keywords if keyword in text_lower)
            
            # Project finance keywords
            finance_keywords = ['cost', 'price', 'investment', 'roi', 'npv', 'irr', 'financing', 'budget']
            categories["project_finance"] = sum(1 for keyword in finance_keywords if keyword in text_lower)
            
            # Environmental impact keywords
            env_keywords = ['environmental', 'impact', 'carbon', 'emission', 'sustainability', 'green']
            categories["environmental_impact"] = sum(1 for keyword in env_keywords if keyword in text_lower)
            
            # Technical specifications keywords
            tech_keywords = ['specification', 'technical', 'capacity', 'efficiency', 'performance', 'design']
            categories["technical_specifications"] = sum(1 for keyword in tech_keywords if keyword in text_lower)
            
            # Regulatory compliance keywords
            reg_keywords = ['regulation', 'permit', 'compliance', 'legal', 'policy', 'standard']
            categories["regulatory_compliance"] = sum(1 for keyword in reg_keywords if keyword in text_lower)
            
            # Find primary category
            primary_category = max(categories.items(), key=lambda x: x[1])
            
            return {
                "primary_category": primary_category[0],
                "confidence": primary_category[1] / len(text.split()) if text.split() else 0,
                "all_categories": categories,
                "classification_method": "rule_based"
            }
            
        except Exception as e:
            logger.error(f"Error in text classification: {e}")
            return {
                "primary_category": "unknown",
                "confidence": 0.0,
                "all_categories": {},
                "classification_method": "error"
            }
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text (simplified implementation)"""
        try:
            # Simple language detection based on common words
            languages = {
                "english": ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had'],
                "spanish": ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se'],
                "french": ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
                "german": ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich']
            }
            
            text_lower = text.lower()
            scores = {}
            
            for lang, words in languages.items():
                score = sum(1 for word in words if word in text_lower)
                scores[lang] = score
            
            detected_language = max(scores.items(), key=lambda x: x[1])
            
            return {
                "language": detected_language[0],
                "confidence": detected_language[1] / len(text.split()) if text.split() else 0,
                "all_scores": scores,
                "detection_method": "word_frequency"
            }
            
        except Exception as e:
            logger.error(f"Error in language detection: {e}")
            return {
                "language": "unknown",
                "confidence": 0.0,
                "all_scores": {},
                "detection_method": "error"
            }
    
    async def process_renewable_energy_document(self, text: str) -> Dict[str, Any]:
        """Process renewable energy document with comprehensive NLP analysis"""
        tasks = [
            NLPTask.NAMED_ENTITY_RECOGNITION,
            NLPTask.TEXT_SUMMARIZATION,
            NLPTask.SENTIMENT_ANALYSIS,
            NLPTask.KEYWORD_EXTRACTION,
            NLPTask.TEXT_CLASSIFICATION
        ]
        
        results = await self.process_text(text, tasks)
        
        # Add renewable energy specific analysis
        results["renewable_energy_analysis"] = await self._analyze_renewable_energy_content(text)
        
        return results
    
    async def _analyze_renewable_energy_content(self, text: str) -> Dict[str, Any]:
        """Analyze renewable energy specific content"""
        try:
            analysis = {
                "energy_types_mentioned": [],
                "technical_metrics": [],
                "financial_metrics": [],
                "geographical_references": [],
                "temporal_references": []
            }
            
            text_lower = text.lower()
            
            # Energy types
            energy_types = {
                "solar": ["solar", "photovoltaic", "pv", "sunlight", "irradiance"],
                "wind": ["wind", "turbine", "windfarm", "wind farm"],
                "hydro": ["hydro", "hydropower", "dam", "water power"],
                "geothermal": ["geothermal", "geothermal energy"],
                "biomass": ["biomass", "bioenergy", "biofuel"]
            }
            
            for energy_type, keywords in energy_types.items():
                if any(keyword in text_lower for keyword in keywords):
                    analysis["energy_types_mentioned"].append(energy_type)
            
            # Technical metrics
            tech_patterns = [
                r'(\d+(?:\.\d+)?)\s*(?:MW|GW|kW)',
                r'(\d+(?:\.\d+)?)\s*(?:kWh|MWh|GWh)',
                r'(\d+(?:\.\d+)?)\s*(?:m/s|km/h)',
                r'(\d+(?:\.\d+)?)\s*(?:km²|acres|hectares)',
                r'(\d+(?:\.\d+)?)\s*(?:%|percent)'
            ]
            
            for pattern in tech_patterns:
                matches = re.findall(pattern, text)
                analysis["technical_metrics"].extend(matches)
            
            # Financial metrics
            finance_patterns = [
                r'\$[\d,]+(?:\.\d{2})?',
                r'(\d+(?:\.\d+)?)\s*(?:million|billion)',
                r'(?:ROI|NPV|IRR|LCOE)',
                r'(?:cost|price|investment|budget)'
            ]
            
            for pattern in finance_patterns:
                matches = re.findall(pattern, text)
                analysis["financial_metrics"].extend(matches)
            
            # Geographical references (simplified)
            geo_patterns = [
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:State|County|Province|Region)\b',
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'  # Capitalized words (likely locations)
            ]
            
            for pattern in geo_patterns:
                matches = re.findall(pattern, text)
                analysis["geographical_references"].extend(matches[:5])  # Limit to 5
            
            # Temporal references
            temporal_patterns = [
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                r'\b\d{4}\b',
                r'\b(?:Q1|Q2|Q3|Q4)\s+\d{4}\b'
            ]
            
            for pattern in temporal_patterns:
                matches = re.findall(pattern, text)
                analysis["temporal_references"].extend(matches)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in renewable energy content analysis: {e}")
            return {"error": str(e)}

# Global NLP processor instance
nlp_processor = NLPProcessor()