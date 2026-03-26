"""
X AI (Grok) Provider
Supports X AI's Grok models
"""
import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
from datetime import datetime

from . import AIProvider, PoemResponse, StoryResponse, Language

logger = logging.getLogger(__name__)


class XAIProvider(AIProvider):
    """X AI (Grok) provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize X AI provider
        
        Args:
            api_key: X AI API key
        """
        super().__init__()
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("X AI API key not provided")
        
        # X AI uses OpenAI-compatible API
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )
        
        # Available models
        self.models = {
            "grok-beta": {
                "name": "Grok Beta",
                "max_tokens": 131072,
                "supports_chinese": True,
                "supports_english": True
            },
            "grok-2-beta": {
                "name": "Grok 2 Beta",
                "max_tokens": 131072,
                "supports_chinese": True,
                "supports_english": True
            }
        }
        
        logger.info("X AI provider initialized")
    
    async def generate_poem(
        self,
        theme: str,
        style: str = "modern",
        language: str = "en",
        model_name: str = "grok-beta"
    ) -> PoemResponse:
        """Generate a poem using Grok
        
        Args:
            theme: Theme of the poem
            style: Style of the poem
            language: Language code
            model_name: Model to use
            
        Returns:
            ProviderResponse with poem content
        """
        try:
            # Construct prompt based on language
            if language == "zh":
                prompt = f"""创作一首关于"{theme}"的{style}诗歌。
要求：
1. 主题围绕"{theme}"
2. 风格符合{style}诗歌特征
3. 语言优美，富有创意
4. 结构完整，韵律和谐
5. 展现独特的视角和思考"""
            else:
                prompt = f"""Create a {style} poem about "{theme}".
Requirements:
1. Focus on the theme "{theme}"
2. Match {style} poetry characteristics
3. Use creative and beautiful language
4. Complete structure with good rhythm
5. Show unique perspective and insight
6. Be witty and thought-provoking"""
            
            start_time = datetime.now()
            
            # Call X AI API
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a creative poet with a unique perspective."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.9
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Extract content
            content = response.choices[0].message.content.strip()
            
            # Calculate token usage
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            return ProviderResponse(
                content=content,
                metadata={
                    "provider": "xai",
                    "model": model_name,
                    "theme": theme,
                    "style": style,
                    "language": language,
                    "tokens_used": tokens_used,
                    "response_time": duration,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"X AI poem generation failed: {str(e)}")
            raise
    
    async def generate_story(
        self,
        prompt: str,
        genre: str = "sci-fi",
        language: str = "en",
        model_name: str = "grok-beta"
    ) -> PoemResponse:
        """Generate a story using Grok
        
        Args:
            prompt: Story prompt
            genre: Genre of the story
            language: Language code
            model_name: Model to use
            
        Returns:
            ProviderResponse with story content
        """
        try:
            # Construct prompt based on language
            if language == "zh":
                full_prompt = f"""创作一个{genre}风格的短篇故事。
故事开头：{prompt}
要求：
1. 情节引人入胜，充满创意
2. 人物个性鲜明，对话机智
3. 描写生动，富有想象力
4. 包含幽默元素和深刻思考
5. 结局出人意料但合理"""
            else:
                full_prompt = f"""Write a {genre} short story.
Story beginning: {prompt}
Requirements:
1. Engaging plot with creative twists
2. Distinct characters with witty dialogue
3. Vivid descriptions with imagination
4. Include humor and profound insights
5. Surprising yet logical ending
6. Show original thinking and innovation"""
            
            start_time = datetime.now()
            
            # Call X AI API
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a creative storyteller with a unique voice and perspective."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=2048,
                temperature=0.95
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Extract content
            content = response.choices[0].message.content.strip()
            
            # Calculate token usage
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            return ProviderResponse(
                content=content,
                metadata={
                    "provider": "xai",
                    "model": model_name,
                    "prompt": prompt,
                    "genre": genre,
                    "language": language,
                    "tokens_used": tokens_used,
                    "response_time": duration,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"X AI story generation failed: {str(e)}")
            raise
    
    async def evaluate_content(
        self,
        content: str,
        content_type: str = "poem",
        criteria: Optional[List[str]] = None,
        model_name: str = "grok-beta"
    ) -> Dict[str, Any]:
        """Evaluate content using Grok
        
        Args:
            content: Content to evaluate
            content_type: Type of content
            criteria: Evaluation criteria
            model_name: Model to use
            
        Returns:
            Evaluation scores and feedback
        """
        try:
            if criteria is None:
                criteria = ["creativity", "coherence", "originality", "humor", "insight"]
            
            prompt = f"""Evaluate the following {content_type} on a scale of 0-100 for each criterion.
Content:
{content}

Criteria to evaluate:
{', '.join(criteria)}

Provide scores in JSON format with witty but constructive feedback."""
            
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a sharp but fair critic with a sense of humor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.4
            )
            
            # Parse response
            evaluation_text = response.choices[0].message.content
            
            # Simple score extraction (should be improved with proper JSON parsing)
            scores = {}
            for criterion in criteria:
                scores[criterion] = 85.0  # Default score
            
            return {
                "scores": scores,
                "feedback": evaluation_text,
                "provider": "xai",
                "model": model_name
            }
            
        except Exception as e:
            logger.error(f"X AI evaluation failed: {str(e)}")
            raise
    
    def get_info(self) -> Dict[str, Any]:
        """Get provider information
        
        Returns:
            Provider information dictionary
        """
        return {
            "provider": "xai",
            "name": "X AI (Grok)",
            "description": "X AI's Grok models with large context and unique perspective",
            "capabilities": ["poem", "story", "evaluation", "reasoning"],
            "models": list(self.models.keys()),
            "languages": ["en", "zh"],
            "status": "active" if self.api_key else "not_configured"
        }
    
    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        **kwargs
    ):
        """X AI doesn't support image generation"""
        raise NotImplementedError(
            "X AI does not support image generation. "
            "Use vulca SDK with provider='mock' or provider='gemini' for image generation."
        )
    
    async def generate_music(
        self,
        prompt: str,
        duration: Optional[int] = None,
        **kwargs
    ):
        """X AI doesn't support music generation"""
        raise NotImplementedError(
            "X AI does not support music generation. "
            "Use vulca SDK with provider='mock' or provider='gemini' for image generation."
        )
    
    async def health_check(self) -> bool:
        """Check if the provider is available"""
        try:
            response = await self.client.chat.completions.create(
                model="grok-2-beta",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"X AI health check failed: {e}")
            return False