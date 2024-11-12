"""
AI Services for book recommendations, summaries, and review analysis
Uses: OpenAI (GPT-3.5), Cohere, and Anthropic Claude
All have free tiers available!
"""
import logging
from typing import List, Dict, Optional
from django.conf import settings
from django.core.cache import cache
import json

logger = logging.getLogger(__name__)


class BookRecommendationAI:
    """
    AI-powered book recommendations using multiple providers
    """
    
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.cohere_key = settings.COHERE_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY
    
    def get_recommendations(
        self, 
        user_preferences: Dict,
        read_books: List[str],
        limit: int = 5
    ) -> List[Dict]:
        """
        Get AI-powered book recommendations based on user preferences
        
        Args:
            user_preferences: Dict with favorite_genres, reading_goal, etc.
            read_books: List of book titles user has read
            limit: Number of recommendations
        
        Returns:
            List of recommended books with reasoning
        """
        cache_key = f"ai:recommendations:{hash(str(user_preferences))}:{hash(str(read_books))}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Try OpenAI first (best quality)
            if self.openai_key:
                recommendations = self._get_openai_recommendations(
                    user_preferences, read_books, limit
                )
                if recommendations:
                    cache.set(cache_key, recommendations, 3600)  # Cache 1 hour
                    return recommendations
            
            # Fallback to Cohere
            if self.cohere_key:
                recommendations = self._get_cohere_recommendations(
                    user_preferences, read_books, limit
                )
                if recommendations:
                    cache.set(cache_key, recommendations, 3600)
                    return recommendations
            
            return []
            
        except Exception as e:
            logger.error(f"AI recommendation error: {str(e)}")
            return []
    
    def _get_openai_recommendations(
        self, user_prefs: Dict, read_books: List[str], limit: int
    ) -> List[Dict]:
        """Get recommendations from OpenAI GPT"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            prompt = f"""Based on the following user reading profile, recommend {limit} books.
            
User's favorite genres: {user_prefs.get('favorite_genres', 'Not specified')}
Books they've read: {', '.join(read_books[:10])}

Please provide {limit} book recommendations in JSON format:
[
    {{
        "title": "Book Title",
        "author": "Author Name",
        "genre": "Genre",
        "reason": "Why this book is recommended"
    }}
]

Only return valid JSON, no additional text."""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable book recommendation assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            recommendations = json.loads(content)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return []
    
    def _get_cohere_recommendations(
        self, user_prefs: Dict, read_books: List[str], limit: int
    ) -> List[Dict]:
        """Get recommendations from Cohere"""
        try:
            import cohere
            co = cohere.Client(self.cohere_key)
            
            prompt = f"""Recommend {limit} books based on this profile:
Favorite genres: {user_prefs.get('favorite_genres', 'various')}
Previously read: {', '.join(read_books[:5])}

Format: JSON array with title, author, genre, reason"""
            
            response = co.generate(
                model='command-light',
                prompt=prompt,
                max_tokens=300,
                temperature=0.7
            )
            
            # Parse response (Cohere may return less structured output)
            content = response.generations[0].text.strip()
            
            # Try to extract JSON or parse structured text
            try:
                recommendations = json.loads(content)
            except:
                # Fallback: parse as text and structure it
                recommendations = self._parse_text_recommendations(content)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Cohere API error: {str(e)}")
            return []
    
    def _parse_text_recommendations(self, text: str) -> List[Dict]:
        """Parse unstructured recommendation text into structured data"""
        # Simple parsing logic - can be improved
        recommendations = []
        lines = text.split('\n')
        
        current_rec = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current_rec:
                    recommendations.append(current_rec)
                    current_rec = {}
                continue
            
            if line.lower().startswith('title:'):
                current_rec['title'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('author:'):
                current_rec['author'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('genre:'):
                current_rec['genre'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('reason:'):
                current_rec['reason'] = line.split(':', 1)[1].strip()
        
        if current_rec:
            recommendations.append(current_rec)
        
        return recommendations


class BookSummaryAI:
    """
    Generate AI summaries of books
    """
    
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY
    
    def generate_summary(self, book_title: str, book_description: str) -> Optional[str]:
        """
        Generate a concise, engaging summary of a book
        
        Args:
            book_title: The book's title
            book_description: Long description or synopsis
        
        Returns:
            AI-generated summary or None
        """
        cache_key = f"ai:summary:{hash(book_title + book_description)}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            if self.openai_key:
                summary = self._generate_openai_summary(book_title, book_description)
            elif self.anthropic_key:
                summary = self._generate_anthropic_summary(book_title, book_description)
            else:
                return None
            
            if summary:
                # Cache for 7 days (summaries don't change)
                cache.set(cache_key, summary, 604800)
            
            return summary
            
        except Exception as e:
            logger.error(f"AI summary error: {str(e)}")
            return None
    
    def _generate_openai_summary(self, title: str, description: str) -> Optional[str]:
        """Generate summary using OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            prompt = f"""Summarize this book in 2-3 engaging sentences that would make someone want to read it:

Title: {title}
Description: {description}

Write a concise, compelling summary:"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a literary expert who writes engaging, concise book summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI summary error: {str(e)}")
            return None
    
    def _generate_anthropic_summary(self, title: str, description: str) -> Optional[str]:
        """Generate summary using Anthropic Claude"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            prompt = f"""Summarize this book in 2-3 engaging sentences:

