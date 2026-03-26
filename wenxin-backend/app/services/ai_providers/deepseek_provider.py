"""
DeepSeek AI Provider
Supports DeepSeek's language models using OpenAI-compatible API
"""
import os
import asyncio
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from datetime import datetime

from . import AIProvider, PoemResponse, StoryResponse, ImageResponse, MusicResponse, Language

logger = logging.getLogger(__name__)


class DeepSeekProvider(AIProvider):
    """DeepSeek AI provider using OpenAI-compatible API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize DeepSeek provider"""
        super().__init__(api_key=api_key or os.getenv("DEEPSEEK_API_KEY"))
        if not self.api_key:
            raise ValueError("DeepSeek API key not provided")
        
        # DeepSeek uses OpenAI-compatible API
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1"
        )
        logger.info("DeepSeek provider initialized")
    
    async def generate_poem(
        self,
        prompt: str,
        style: Optional[str] = None,
        language: Language = Language.CHINESE,
        **kwargs
    ) -> PoemResponse:
        """Generate a poem using DeepSeek"""
        try:
            # Construct prompt based on language
            lang_str = "zh" if language == Language.CHINESE else "en"
            model_name = kwargs.get("model_name", "deepseek-chat")
            
            if lang_str == "zh":
                full_prompt = f"""请创作一首关于"{prompt}"的{style or '现代'}诗歌。
要求：语言优美，意境深远，结构完整。"""
            else:
                full_prompt = f"""Write a {style or 'modern'} poem about "{prompt}".
Requirements: Beautiful language, profound imagery, complete structure."""
            
            # Call DeepSeek API
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a talented poet."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1024,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract title if present, otherwise use prompt
            lines = content.split('\n')
            title = lines[0] if lines else prompt
            
            return PoemResponse(
                title=title,
                content=content,
                style=style,
                language=language,
                metadata={
                    "provider": "deepseek",
                    "model": model_name,
                    "tokens_used": response.usage.total_tokens if response.usage else 0
                }
            )
            
        except Exception as e:
            logger.error(f"DeepSeek poem generation failed: {str(e)}")
            raise
    
    async def generate_story(
        self,
        prompt: str,
        max_length: int = 500,
        language: Language = Language.CHINESE,
        **kwargs
    ) -> StoryResponse:
        """Generate a story using DeepSeek"""
        try:
            lang_str = "zh" if language == Language.CHINESE else "en"
            model_name = kwargs.get("model_name", "deepseek-chat")
            genre = kwargs.get("genre", "fantasy")
            
            if lang_str == "zh":
                full_prompt = f"""创作一个{genre}故事，开头：{prompt}
要求：情节完整，人物鲜明，语言生动。"""
            else:
                full_prompt = f"""Write a {genre} story beginning with: {prompt}
Requirements: Complete plot, vivid characters, engaging language."""
            
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a creative storyteller."},
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
                    "provider": "deepseek",
                    "model": model_name,
                    "tokens_used": response.usage.total_tokens if response.usage else 0
                }
            )
            
        except Exception as e:
            logger.error(f"DeepSeek story generation failed: {str(e)}")
            raise
    
    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        **kwargs
    ) -> ImageResponse:
        """DeepSeek doesn't support image generation"""
        raise NotImplementedError(
            "DeepSeek does not support image generation. "
            "Use vulca SDK with provider='mock' or provider='gemini' for image generation."
        )
    
    async def generate_music(
        self,
        prompt: str,
        duration: Optional[int] = None,
        **kwargs
    ) -> MusicResponse:
        """DeepSeek doesn't support music generation"""
        raise NotImplementedError(
            "DeepSeek does not support music generation. "
            "Use vulca SDK with provider='mock' or provider='gemini' for image generation."
        )
    
    async def health_check(self) -> bool:
        """Check if the provider is available"""
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            return True
        except Exception:
            return False