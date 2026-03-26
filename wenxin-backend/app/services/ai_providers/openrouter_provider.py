"""
OpenRouter AI Provider
Provides unified access to multiple AI models including Kimi
"""
import os
import asyncio
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from datetime import datetime

from . import AIProvider, PoemResponse, StoryResponse, ImageResponse, MusicResponse, Language

logger = logging.getLogger(__name__)


class OpenRouterProvider(AIProvider):
    """OpenRouter provider for accessing multiple AI models"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenRouter provider"""
        super().__init__(api_key=api_key or os.getenv("OPENROUTER_API_KEY"))
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided")
        
        # OpenRouter uses OpenAI-compatible API
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": os.environ.get("BACKEND_URL", "https://vulcaart.art"),  # Required by OpenRouter
                "X-Title": "WenXin MoYun Platform",  # Optional, for dashboard
            }
        )
        
        # Available models through OpenRouter
        self.models = {
            "kimi": "moonshotai/kimi-k2",  # Kimi K2 model
            "claude-3-sonnet": "anthropic/claude-3-sonnet",
            "gpt-4": "openai/gpt-4",
            "mixtral": "mistralai/mixtral-8x7b-instruct",
        }
        
        logger.info("OpenRouter provider initialized")
    
    async def generate_poem(
        self,
        prompt: str,
        style: Optional[str] = None,
        language: Language = Language.CHINESE,
        **kwargs
    ) -> PoemResponse:
        """Generate a poem using OpenRouter models"""
        try:
            # Get model name from kwargs or use Kimi as default
            model_name = kwargs.get("model_name", self.models.get("kimi"))
            lang_str = "zh" if language == Language.CHINESE else "en"
            
            if lang_str == "zh":
                full_prompt = f"""请创作一首关于"{prompt}"的{style or '现代'}诗歌。
要求：
1. 语言优美，富有诗意
2. 意境深远，有感染力
3. 结构完整，韵律和谐
4. 富有创造力和想象力"""
            else:
                full_prompt = f"""Write a {style or 'modern'} poem about "{prompt}".
Requirements:
1. Beautiful and poetic language
2. Profound imagery with emotional impact
3. Complete structure with harmonious rhythm
4. Creative and imaginative"""
            
            # Call OpenRouter API
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a talented poet with deep literary knowledge."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1024,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract title if present
            lines = content.split('\n')
            title = lines[0] if lines else prompt
            
            return PoemResponse(
                title=title,
                content=content,
                style=style,
                language=language,
                metadata={
                    "provider": "openrouter",
                    "model": model_name,
                    "tokens_used": response.usage.total_tokens if response.usage else 0
                }
            )
            
        except Exception as e:
            logger.error(f"OpenRouter poem generation failed: {str(e)}")
            raise
    
    async def generate_story(
        self,
        prompt: str,
        max_length: int = 500,
        language: Language = Language.CHINESE,
        **kwargs
    ) -> StoryResponse:
        """Generate a story using OpenRouter models"""
        try:
            model_name = kwargs.get("model_name", self.models.get("kimi"))
            genre = kwargs.get("genre", "fantasy")
            lang_str = "zh" if language == Language.CHINESE else "en"
            
            if lang_str == "zh":
                full_prompt = f"""创作一个{genre}类型的短篇故事。
故事开头：{prompt}
要求：
1. 情节完整，有起承转合
2. 人物形象鲜明，性格突出
3. 语言生动，描写细腻
4. 富有想象力和创意"""
            else:
                full_prompt = f"""Write a {genre} short story.
Beginning: {prompt}
Requirements:
1. Complete plot with clear structure
2. Vivid characters with distinct personalities
3. Engaging language with detailed descriptions
4. Imaginative and creative"""
            
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a creative storyteller with rich imagination."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=2048,
                temperature=0.85
            )
            
            content = response.choices[0].message.content.strip()
            
            return StoryResponse(
                title=f"{genre.title()} Story",
                content=content,
                genre=genre,
                word_count=len(content),
                language=language,
                metadata={
                    "provider": "openrouter",
                    "model": model_name,
                    "tokens_used": response.usage.total_tokens if response.usage else 0
                }
            )
            
        except Exception as e:
            logger.error(f"OpenRouter story generation failed: {str(e)}")
            raise
    
    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        **kwargs
    ) -> ImageResponse:
        """OpenRouter text models don't support image generation"""
        raise NotImplementedError(
            "OpenRouter text models do not support image generation. "
            "Use vulca SDK with provider='mock' or provider='gemini' for image generation."
        )
    
    async def generate_music(
        self,
        prompt: str,
        duration: Optional[int] = None,
        **kwargs
    ) -> MusicResponse:
        """OpenRouter text models don't support music generation"""
        raise NotImplementedError(
            "OpenRouter text models do not support music generation. "
            "Use vulca SDK with provider='mock' or provider='gemini' for image generation."
        )
    
    async def health_check(self) -> bool:
        """Check if the provider is available"""
        try:
            # Test with a simple request to Kimi
            response = await self.client.chat.completions.create(
                model=self.models["kimi"],
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"OpenRouter health check failed: {e}")
            return False
    
    def get_available_models(self) -> Dict[str, str]:
        """Get list of available models through OpenRouter"""
        return self.models.copy()