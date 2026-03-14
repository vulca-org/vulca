import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from enum import Enum
import json


class CostController:
    """Smart cost control and budget management"""
    
    # Cost per operation (USD)
    PROVIDER_COSTS = {
        "openai": {
            "gpt-4-turbo": 0.01,  # per 1K tokens (input)
            "gpt-4-turbo-output": 0.03,  # per 1K tokens (output)
            "dalle-3": 0.04,  # per image
        },
        "gemini": {
            "pro": 0.0,  # Free tier
        },
        "huggingface": {
            "text": 0.0,  # Free inference API
            "image": 0.0,  # Free inference API
        },
        "mock": {
            "all": 0.0,  # No cost
        }
    }
    
    # Daily quotas by user tier
    USER_QUOTAS = {
        "guest": {
            "daily_requests": 10,
            "daily_budget": 0.0,  # No paid services
            "allowed_providers": ["gemini", "mock"]
        },
        "user": {
            "daily_requests": 10,
            "daily_budget": 1.0,  # $1 per day
            "allowed_providers": ["gemini", "huggingface", "mock"]
        },
        "premium": {
            "daily_requests": 50,
            "daily_budget": 5.0,  # $5 per day
            "allowed_providers": ["gemini", "huggingface", "mock"]
        },
        "self_hosted": {
            "daily_requests": -1,  # Unlimited
            "daily_budget": 0.0,  # Self-hosted, no external cost
            "allowed_providers": ["openai", "gemini", "huggingface", "mock"]
        },
        "vip": {
            "daily_requests": -1,  # Unlimited
            "daily_budget": 20.0,  # $20 per day
            "allowed_providers": ["openai", "gemini", "huggingface", "mock"]
        }
    }
    
    def __init__(self):
        self.daily_usage = {}  # Track daily usage per user
        self.global_budget_limit = float(os.getenv("DAILY_COST_LIMIT", "50.0"))
        self.enable_cost_control = os.getenv("ENABLE_COST_CONTROL", "true").lower() == "true"
    
    def estimate_cost(
        self,
        provider: str,
        task_type: str,
        estimated_tokens: int = 1000,
        **kwargs
    ) -> float:
        """Estimate the cost of an operation"""
        if not self.enable_cost_control:
            return 0.0
            
        provider_costs = self.PROVIDER_COSTS.get(provider, {})
        
        if provider == "openai":
            if task_type == "painting":
                return provider_costs.get("dalle-3", 0.04)
            else:
                # Estimate input + output tokens
                input_cost = (estimated_tokens / 1000) * provider_costs.get("gpt-4-turbo", 0.01)
                output_cost = (estimated_tokens / 1000) * provider_costs.get("gpt-4-turbo-output", 0.03)
                return input_cost + output_cost
        
        # Other providers are mostly free
        return 0.0
    
    def check_user_quota(
        self,
        user_id: Optional[str],
        user_tier: str = "guest",
        estimated_cost: float = 0.0
    ) -> Tuple[bool, str]:
        """Check if user can make this request"""
        if not self.enable_cost_control:
            return True, "Cost control disabled"
        
        today = datetime.now().date().isoformat()
        user_key = user_id or "anonymous"
        
        # Initialize user tracking
        if user_key not in self.daily_usage:
            self.daily_usage[user_key] = {}
        
        if today not in self.daily_usage[user_key]:
            self.daily_usage[user_key][today] = {
                "requests": 0,
                "cost": 0.0
            }
        
        daily_data = self.daily_usage[user_key][today]
        quota = self.USER_QUOTAS.get(user_tier, self.USER_QUOTAS["guest"])
        
        # Check request limit
        if quota["daily_requests"] > 0:  # -1 means unlimited
            if daily_data["requests"] >= quota["daily_requests"]:
                return False, f"Daily request limit reached ({quota['daily_requests']})"
        
        # Check budget limit
        if daily_data["cost"] + estimated_cost > quota["daily_budget"]:
            return False, f"Daily budget limit reached (${quota['daily_budget']:.2f})"
        
        # Check global budget
        total_daily_cost = self._get_total_daily_cost(today)
        if total_daily_cost + estimated_cost > self.global_budget_limit:
            return False, f"Global daily budget limit reached (${self.global_budget_limit:.2f})"
        
        return True, "OK"
    
    def record_usage(
        self,
        user_id: Optional[str],
        provider: str,
        task_type: str,
        actual_cost: float = 0.0,
        tokens_used: int = 0
    ):
        """Record actual usage after operation"""
        if not self.enable_cost_control:
            return
        
        today = datetime.now().date().isoformat()
        user_key = user_id or "anonymous"
        
        # Ensure user tracking exists
        if user_key not in self.daily_usage:
            self.daily_usage[user_key] = {}
        
        if today not in self.daily_usage[user_key]:
            self.daily_usage[user_key][today] = {
                "requests": 0,
                "cost": 0.0
            }
        
        # Record the usage
        self.daily_usage[user_key][today]["requests"] += 1
        self.daily_usage[user_key][today]["cost"] += actual_cost
        
        # Log for monitoring
        print(f"Usage recorded - User: {user_key}, Provider: {provider}, "
              f"Task: {task_type}, Cost: ${actual_cost:.4f}, Tokens: {tokens_used}")
    
    def get_user_usage_stats(
        self,
        user_id: Optional[str],
        user_tier: str = "guest"
    ) -> Dict:
        """Get user's current usage statistics"""
        today = datetime.now().date().isoformat()
        user_key = user_id or "anonymous"
        quota = self.USER_QUOTAS.get(user_tier, self.USER_QUOTAS["guest"])
        
        current_usage = self.daily_usage.get(user_key, {}).get(today, {
            "requests": 0,
            "cost": 0.0
        })
        
        return {
            "today": today,
            "requests_used": current_usage["requests"],
            "requests_limit": quota["daily_requests"],
            "cost_used": current_usage["cost"],
            "budget_limit": quota["daily_budget"],
            "requests_remaining": max(0, quota["daily_requests"] - current_usage["requests"]) if quota["daily_requests"] > 0 else -1,
            "budget_remaining": max(0, quota["daily_budget"] - current_usage["cost"])
        }
    
    def suggest_provider(
        self,
        task_type: str,
        user_tier: str = "guest",
        budget_remaining: float = 0.0
    ) -> str:
        """Suggest the best provider based on budget"""
        quota = self.USER_QUOTAS.get(user_tier, self.USER_QUOTAS["guest"])
        allowed_providers = quota["allowed_providers"]
        
        if budget_remaining <= 0.0 or user_tier == "guest":
            # Use free providers
            free_providers = ["gemini", "huggingface", "mock"]
            for provider in free_providers:
                if provider in allowed_providers:
                    return provider
            return "mock"
        
        # Use premium providers if budget allows
        if task_type == "painting" and budget_remaining >= 0.04:
            return "openai"
        elif task_type in ["poem", "story"] and budget_remaining >= 0.05:
            return "openai"
        elif "gemini" in allowed_providers:
            return "gemini"
        else:
            return "mock"
    
    def _get_total_daily_cost(self, date: str) -> float:
        """Calculate total daily cost across all users"""
        total_cost = 0.0
        for user_data in self.daily_usage.values():
            if date in user_data:
                total_cost += user_data[date]["cost"]
        return total_cost
    
    def get_system_stats(self) -> Dict:
        """Get system-wide cost statistics"""
        today = datetime.now().date().isoformat()
        total_daily_cost = self._get_total_daily_cost(today)
        
        return {
            "date": today,
            "total_daily_cost": total_daily_cost,
            "global_budget_limit": self.global_budget_limit,
            "budget_remaining": max(0, self.global_budget_limit - total_daily_cost),
            "cost_control_enabled": self.enable_cost_control,
            "active_users_today": len([
                user for user, data in self.daily_usage.items() 
                if today in data and data[today]["requests"] > 0
            ])
        }
    
    def cleanup_old_data(self, days_to_keep: int = 7):
        """Clean up old usage data"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).date().isoformat()
        
        for user_key in self.daily_usage:
            dates_to_remove = [
                date for date in self.daily_usage[user_key].keys() 
                if date < cutoff_date
            ]
            for date in dates_to_remove:
                del self.daily_usage[user_key][date]


# Global instance
cost_controller = CostController()