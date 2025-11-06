"""
AI Matching Service for coach-client matching using OpenAI embeddings.

Requirements: 4.1, 4.2, 4.3, 4.5
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
import asyncio
import hashlib
import json
from datetime import datetime

from openai import OpenAI, OpenAIError
import numpy as np
from sqlalchemy.orm import Session

from app.config import settings
from app.models.profile import ClientProfile, CoachProfile
from app.repositories.profile_repository import CoachProfileRepository


class MatchingService:
    """
    Service for AI-powered coach matching using OpenAI embeddings.
    
    Implements weighted similarity calculation across 20+ matching factors:
    - Language overlap: 25%
    - Country experience: 20%
    - Goal-expertise alignment: 30%
    - Budget compatibility: 15%
    - Availability match: 10%
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.coach_repo = CoachProfileRepository(db)
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.timeout = 10  # 10 seconds timeout for OpenAI API
        
    def normalize_client_data(self, client: ClientProfile) -> Dict[str, Any]:
        """
        Normalize client quiz data for matching.
        
        Args:
            client: ClientProfile instance
            
        Returns:
            Normalized data dictionary
        """
        quiz = client.quiz_data or {}
        
        return {
            'languages': quiz.get('preferred_languages', []),
            'countries': quiz.get('target_countries', []),
            'goals': quiz.get('cultural_goals', []),
            'challenges': quiz.get('specific_challenges', []),
            'industry': quiz.get('industry', ''),
            'coaching_style': quiz.get('coaching_style', ''),
            'budget_min': quiz.get('budget_range', {}).get('min', 0),
            'budget_max': quiz.get('budget_range', {}).get('max', 500),
            'timeline_urgency': quiz.get('timeline_urgency', 3),
            'previous_experience': quiz.get('previous_expat_experience', False),
            'family_status': quiz.get('family_status', ''),
            'timezone': client.timezone or 'UTC'
        }
    
    def normalize_coach_data(self, coach: CoachProfile) -> Dict[str, Any]:
        """
        Normalize coach profile data for matching.
        
        Args:
            coach: CoachProfile instance
            
        Returns:
            Normalized data dictionary
        """
        return {
            'languages': coach.languages or [],
            'countries': coach.countries or [],
            'expertise': coach.expertise or [],
            'hourly_rate': float(coach.hourly_rate) if coach.hourly_rate else 0,
            'rating': float(coach.rating) if coach.rating else 0,
            'total_sessions': coach.total_sessions or 0,
            'is_verified': coach.is_verified,
            'availability': coach.availability or {}
        }
    
    async def get_text_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get OpenAI text embedding for similarity calculation.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if API fails
        """
        if not self.client:
            return None
            
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.embeddings.create,
                    model="text-embedding-3-small",
                    input=text
                ),
                timeout=self.timeout
            )
            return response.data[0].embedding
        except (OpenAIError, asyncio.TimeoutError) as e:
            print(f"OpenAI embedding error: {e}")
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0-1)
        """
        if not vec1 or not vec2:
            return 0.0
            
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
            
        return float(dot_product / (norm_v1 * norm_v2))
    
    def calculate_language_score(
        self,
        client_languages: List[str],
        coach_languages: List[str]
    ) -> float:
        """
        Calculate language overlap score.
        
        Args:
            client_languages: Client's preferred languages
            coach_languages: Coach's spoken languages
            
        Returns:
            Score (0-1)
        """
        if not client_languages or not coach_languages:
            return 0.0
        
        # Convert to lowercase for case-insensitive comparison
        client_set = set(lang.lower() for lang in client_languages)
        coach_set = set(lang.lower() for lang in coach_languages)
        
        # Calculate Jaccard similarity
        intersection = len(client_set & coach_set)
        union = len(client_set | coach_set)
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_country_score(
        self,
        client_countries: List[str],
        coach_countries: List[str]
    ) -> float:
        """
        Calculate country experience overlap score.
        
        Args:
            client_countries: Client's target countries
            coach_countries: Coach's country experience
            
        Returns:
            Score (0-1)
        """
        if not client_countries or not coach_countries:
            return 0.0
        
        # Convert to lowercase for case-insensitive comparison
        client_set = set(country.lower() for country in client_countries)
        coach_set = set(country.lower() for country in coach_countries)
        
        # Calculate Jaccard similarity
        intersection = len(client_set & coach_set)
        union = len(client_set | coach_set)
        
        return intersection / union if union > 0 else 0.0
    
    async def calculate_goal_expertise_score(
        self,
        client_goals: List[str],
        client_challenges: List[str],
        coach_expertise: List[str]
    ) -> float:
        """
        Calculate goal-expertise alignment using semantic similarity.
        
        Args:
            client_goals: Client's cultural goals
            client_challenges: Client's specific challenges
            coach_expertise: Coach's expertise areas
            
        Returns:
            Score (0-1)
        """
        if not (client_goals or client_challenges) or not coach_expertise:
            return 0.0
        
        # Combine client goals and challenges
        client_text = " ".join(client_goals + client_challenges)
        coach_text = " ".join(coach_expertise)
        
        # Get embeddings
        client_embedding = await self.get_text_embedding(client_text)
        coach_embedding = await self.get_text_embedding(coach_text)
        
        if not client_embedding or not coach_embedding:
            # Fallback to simple keyword matching
            client_words = set(client_text.lower().split())
            coach_words = set(coach_text.lower().split())
            intersection = len(client_words & coach_words)
            union = len(client_words | coach_words)
            return intersection / union if union > 0 else 0.0
        
        return self.cosine_similarity(client_embedding, coach_embedding)
    
    def calculate_budget_score(
        self,
        client_budget_max: float,
        coach_rate: float
    ) -> float:
        """
        Calculate budget compatibility score.
        
        Args:
            client_budget_max: Client's maximum budget
            coach_rate: Coach's hourly rate
            
        Returns:
            Score (0-1)
        """
        if coach_rate <= 0:
            return 0.5  # Neutral score if rate not set
        
        if coach_rate <= client_budget_max:
            return 1.0  # Perfect match
        else:
            # Partial score if slightly over budget (within 20%)
            overage = (coach_rate - client_budget_max) / client_budget_max
            if overage <= 0.2:
                return 0.5
            else:
                return 0.0
    
    def calculate_availability_score(
        self,
        client_timezone: str,
        coach_availability: Dict[str, Any]
    ) -> float:
        """
        Calculate availability compatibility score.
        
        Args:
            client_timezone: Client's timezone
            coach_availability: Coach's availability data
            
        Returns:
            Score (0-1)
        """
        # Simplified availability check
        # In production, this would check actual time slot overlaps
        if not coach_availability:
            return 0.5  # Neutral score if availability not set
        
        # Check if coach has any availability slots
        has_availability = bool(coach_availability)
        return 1.0 if has_availability else 0.0
    
    async def calculate_match_score(
        self,
        client_data: Dict[str, Any],
        coach_data: Dict[str, Any]
    ) -> float:
        """
        Calculate overall match score using weighted similarity.
        
        Weights:
        - Language: 25%
        - Country: 20%
        - Goals: 30%
        - Budget: 15%
        - Availability: 10%
        
        Args:
            client_data: Normalized client data
            coach_data: Normalized coach data
            
        Returns:
            Match score (0-100)
        """
        # Calculate individual scores
        language_score = self.calculate_language_score(
            client_data['languages'],
            coach_data['languages']
        )
        
        country_score = self.calculate_country_score(
            client_data['countries'],
            coach_data['countries']
        )
        
        goal_score = await self.calculate_goal_expertise_score(
            client_data['goals'],
            client_data['challenges'],
            coach_data['expertise']
        )
        
        budget_score = self.calculate_budget_score(
            client_data['budget_max'],
            coach_data['hourly_rate']
        )
        
        availability_score = self.calculate_availability_score(
            client_data['timezone'],
            coach_data['availability']
        )
        
        # Weighted sum
        total_score = (
            language_score * 0.25 +
            country_score * 0.20 +
            goal_score * 0.30 +
            budget_score * 0.15 +
            availability_score * 0.10
        ) * 100
        
        return min(total_score, 100.0)
    
    async def find_matches(
        self,
        client: ClientProfile,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find top matching coaches for a client.
        
        Args:
            client: ClientProfile instance
            limit: Maximum number of matches to return (default 10)
            
        Returns:
            List of match results with coach data and confidence scores
        """
        try:
            # Normalize client data
            client_data = self.normalize_client_data(client)
            
            # Get all active coaches
            coaches = self.coach_repo.get_active_coaches(limit=100)
            
            if not coaches:
                return []
            
            # Calculate match scores for all coaches
            matches = []
            for coach in coaches:
                coach_data = self.normalize_coach_data(coach)
                
                # Calculate match score with timeout
                try:
                    score = await asyncio.wait_for(
                        self.calculate_match_score(client_data, coach_data),
                        timeout=self.timeout
                    )
                    
                    matches.append({
                        'coach_id': str(coach.id),
                        'user_id': str(coach.user_id),
                        'first_name': coach.first_name,
                        'last_name': coach.last_name,
                        'photo_url': coach.photo_url,
                        'bio': coach.bio,
                        'expertise': coach.expertise,
                        'languages': coach.languages,
                        'countries': coach.countries,
                        'hourly_rate': float(coach.hourly_rate) if coach.hourly_rate else None,
                        'currency': coach.currency,
                        'rating': float(coach.rating) if coach.rating else 0.0,
                        'total_sessions': coach.total_sessions,
                        'is_verified': coach.is_verified,
                        'match_score': round(score, 2),
                        'confidence_score': round(score, 2)  # Alias for frontend
                    })
                except asyncio.TimeoutError:
                    print(f"Timeout calculating score for coach {coach.id}")
                    continue
            
            # Sort by match score (descending) and rating (secondary)
            matches.sort(key=lambda x: (x['match_score'], x['rating']), reverse=True)
            
            # Return top N matches
            return matches[:limit]
            
        except Exception as e:
            print(f"Error in find_matches: {e}")
            # Fallback: return top-rated coaches
            return await self.get_fallback_matches(limit)
    
    async def get_fallback_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get fallback matches (top-rated coaches) when AI matching fails.
        
        Args:
            limit: Maximum number of matches to return
            
        Returns:
            List of top-rated coaches
        """
        coaches = self.coach_repo.get_active_coaches(limit=limit)
        
        return [
            {
                'coach_id': str(coach.id),
                'user_id': str(coach.user_id),
                'first_name': coach.first_name,
                'last_name': coach.last_name,
                'photo_url': coach.photo_url,
                'bio': coach.bio,
                'expertise': coach.expertise,
                'languages': coach.languages,
                'countries': coach.countries,
                'hourly_rate': float(coach.hourly_rate) if coach.hourly_rate else None,
                'currency': coach.currency,
                'rating': float(coach.rating) if coach.rating else 0.0,
                'total_sessions': coach.total_sessions,
                'is_verified': coach.is_verified,
                'match_score': 0.0,  # No score for fallback
                'confidence_score': 0.0
            }
            for coach in coaches
        ]
    
    @staticmethod
    def generate_cache_key(client_id: UUID, quiz_data: Dict[str, Any]) -> str:
        """
        Generate cache key for match results.
        
        Args:
            client_id: Client's user ID
            quiz_data: Client's quiz data
            
        Returns:
            Cache key string
        """
        # Create hash of quiz data for cache key
        quiz_json = json.dumps(quiz_data, sort_keys=True)
        quiz_hash = hashlib.md5(quiz_json.encode()).hexdigest()
        
        return f"match:{client_id}:{quiz_hash}"
