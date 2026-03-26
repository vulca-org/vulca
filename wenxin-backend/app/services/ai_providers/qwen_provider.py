"""
Qwen (Tongyi Qianwen) AI Provider
Supports Alibaba's Qwen models
"""
import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
from datetime import datetime

from . import AIProvider, PoemResponse, StoryResponse, ImageResponse, MusicResponse, Language

logger = logging.getLogger(__name__)


class QwenProvider(AIProvider):
    """Qwen (Tongyi Qianwen) AI provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Qwen provider
        
        Args:
            api_key: Qwen API key
        """
        super().__init__()
        self.api_key = api_key or os.getenv("QWEN_API_KEY")
        if not self.api_key:
            raise ValueError("Qwen API key not provided")
        
        # Qwen uses OpenAI-compatible API
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # Available models
        self.models = {
            "qwen-turbo": {
                "name": "Qwen Turbo",
                "max_tokens": 8192,
                "supports_chinese": True,
                "supports_english": True
            },
            "qwen-plus": {
                "name": "Qwen Plus",
                "max_tokens": 32768,
                "supports_chinese": True,
                "supports_english": True
            },
            "qwen-max": {
                "name": "Qwen Max",
                "max_tokens": 32768,
                "supports_chinese": True,
                "supports_english": True
            }
        }
        
        logger.info("Qwen provider initialized")
    
    async def generate_poem(
        self,
        theme: str,
        style: str = "modern",
        language: str = "zh",
        model_name: str = "qwen-plus"
    ) -> PoemResponse:
        """Generate a poem using Qwen
        
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
1. 紧扣主题"{theme}"
2. 符合{style}诗歌的特点
3. 语言优美，富有诗意
4. 结构完整，韵律优美
5. 具有中国文化特色"""
            else:
                prompt = f"""Compose a {style} poem about "{theme}".
Requirements:
1. Focus on the theme "{theme}"
2. Match {style} poetry characteristics
3. Use beautiful and poetic language
4. Complete structure with good rhythm
5. Show cultural depth"""
            
            start_time = datetime.now()
            
            # Call Qwen API
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "你是一位才华横溢的诗人，精通各种诗歌风格。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.85
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Extract content
            content = response.choices[0].message.content.strip()
            
            # Calculate token usage
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            return PoemResponse(
                title=theme,
                content=content,
                style=style,
                language=Language.CHINESE if language == "zh" else Language.ENGLISH,
                metadata={
                    "provider": "qwen",
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
            logger.error(f"Qwen poem generation failed: {str(e)}")
            raise
    
    async def generate_story(
        self,
        prompt: str,
        genre: str = "fantasy",
        language: str = "zh",
        model_name: str = "qwen-plus"
    ) -> StoryResponse:
        """Generate a story using Qwen
        
        Args:
            prompt: Story prompt
            genre: Genre of the story
            language: Language code
            model_name: Model to use
            
        Returns:
            StoryResponse with story content
        """
        try:
            # Construct prompt based on language
            if language == "zh":
                full_prompt = f"""创作一个{genre}风格的短篇故事。
故事开头：{prompt}
要求：
1. 情节完整，有明确的开端、发展、高潮和结局
2. 人物性格鲜明，对话生动
3. 描写细腻，画面感强
4. 富有想象力和创意
5. 体现中国文化元素"""
            else:
                full_prompt = f"""Create a {genre} short story.
Story beginning: {prompt}
Requirements:
1. Complete plot with clear beginning, development, climax and ending
2. Distinct characters with vivid dialogue
3. Detailed descriptions with strong imagery
4. Rich imagination and creativity
5. Cultural elements incorporated"""
            
            start_time = datetime.now()
            
            # Call Qwen API
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "你是一位富有想象力的故事创作者。"},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=2048,
                temperature=0.9
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Extract content
            content = response.choices[0].message.content.strip()
            
            # Calculate token usage
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            return StoryResponse(
                title=f"{genre.title()} Story",
                content=content,
                genre=genre,
                word_count=len(content),
                language=Language.CHINESE if language == "zh" else Language.ENGLISH,
                metadata={
                    "provider": "qwen",
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
            logger.error(f"Qwen story generation failed: {str(e)}")
            raise
    
    async def evaluate_content(
        self,
        content: str,
        content_type: str = "poem",
        criteria: Optional[List[str]] = None,
        model_name: str = "qwen-plus"
    ) -> Dict[str, Any]:
        """Evaluate content using Qwen
        
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
                criteria = ["creativity", "coherence", "quality", "cultural_relevance"]
            
            prompt = f"""请对以下{content_type}进行专业评价，每项标准打分0-100。
内容：
{content}

评价标准：
{', '.join(criteria)}

请以JSON格式提供分数，并简要说明评分理由。"""
            
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "你是一位专业的文学评论家。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.3
            )
            
            # Parse response
            evaluation_text = response.choices[0].message.content
            
            # Simple score extraction (should be improved with proper JSON parsing)
            scores = {}
            for criterion in criteria:
                scores[criterion] = 80.0  # Default score
            
            return {
                "scores": scores,
                "feedback": evaluation_text,
                "provider": "qwen",
                "model": model_name
            }
            
        except Exception as e:
            logger.error(f"Qwen evaluation failed: {str(e)}")
            raise
    
    def get_info(self) -> Dict[str, Any]:
        """Get provider information
        
        Returns:
            Provider information dictionary
        """
        return {
            "provider": "qwen",
            "name": "Qwen (通义千问)",
            "description": "Alibaba's advanced language models with strong Chinese capabilities",
            "capabilities": ["poem", "story", "evaluation", "translation"],
            "models": list(self.models.keys()),
            "languages": ["zh", "en"],
            "status": "active" if self.api_key else "not_configured"
        }
    
    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        **kwargs
    ):
        """Qwen doesn't support image generation"""
        raise NotImplementedError(
            "Qwen does not support image generation. "
            "Use vulca SDK with provider='mock' or provider='gemini' for image generation."
        )
    
    async def generate_music(
        self,
        prompt: str,
        duration: Optional[int] = None,
        **kwargs
    ):
        """Qwen doesn't support music generation"""
        raise NotImplementedError(
            "Qwen does not support music generation. "
            "Use vulca SDK with provider='mock' or provider='gemini' for image generation."
        )
    
    async def health_check(self) -> bool:
        """Check if the provider is available"""
        try:
            response = await self.client.chat.completions.create(
                model="qwen-plus",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"Qwen health check failed: {e}")
            return False