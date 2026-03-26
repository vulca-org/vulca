import asyncio
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.evaluation_task import EvaluationTask, TaskStatus
from app.models.ai_model import AIModel
from app.models.artwork import Artwork
from app.services.ai_providers.mock_provider import MockProvider
from app.services.models import UnifiedModelClient
from app.services.cost_controller import cost_controller
from app.services.ai_providers import TaskType as ProviderTaskType
from app.services.intelligent_scoring import IntelligentScorer


class EvaluationEngine:
    """Engine for executing AI evaluation tasks"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.unified_client = UnifiedModelClient()
        self.cost_controller = cost_controller
        self.fallback_provider = MockProvider()
        self.intelligent_scorer = IntelligentScorer()
        
    async def execute_evaluation(self, task_id: str, user_tier: str = "guest"):
        """Execute a single evaluation task with real AI providers"""
        try:
            # Get task
            result = await self.db.execute(
                select(EvaluationTask).where(EvaluationTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            
            if not task:
                print(f"Task {task_id} not found")
                return
                
            # Select appropriate model based on task type
            # For now, use gpt-4o-mini as default (best performance/cost ratio)
            model_id = "gpt-4o-mini"
            
            # For premium users, could use better models
            if user_tier == "premium":
                model_id = "o1-mini"  # Best performing model
            
            # Estimate cost (simplified for unified interface)
            estimated_cost = 0.01  # Base estimate
            
            # Check quota
            can_proceed, reason = self.cost_controller.check_user_quota(
                task.user_id, user_tier, estimated_cost
            )
            
            if not can_proceed:
                task.status = TaskStatus.FAILED
                task.error_message = f"Quota exceeded: {reason}"
                await self.db.commit()
                print(f"Task {task_id} failed: {reason}")
                return
                
            # Update status to running
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
            task.progress = 0.0
            await self.db.commit()
            
            print(f"Task {task_id} started with provider: {provider.__class__.__name__}")
            
            # Add realistic delay to simulate processing time
            stage_configs = {
                "poem": {
                    "delays": [15, 45, 30, 20],      # analyzing, generating, refining, evaluating
                    "stages": ["分析提示词", "构思创作", "润色优化", "质量评估"]
                },
                "story": {
                    "delays": [20, 35, 60, 25],     # analyzing, structuring, writing, evaluating  
                    "stages": ["理解需求", "构建框架", "内容创作", "综合评估"]
                },
                "painting": {
                    "delays": [18, 40, 80, 22],  # analyzing, composing, rendering, evaluating
                    "stages": ["主题分析", "构图设计", "图像生成", "美学评估"]
                },
                "music": {
                    "delays": [25, 70, 50, 18],      # analyzing, composing, arranging, evaluating
                    "stages": ["风格分析", "旋律创作", "编曲制作", "音乐评估"]
                }
            }
            
            config = stage_configs.get(task.task_type, {
                "delays": [15, 45, 30, 20],
                "stages": ["分析中", "生成中", "优化中", "评估中"]
            })
            delays = config["delays"]
            stages = config["stages"]
            
            # Simulate stages with delays and progress updates (shortened for demo)
            for i, (delay, stage) in enumerate(zip(delays, stages)):
                # Update current stage and progress
                task.current_stage = stage
                task.progress = (i / len(delays)) * 100
                await self.db.commit()
                print(f"Task {task_id} - Stage {i+1}/{len(delays)}: {stage} ({task.progress:.1f}%)")
                
                # Use shorter delays for demo (divide by 3)
                await asyncio.sleep(delay / 3)
            
            # Execute based on task type using unified client
            if task.task_type == "poem":
                result = await self._evaluate_poem(task, model_id)
            elif task.task_type == "story":
                result = await self._evaluate_story(task, model_id)
            elif task.task_type == "painting":
                result = await self._evaluate_painting(task, model_id)
            elif task.task_type == "music":
                result = await self._evaluate_music(task, model_id)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            # Record actual usage
            provider_name = provider.__class__.__name__.lower().replace('provider', '')
            tokens_used = result.get("metadata", {}).get("tokens_used", 0)
            actual_cost = self.cost_controller.estimate_cost(
                provider_name, task.task_type, tokens_used
            )
            
            self.cost_controller.record_usage(
                task.user_id, provider_name, task.task_type, 
                actual_cost, tokens_used
            )
            
            # Update task with results
            task.status = TaskStatus.COMPLETED
            task.progress = 100.0
            task.current_stage = "已完成"
            task.completed_at = datetime.now(timezone.utc)
            task.result = result["content"]
            task.raw_response = result["raw"]
            task.auto_score = result["score"]
            task.evaluation_metrics = result["metrics"]
            task.final_score = result["score"]  # Use auto score as initial final score
            
            # Create artwork automatically from completed evaluation
            await self._create_artwork_from_evaluation(task, result)
            
            await self.db.commit()
            print(f"Task {task_id} completed successfully with score {result['score']:.1f}")
            
        except Exception as e:
            print(f"Error executing task {task_id}: {str(e)}")
            traceback.print_exc()
            
            # Update task with error
            try:
                result = await self.db.execute(
                    select(EvaluationTask).where(EvaluationTask.id == task_id)
                )
                task = result.scalar_one_or_none()
                if task:
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.now(timezone.utc)
                    task.error_message = str(e)
                    await self.db.commit()
            except:
                pass
    
    async def _evaluate_poem(self, task: EvaluationTask, model_id: str) -> Dict[str, Any]:
        """Evaluate poem generation using unified client"""
        
        # Get language from task parameters  
        language = task.parameters.get("language", "zh")
        
        # Generate poem using unified client
        response = await self.unified_client.generate_poem(
            model_id=model_id,
            theme=task.prompt,
            style="modern",
            language=language,
            max_tokens=300
        )
        
        # Extract content from unified response
        content = response.get('content', '')
        model_used = response.get('model_used', model_id)
        
        # Calculate scores using intelligent scoring
        metrics = await self.intelligent_scorer.evaluate_poem(
            content=content,
            style="modern",
            **task.parameters
        )
        score = sum(metrics.values()) / len(metrics) * 100
        
        # Build content dict
        content_dict = {
            "title": f"Poem by {model_used}",
            "content": content,
            "style": "modern"
        }
        
        return {
            "content": content_dict,
            "raw": response,
            "score": score,
            "metrics": metrics
        }
    
    async def _evaluate_story(self, task: EvaluationTask, model_id: str) -> Dict[str, Any]:
        """Evaluate story generation using unified client"""
        
        # Get language from task parameters
        language = task.parameters.get("language", "zh")
        
        # Generate story using unified client
        response = await self.unified_client.generate_story(
            model_id=model_id,
            prompt=task.prompt,
            genre="general",
            language=language,
            max_tokens=500
        )
        
        # Extract content from unified response
        content = response.get('content', '')
        model_used = response.get('model_used', model_id)
        
        # Calculate scores using intelligent scoring
        metrics = await self.intelligent_scorer.evaluate_story(
            content=content,
            genre="general",
            word_count=len(content.split()),
            **task.parameters
        )
        score = sum(metrics.values()) / len(metrics) * 100
        
        # Build content dict
        content_dict = {
            "title": f"Story by {model_used}",
            "content": content,
            "genre": "general",
            "word_count": len(content.split())
        }
        
        return {
            "content": content_dict,
            "raw": response,
            "score": score,
            "metrics": metrics
        }
    
    async def _evaluate_painting(self, task: EvaluationTask, model_id: str) -> Dict[str, Any]:
        """Painting evaluation requires a VLM-enabled model."""
        raise NotImplementedError(
            f"Painting evaluation not implemented for model '{model_id}'. "
            "Use the vulca SDK (vulca evaluate) for image evaluation with L1-L5 scoring."
        )

    async def _evaluate_music(self, task: EvaluationTask, model_id: str) -> Dict[str, Any]:
        """Music evaluation is not yet supported."""
        raise NotImplementedError(
            f"Music evaluation not implemented for model '{model_id}'."
        )
    
    async def _create_artwork_from_evaluation(self, task: EvaluationTask, result: Dict[str, Any]) -> Optional[Artwork]:
        """Automatically create Artwork from completed evaluation task"""
        try:
            # Get AI model info for artwork
            model_result = await self.db.execute(
                select(AIModel).where(AIModel.id == task.model_id)
            )
            model = model_result.scalar_one_or_none()
            
            # Extract content based on task type
            content_data = result.get("content", {})
            
            # Create artwork based on task type
            artwork_data = {
                "id": f"art_{task.id}",
                "model_id": task.model_id,
                "type": task.task_type,
                "prompt": task.prompt,
                "score": result.get("score", 0.0),
                "created_at": datetime.now(timezone.utc)
            }
            
            # Type-specific content handling
            if task.task_type == "poem":
                artwork_data.update({
                    "title": content_data.get("title", f"Poem by {model.name if model else 'AI'}"),
                    "content": content_data.get("content", ""),
                    "extra_metadata": {
                        "style": content_data.get("style"),
                        "metrics": result.get("metrics", {}),
                        "raw_response": result.get("raw", {})
                    }
                })
            
            elif task.task_type == "story":
                artwork_data.update({
                    "title": content_data.get("title", f"Story by {model.name if model else 'AI'}"),
                    "content": content_data.get("content", ""),
                    "extra_metadata": {
                        "genre": content_data.get("genre"),
                        "word_count": content_data.get("word_count", 0),
                        "metrics": result.get("metrics", {}),
                        "raw_response": result.get("raw", {})
                    }
                })
            
            elif task.task_type == "painting":
                artwork_data.update({
                    "title": f"AI Painting - {task.prompt[:50]}..." if len(task.prompt) > 50 else f"AI Painting - {task.prompt}",
                    "image_url": content_data.get("image_url", ""),
                    "extra_metadata": {
                        "prompt_used": content_data.get("prompt_used", task.prompt),
                        "style": task.parameters.get("style"),
                        "metrics": result.get("metrics", {}),
                        "raw_response": result.get("raw", {})
                    }
                })
            
            elif task.task_type == "music":
                artwork_data.update({
                    "title": f"AI Music - {task.prompt[:50]}..." if len(task.prompt) > 50 else f"AI Music - {task.prompt}",
                    "content": f"Notation: {content_data.get('notation', '')}\nLyrics: {content_data.get('lyrics', '')}",
                    "extra_metadata": {
                        "notation": content_data.get("notation"),
                        "lyrics": content_data.get("lyrics"),
                        "style": task.parameters.get("style"),
                        "metrics": result.get("metrics", {}),
                        "raw_response": result.get("raw", {})
                    }
                })
            
            # Create artwork record
            print(f"DEBUG: Creating artwork with data: {artwork_data}")
            artwork = Artwork(**artwork_data)
            self.db.add(artwork)
            print(f"DEBUG: Added artwork to database session: {artwork.id}")
            
            print(f"Created artwork from task {task.id}: {artwork_data['title']}")
            return artwork
            
        except Exception as e:
            print(f"Error creating artwork from task {task.id}: {e}")
            return None
    
