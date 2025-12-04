"""Mistral AI client for code review and feedback."""
from mistralai import Mistral
from bot.config import MISTRAL_API_KEY, MISTRAL_MODEL, MISTRAL_MAX_TOKENS, MISTRAL_TEMPERATURE
from bot.ai.prompts import CODE_REVIEW_PROMPT, INTERVIEW_EVALUATION_PROMPT


class MistralAIClient:
    """Client for interacting with Mistral AI API."""
    
    def __init__(self):
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.model = MISTRAL_MODEL
    
    async def review_code(self, code: str, language: str, challenge_description: str) -> str:
        """
        Review submitted code and provide feedback.
        
        Args:
            code: The code to review
            language: Programming language
            challenge_description: Description of the challenge
            
        Returns:
            AI-generated feedback
        """
        try:
            prompt = CODE_REVIEW_PROMPT.format(
                language=language,
                challenge=challenge_description,
                code=code
            )
            
            response = await self.client.chat.complete_async(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=MISTRAL_MAX_TOKENS,
                temperature=MISTRAL_TEMPERATURE
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"❌ Error during code review: {str(e)}"
    
    async def evaluate_interview_answer(self, question: str, user_answer: str) -> str:
        """
        Evaluate user's answer to an interview question.
        
        Args:
            question: The interview question
            user_answer: User's answer
            
        Returns:
            AI-generated evaluation
        """
        try:
            prompt = INTERVIEW_EVALUATION_PROMPT.format(
                question=question,
                answer=user_answer
            )
            
            response = await self.client.chat.complete_async(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=MISTRAL_MAX_TOKENS,
                temperature=MISTRAL_TEMPERATURE
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"❌ Error during evaluation: {str(e)}"
    
    async def generate_hint(self, challenge_description: str, language: str) -> str:
        """
        Generate a hint for a coding challenge.
        
        Args:
            challenge_description: Description of the challenge
            language: Programming language
            
        Returns:
            AI-generated hint
        """
        try:
            prompt = f"""Generate a helpful hint for this coding challenge in {language}:

Challenge: {challenge_description}

Provide a hint that guides the user without giving away the complete solution. Focus on the approach or key concepts."""
            
            response = await self.client.chat.complete_async(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.8
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"❌ Error generating hint: {str(e)}"