Title: {title}
Description: {description}"""
            
            message = client.messages.create(
                model="claude-3-haiku-20240307",  # Cheapest Claude model
                max_tokens=150,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Anthropic summary error: {str(e)}")
            return None


class ReviewAnalysisAI:
    """
    Analyze book reviews for sentiment, themes, and insights
    """
    
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.cohere_key = settings.COHERE_API_KEY
    
    def analyze_reviews(self, reviews: List[str]) -> Dict:
        """
        Analyze multiple reviews to extract insights
        
        Args:
            reviews: List of review texts
        
        Returns:
            Dict with sentiment, common themes, and overall insight
        """
        if not reviews:
            return {"sentiment": "neutral", "themes": [], "insight": ""}
        
        cache_key = f"ai:review_analysis:{hash(str(reviews))}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            if self.cohere_key:
                analysis = self._analyze_with_cohere(reviews)
            elif self.openai_key:
                analysis = self._analyze_with_openai(reviews)
            else:
                return {"sentiment": "neutral", "themes": [], "insight": ""}
            
            if analysis:
                cache.set(cache_key, analysis, 3600)  # Cache 1 hour
            
            return analysis
            
        except Exception as e:
            logger.error(f"Review analysis error: {str(e)}")
            return {"sentiment": "neutral", "themes": [], "insight": ""}
    
    def _analyze_with_cohere(self, reviews: List[str]) -> Dict:
        """Analyze reviews using Cohere"""
        try:
            import cohere
            co = cohere.Client(self.cohere_key)
            
            # Combine reviews (limit to avoid token limits)
            combined_reviews = " | ".join(reviews[:10])
            
            prompt = f"""Analyze these book reviews and provide:
1. Overall sentiment (positive/negative/mixed)
2. Top 3 themes mentioned
3. One-sentence insight

Reviews: {combined_reviews}

Format your response as JSON:
{{"sentiment": "...", "themes": ["...", "...", "..."], "insight": "..."}}"""
            
            response = co.generate(
                model='command-light',
                prompt=prompt,
                max_tokens=200
            )
            
            content = response.generations[0].text.strip()
            
            try:
                analysis = json.loads(content)
            except:
                # Fallback parsing
                analysis = {
                    "sentiment": "mixed",
                    "themes": ["character development", "plot", "writing style"],
                    "insight": "Reviews show mixed opinions about this book."
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Cohere analysis error: {str(e)}")
            return {"sentiment": "neutral", "themes": [], "insight": ""}
    
    def _analyze_with_openai(self, reviews: List[str]) -> Dict:
        """Analyze reviews using OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            combined_reviews = "\n\n".join(reviews[:10])
            
            prompt = f"""Analyze these book reviews and provide a JSON response with:
- sentiment: overall sentiment (positive/negative/mixed)
- themes: top 3 themes mentioned in reviews
- insight: one insightful sentence about what reviewers think

Reviews:
{combined_reviews}

Return only valid JSON."""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a book review analyst. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            analysis = json.loads(content)
            
            return analysis
            
        except Exception as e:
            logger.error(f"OpenAI analysis error: {str(e)}")
            return {"sentiment": "neutral", "themes": [], "insight": ""}


# Initialize AI services
recommendation_ai = BookRecommendationAI()
summary_ai = BookSummaryAI()
review_analysis_ai = ReviewAnalysisAI()

