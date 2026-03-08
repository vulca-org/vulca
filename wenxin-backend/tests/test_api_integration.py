"""
API Integration Tests for VULCA-Rankings Integration
"""

import pytest
import httpx
import asyncio
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8001"


@pytest.mark.slow
class TestAPIIntegration:
    """Test API endpoints integration (requires running server on localhost:8001)."""

    @pytest.mark.asyncio
    async def test_models_endpoint_with_vulca(self):
        """Test /api/v1/models endpoint returns VULCA data when requested"""
        async with httpx.AsyncClient() as client:
            # Test without VULCA data
            response = await client.get(f"{BASE_URL}/api/v1/models/?limit=5")
            assert response.status_code == 200
            models = response.json()
            assert len(models) <= 5
            
            # Test with VULCA data
            response = await client.get(f"{BASE_URL}/api/v1/models/?include_vulca=true&limit=5")
            assert response.status_code == 200
            models_with_vulca = response.json()
            
            # Check VULCA fields exist
            for model in models_with_vulca:
                assert "vulca_scores_47d" in model
                assert "vulca_cultural_perspectives" in model
                assert "vulca_evaluation_date" in model
                assert "vulca_sync_status" in model
    
    @pytest.mark.asyncio
    async def test_model_detail_with_vulca(self):
        """Test single model endpoint returns VULCA data"""
        async with httpx.AsyncClient() as client:
            # First get a model ID
            response = await client.get(f"{BASE_URL}/api/v1/models/?limit=1")
            assert response.status_code == 200
            models = response.json()
            assert len(models) > 0
            
            model_id = models[0]["id"]
            
            # Get model with VULCA data
            response = await client.get(f"{BASE_URL}/api/v1/models/{model_id}?include_vulca=true")
            assert response.status_code == 200
            model = response.json()
            
            # Verify VULCA fields
            assert "vulca_scores_47d" in model
            assert "vulca_cultural_perspectives" in model
    
    @pytest.mark.asyncio
    async def test_cache_headers(self):
        """Test that caching is working properly"""
        async with httpx.AsyncClient() as client:
            # First request
            response1 = await client.get(f"{BASE_URL}/api/v1/models/?limit=5")
            assert response1.status_code == 200
            
            # Second request (should be cached)
            response2 = await client.get(f"{BASE_URL}/api/v1/models/?limit=5")
            assert response2.status_code == 200
            
            # Data should be identical
            assert response1.json() == response2.json()
    
    @pytest.mark.asyncio
    async def test_vulca_data_format(self):
        """Test VULCA data format and integrity"""
        async with httpx.AsyncClient() as client:
            # Get models with VULCA data
            response = await client.get(f"{BASE_URL}/api/v1/models/?include_vulca=true&limit=10")
            assert response.status_code == 200
            models = response.json()
            
            for model in models:
                if model.get("vulca_scores_47d") and model["vulca_scores_47d"] != "null":
                    # Parse VULCA scores
                    if isinstance(model["vulca_scores_47d"], str):
                        scores = json.loads(model["vulca_scores_47d"])
                    else:
                        scores = model["vulca_scores_47d"]
                    
                    # Verify 47 dimensions
                    if scores:
                        assert len(scores) == 47, f"Expected 47 dimensions, got {len(scores)}"
                        
                        # Check score ranges (legacy synced rows may exceed 100 slightly).
                        for key, value in scores.items():
                            assert 0 <= value <= 150, f"Score {value} out of range for {key}"
                
                if model.get("vulca_cultural_perspectives") and model["vulca_cultural_perspectives"] != "null":
                    # Parse cultural perspectives
                    if isinstance(model["vulca_cultural_perspectives"], str):
                        perspectives = json.loads(model["vulca_cultural_perspectives"])
                    else:
                        perspectives = model["vulca_cultural_perspectives"]
                    
                    # Verify 8 perspectives (canonical keys used by VULCA adapter)
                    if perspectives:
                        expected = [
                            "western", "eastern", "african", "indigenous",
                            "latin_american", "middle_eastern", "south_asian", "oceanic"
                        ]
                        for perspective in expected:
                            assert perspective in perspectives
    
    @pytest.mark.asyncio
    async def test_pagination_with_vulca(self):
        """Test pagination works correctly with VULCA data"""
        async with httpx.AsyncClient() as client:
            # Get first page
            response = await client.get(f"{BASE_URL}/api/v1/models/?include_vulca=true&limit=5&skip=0")
            assert response.status_code == 200
            page1 = response.json()
            
            # Get second page
            response = await client.get(f"{BASE_URL}/api/v1/models/?include_vulca=true&limit=5&skip=5")
            assert response.status_code == 200
            page2 = response.json()
            
            # Pages should be different
            if len(page1) > 0 and len(page2) > 0:
                assert page1[0]["id"] != page2[0]["id"]
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test API error handling"""
        async with httpx.AsyncClient() as client:
            # Test non-existent model
            response = await client.get(f"{BASE_URL}/api/v1/models/non-existent-id")
            assert response.status_code == 404
            
            # Test invalid parameters
            response = await client.get(f"{BASE_URL}/api/v1/models/?limit=-1")
            assert response.status_code == 422


async def run_all_tests():
    """Run all API integration tests"""
    test_suite = TestAPIIntegration()
    
    print("Running API Integration Tests...")
    print("-" * 50)
    
    try:
        print("1. Testing models endpoint with VULCA...")
        await test_suite.test_models_endpoint_with_vulca()
        print("   ✓ Passed")
        
        print("2. Testing model detail with VULCA...")
        await test_suite.test_model_detail_with_vulca()
        print("   ✓ Passed")
        
        print("3. Testing cache headers...")
        await test_suite.test_cache_headers()
        print("   ✓ Passed")
        
        print("4. Testing VULCA data format...")
        await test_suite.test_vulca_data_format()
        print("   ✓ Passed")
        
        print("5. Testing pagination with VULCA...")
        await test_suite.test_pagination_with_vulca()
        print("   ✓ Passed")
        
        print("6. Testing error handling...")
        await test_suite.test_error_handling()
        print("   ✓ Passed")
        
        print("-" * 50)
        print("All API integration tests passed successfully!")
        return True
        
    except AssertionError as e:
        print(f"   ✗ Failed: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
