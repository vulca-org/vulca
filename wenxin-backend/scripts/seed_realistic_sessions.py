#!/usr/bin/env python3
"""
Generate 20 realistic synthetic user sessions for digestion system validation.

Each session has a backstory and represents a distinct usage pattern:
- Cross-cultural fusion attempts
- Expert vs novice behavior
- High/low satisfaction feedback
- Multi-round iteration vs single-pass
- Explicit comments + implicit signals
"""

import json
import time
import uuid

# 20 realistic user sessions with stories
SESSIONS = [
    # ── Story 1: 资深水墨画家，高标准，多轮迭代 ──
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}",
        "mode": "create",
        "intent": "传统山水画，追求气韵生动，留白至少40%",
        "tradition": "chinese_xieyi",
        "subject": "mountain landscape with mist",
        "user_type": "human",
        "user_id": "artist-wang",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c1", "weighted_total": 0.62, "dimension_scores": {"L1": 0.70, "L2": 0.55, "L3": 0.65, "L4": 0.58, "L5": 0.52}, "decision": "rerun", "latency_ms": 12000},
            {"round_num": 1, "candidates_generated": 4, "best_candidate_id": "c3", "weighted_total": 0.78, "dimension_scores": {"L1": 0.82, "L2": 0.72, "L3": 0.85, "L4": 0.76, "L5": 0.75}, "decision": "rerun", "latency_ms": 11000},
            {"round_num": 2, "candidates_generated": 4, "best_candidate_id": "c2", "weighted_total": 0.89, "dimension_scores": {"L1": 0.90, "L2": 0.85, "L3": 0.93, "L4": 0.88, "L5": 0.90}, "decision": "accept", "latency_ms": 10500},
        ],
        "final_scores": {"L1": 0.90, "L2": 0.85, "L3": 0.93, "L4": 0.88, "L5": 0.90},
        "final_weighted_total": 0.89,
        "best_image_url": "",
        "risk_flags": [],
        "recommendations": ["Consider more variation in ink tones"],
        "feedback": [{"type": "explicit", "liked": True, "comment": "第三轮终于抓住了气韵，留白的比例很好。前两轮墨色太平，缺少浓淡对比。", "action": "accept", "final_score": 0.89, "rounds_used": 3, "total_cost_usd": 0.42}],
        "total_rounds": 3,
        "total_latency_ms": 33500,
        "total_cost_usd": 0.42,
        "candidate_choice_index": 1,
        "time_to_select_ms": 15000,
        "downloaded": True,
        "cultural_features": {
            "tradition_specificity": 0.8,
            "l5_emphasis": 0.90 / 0.93,
            "avg_score": 0.892,
            "risk_level": 0.0,
            "cultural_depth": 0.93,
            "dimension_variance": 0.028,
            "l4_emphasis": 0.88 / 0.93,
            "generation_efficiency": 0.0,
            "emotional_tone": ["Serene", "Contemplative", "Transcendent"],
            "style_elements": ["Ink wash (水墨)", "留白 40%+", "Graded tones", "Mist layers"],
            "technique_markers": ["墨分五色", "飞白", "湿笔渲染", "Spontaneous strokes"],
            "cultural_references": ["文人画传统", "道法自然", "气韵生动论"]
        },
        "critic_insights": ["Strong qi-yun achieved through mist layering", "Excellent negative space ratio"],
        "media_type": "image",
        "created_at": time.time() - 3600 * 2,
    },

    # ── Story 2: 设计师尝试赛博朋克水墨融合 ──
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}",
        "mode": "create",
        "intent": "cyberpunk cityscape painted in Chinese ink wash style, neon lights bleeding through ink",
        "tradition": "chinese_xieyi",
        "subject": "cyberpunk ink city",
        "user_type": "human",
        "user_id": "designer-li",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c2", "weighted_total": 0.71, "dimension_scores": {"L1": 0.78, "L2": 0.65, "L3": 0.60, "L4": 0.80, "L5": 0.72}, "decision": "accept", "latency_ms": 14000},
        ],
        "final_scores": {"L1": 0.78, "L2": 0.65, "L3": 0.60, "L4": 0.80, "L5": 0.72},
        "final_weighted_total": 0.71,
        "best_image_url": "",
        "risk_flags": ["cultural_fusion_unverified"],
        "recommendations": ["Fusion style lacks traditional evaluation criteria"],
        "feedback": [{"type": "explicit", "liked": True, "comment": "L3 cultural context score seems too low — this IS a valid contemporary interpretation of ink wash. The system doesn't understand fusion art.", "action": "accept", "final_score": 0.71, "rounds_used": 1, "total_cost_usd": 0.14}],
        "total_rounds": 1,
        "total_latency_ms": 14000,
        "total_cost_usd": 0.14,
        "candidate_choice_index": 1,
        "time_to_select_ms": 8000,
        "downloaded": True,
        "cultural_features": {
            "tradition_specificity": 0.8,
            "l5_emphasis": 0.72 / 0.80,
            "avg_score": 0.71,
            "risk_level": 0.25,
            "cultural_depth": 0.60,
            "dimension_variance": 0.073,
            "l4_emphasis": 0.80 / 0.80,
            "generation_efficiency": 0.67,
            "emotional_tone": ["Futuristic", "Melancholic", "Urban energy"],
            "style_elements": ["Ink wash (水墨)", "Neon glow", "Digital noise", "Cyberpunk aesthetic"],
            "technique_markers": ["Mixed media", "Digital ink simulation", "Light bleeding through wash"],
            "cultural_references": ["当代水墨", "Cyberpunk genre", "Post-traditional art"]
        },
        "critic_insights": ["Fusion of ink wash and cyberpunk creates interesting tension", "L3 may undervalue contemporary fusion"],
        "media_type": "image",
        "created_at": time.time() - 3600 * 1.5,
    },

    # ── Story 3: 日本侘寂花道 ──
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}",
        "mode": "create",
        "intent": "single branch of plum blossom in snow, extreme minimalism, wabi-sabi aesthetic",
        "tradition": "japanese_traditional",
        "subject": "plum blossom in snow",
        "user_type": "human",
        "user_id": "user-tanaka",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c4", "weighted_total": 0.85, "dimension_scores": {"L1": 0.88, "L2": 0.82, "L3": 0.90, "L4": 0.83, "L5": 0.82}, "decision": "accept", "latency_ms": 11000},
        ],
        "final_scores": {"L1": 0.88, "L2": 0.82, "L3": 0.90, "L4": 0.83, "L5": 0.82},
        "final_weighted_total": 0.85,
        "best_image_url": "",
        "risk_flags": [],
        "recommendations": [],
        "feedback": [{"type": "implicit", "liked": True, "action": "accept", "final_score": 0.85, "rounds_used": 1, "total_cost_usd": 0.12}],
        "total_rounds": 1,
        "total_latency_ms": 11000,
        "total_cost_usd": 0.12,
        "candidate_choice_index": 3,
        "time_to_select_ms": 22000,
        "downloaded": True,
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.82/0.90, "avg_score": 0.85,
            "risk_level": 0.0, "cultural_depth": 0.90, "dimension_variance": 0.034,
            "l4_emphasis": 0.83/0.90, "generation_efficiency": 0.67,
            "emotional_tone": ["Wabi-sabi", "Mono no aware", "Stillness"],
            "style_elements": ["Extreme minimalism", "Asymmetric composition", "Ma (間) space"],
            "technique_markers": ["Sumi-e brushwork", "Single stroke emphasis", "Snow as negative space"],
            "cultural_references": ["侘寂 (Wabi-sabi)", "花道 (Ikebana)", "禅 aesthetics"]
        },
        "critic_insights": ["Exceptional use of ma (negative space)", "Wabi-sabi imperfection captured"],
        "media_type": "image",
        "created_at": time.time() - 3600 * 1,
    },

    # ── Story 4: 非洲传统 — 低分，用户不满 ──
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}",
        "mode": "create",
        "intent": "Adinkra symbol pattern with gold leaf on dark background",
        "tradition": "african_traditional",
        "subject": "Adinkra pattern",
        "user_type": "human",
        "user_id": "user-kwame",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c1", "weighted_total": 0.45, "dimension_scores": {"L1": 0.55, "L2": 0.40, "L3": 0.35, "L4": 0.48, "L5": 0.42}, "decision": "rerun", "latency_ms": 15000},
            {"round_num": 1, "candidates_generated": 4, "best_candidate_id": "c2", "weighted_total": 0.52, "dimension_scores": {"L1": 0.58, "L2": 0.48, "L3": 0.45, "L4": 0.55, "L5": 0.50}, "decision": "stop", "latency_ms": 14000},
        ],
        "final_scores": {"L1": 0.58, "L2": 0.48, "L3": 0.45, "L4": 0.55, "L5": 0.50},
        "final_weighted_total": 0.52,
        "best_image_url": "",
        "risk_flags": ["low_cultural_accuracy", "symbol_misrepresentation"],
        "recommendations": ["Adinkra symbols require precise geometric forms", "Consider consulting cultural references"],
        "feedback": [{"type": "explicit", "liked": False, "comment": "The Adinkra symbols are completely wrong — Sankofa should face backward, not forward. The system doesn't know African symbolism at all.", "action": "stop", "final_score": 0.52, "rounds_used": 2, "total_cost_usd": 0.28}],
        "total_rounds": 2,
        "total_latency_ms": 29000,
        "total_cost_usd": 0.28,
        "candidate_choice_index": -1,
        "time_to_select_ms": 3000,
        "downloaded": False,
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.50/0.58, "avg_score": 0.512,
            "risk_level": 0.5, "cultural_depth": 0.45, "dimension_variance": 0.063,
            "l4_emphasis": 0.55/0.58, "generation_efficiency": 0.33,
            "emotional_tone": ["Frustration", "Cultural disconnect"],
            "style_elements": ["Geometric patterns", "Gold on black", "Symbolic art"],
            "technique_markers": ["Precision geometry needed", "Symmetry issues"],
            "cultural_references": ["Adinkra symbols", "Akan culture", "Sankofa"]
        },
        "critic_insights": ["Symbol accuracy is critically low", "Cultural context needs improvement"],
        "media_type": "image",
        "created_at": time.time() - 3600 * 0.8,
    },

    # ── Story 5: 伊斯兰几何 — 高精度，完美通过 ──
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}",
        "mode": "create",
        "intent": "Moorish zellige tile pattern, 8-fold rotational symmetry, deep blue and gold",
        "tradition": "islamic_geometric",
        "subject": "zellige tile pattern",
        "user_type": "human",
        "user_id": "architect-hassan",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c1", "weighted_total": 0.91, "dimension_scores": {"L1": 0.92, "L2": 0.95, "L3": 0.88, "L4": 0.90, "L5": 0.89}, "decision": "accept", "latency_ms": 13000},
        ],
        "final_scores": {"L1": 0.92, "L2": 0.95, "L3": 0.88, "L4": 0.90, "L5": 0.89},
        "final_weighted_total": 0.91,
        "best_image_url": "",
        "risk_flags": [],
        "recommendations": [],
        "feedback": [{"type": "explicit", "liked": True, "comment": "Perfect geometric precision. The 8-fold symmetry is mathematically correct. Excellent understanding of zellige craft.", "action": "accept", "final_score": 0.91, "rounds_used": 1, "total_cost_usd": 0.12}],
        "total_rounds": 1,
        "total_latency_ms": 13000,
        "total_cost_usd": 0.12,
        "candidate_choice_index": 0,
        "time_to_select_ms": 5000,
        "downloaded": True,
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.89/0.95, "avg_score": 0.908,
            "risk_level": 0.0, "cultural_depth": 0.88, "dimension_variance": 0.025,
            "l4_emphasis": 0.90/0.95, "generation_efficiency": 0.67,
            "emotional_tone": ["Sacred geometry", "Divine order", "Meditative"],
            "style_elements": ["8-fold symmetry", "Zellige tessellation", "Deep blue and gold palette"],
            "technique_markers": ["Mathematical precision", "Rotational symmetry", "Interlocking forms"],
            "cultural_references": ["Moorish art", "Alhambra", "Islamic geometric tradition"]
        },
        "critic_insights": ["Exceptional geometric precision", "Authentic zellige craft understanding"],
        "media_type": "image",
        "created_at": time.time() - 3600 * 0.5,
    },

    # ── Story 6: 水彩风景 — 普通用户，中等满意 ──
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}",
        "mode": "create",
        "intent": "watercolor sunset over lavender fields in Provence",
        "tradition": "watercolor",
        "subject": "lavender field sunset",
        "user_type": "human",
        "user_id": "hobbyist-marie",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c3", "weighted_total": 0.74, "dimension_scores": {"L1": 0.80, "L2": 0.70, "L3": 0.72, "L4": 0.75, "L5": 0.68}, "decision": "accept", "latency_ms": 12000},
        ],
        "final_scores": {"L1": 0.80, "L2": 0.70, "L3": 0.72, "L4": 0.75, "L5": 0.68},
        "final_weighted_total": 0.74,
        "best_image_url": "",
        "risk_flags": [],
        "recommendations": ["More wet-on-wet blending would enhance atmosphere"],
        "feedback": [{"type": "implicit", "liked": True, "action": "accept", "final_score": 0.74, "rounds_used": 1, "total_cost_usd": 0.12}],
        "total_rounds": 1,
        "total_latency_ms": 12000,
        "total_cost_usd": 0.12,
        "candidate_choice_index": 2,
        "time_to_select_ms": 12000,
        "downloaded": True,
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.68/0.80, "avg_score": 0.73,
            "risk_level": 0.0, "cultural_depth": 0.72, "dimension_variance": 0.042,
            "l4_emphasis": 0.75/0.80, "generation_efficiency": 0.67,
            "emotional_tone": ["Romantic", "Peaceful", "Golden hour warmth"],
            "style_elements": ["Wet-on-wet", "Atmospheric perspective", "Warm palette"],
            "technique_markers": ["Transparent washes", "Color gradients", "Soft edges"],
            "cultural_references": ["Impressionist landscape", "Provence imagery"]
        },
        "critic_insights": ["Good atmospheric quality", "Could benefit from more transparency layers"],
        "media_type": "image",
        "created_at": time.time() - 3600 * 0.3,
    },

    # ── Story 7: 印度 Rasa 叙事 — 多轮改进 ──
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}",
        "mode": "create",
        "intent": "Radha-Krishna divine love scene in Rajasthani miniature style, depicting Shringara rasa",
        "tradition": "indian_rasa",
        "subject": "Radha-Krishna Shringara",
        "user_type": "human",
        "user_id": "scholar-priya",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c1", "weighted_total": 0.68, "dimension_scores": {"L1": 0.72, "L2": 0.60, "L3": 0.75, "L4": 0.65, "L5": 0.63}, "decision": "rerun", "latency_ms": 13500},
            {"round_num": 1, "candidates_generated": 4, "best_candidate_id": "c4", "weighted_total": 0.82, "dimension_scores": {"L1": 0.85, "L2": 0.78, "L3": 0.88, "L4": 0.80, "L5": 0.79}, "decision": "accept", "latency_ms": 12500},
        ],
        "final_scores": {"L1": 0.85, "L2": 0.78, "L3": 0.88, "L4": 0.80, "L5": 0.79},
        "final_weighted_total": 0.82,
        "best_image_url": "",
        "risk_flags": [],
        "recommendations": ["Consider adding more specific mudra gestures"],
        "feedback": [{"type": "explicit", "liked": True, "comment": "The Shringara rasa is well captured in the second round. The color palette with vermillion and saffron is authentic to Rajasthani miniature.", "action": "accept", "final_score": 0.82, "rounds_used": 2, "total_cost_usd": 0.26}],
        "total_rounds": 2,
        "total_latency_ms": 26000,
        "total_cost_usd": 0.26,
        "candidate_choice_index": 3,
        "time_to_select_ms": 18000,
        "downloaded": True,
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.79/0.88, "avg_score": 0.82,
            "risk_level": 0.0, "cultural_depth": 0.88, "dimension_variance": 0.04,
            "l4_emphasis": 0.80/0.88, "generation_efficiency": 0.33,
            "emotional_tone": ["Divine love", "Devotional", "Shringara rasa"],
            "style_elements": ["Rajasthani miniature", "Vermillion palette", "Ornate border", "Profile perspective"],
            "technique_markers": ["Fine detail brushwork", "Gold leaf accents", "Flat perspective"],
            "cultural_references": ["Bhakti movement", "Rasa theory", "Rajput court painting"]
        },
        "critic_insights": ["Authentic Rajasthani color palette", "Shringara rasa successfully conveyed"],
        "media_type": "image",
        "created_at": time.time() - 3600 * 0.2,
    },

    # ── Story 8: 工笔花鸟 — 技法高要求 ──
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}",
        "mode": "create",
        "intent": "工笔花鸟画，牡丹与翠鸟，三矾九染技法",
        "tradition": "chinese_gongbi",
        "subject": "peony with kingfisher",
        "user_type": "human",
        "user_id": "master-zhang",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c2", "weighted_total": 0.76, "dimension_scores": {"L1": 0.82, "L2": 0.85, "L3": 0.78, "L4": 0.68, "L5": 0.65}, "decision": "rerun", "latency_ms": 14000},
            {"round_num": 1, "candidates_generated": 4, "best_candidate_id": "c1", "weighted_total": 0.84, "dimension_scores": {"L1": 0.88, "L2": 0.90, "L3": 0.85, "L4": 0.80, "L5": 0.78}, "decision": "accept", "latency_ms": 13000},
        ],
        "final_scores": {"L1": 0.88, "L2": 0.90, "L3": 0.85, "L4": 0.80, "L5": 0.78},
        "final_weighted_total": 0.84,
        "best_image_url": "",
        "risk_flags": [],
        "recommendations": [],
        "feedback": [{"type": "explicit", "liked": True, "comment": "线条质量很好，三矾九染的层次感到位。翠鸟的羽毛细节可以再精细些。", "action": "accept", "final_score": 0.84, "rounds_used": 2, "total_cost_usd": 0.28}],
        "total_rounds": 2,
        "total_latency_ms": 27000,
        "total_cost_usd": 0.28,
        "candidate_choice_index": 0,
        "time_to_select_ms": 10000,
        "downloaded": True,
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.78/0.90, "avg_score": 0.842,
            "risk_level": 0.0, "cultural_depth": 0.85, "dimension_variance": 0.045,
            "l4_emphasis": 0.80/0.90, "generation_efficiency": 0.33,
            "emotional_tone": ["Elegant", "Refined", "Classical beauty"],
            "style_elements": ["Fine line (白描)", "三矾九染 layering", "Realistic detail"],
            "technique_markers": ["Iron-wire line (铁线描)", "Color layering", "Silk texture rendering"],
            "cultural_references": ["宋代院体画", "工笔传统", "花鸟画 genre"]
        },
        "critic_insights": ["Excellent line quality (白描)", "Good 三矾九染 layering technique"],
        "media_type": "image",
        "created_at": time.time() - 3600 * 0.15,
    },

    # ── Story 9: 西方学院派 — 新手用户，一次通过但分数中等 ──
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}",
        "mode": "create",
        "intent": "classical still life with fruit bowl, chiaroscuro lighting",
        "tradition": "western_academic",
        "subject": "still life fruit bowl",
        "user_type": "human",
        "user_id": "student-emma",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c2", "weighted_total": 0.70, "dimension_scores": {"L1": 0.75, "L2": 0.72, "L3": 0.65, "L4": 0.68, "L5": 0.62}, "decision": "accept", "latency_ms": 11000},
        ],
        "final_scores": {"L1": 0.75, "L2": 0.72, "L3": 0.65, "L4": 0.68, "L5": 0.62},
        "final_weighted_total": 0.70,
        "best_image_url": "",
        "risk_flags": [],
        "recommendations": ["Strengthen chiaroscuro contrast", "Refine perspective accuracy"],
        "feedback": [{"type": "implicit", "liked": True, "action": "accept", "final_score": 0.70, "rounds_used": 1, "total_cost_usd": 0.12}],
        "total_rounds": 1,
        "total_latency_ms": 11000,
        "total_cost_usd": 0.12,
        "candidate_choice_index": 1,
        "time_to_select_ms": 6000,
        "downloaded": True,
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.62/0.75, "avg_score": 0.684,
            "risk_level": 0.0, "cultural_depth": 0.65, "dimension_variance": 0.048,
            "l4_emphasis": 0.68/0.75, "generation_efficiency": 0.67,
            "emotional_tone": ["Classical", "Contemplative"],
            "style_elements": ["Chiaroscuro", "Academic realism", "Oil painting texture"],
            "technique_markers": ["Light-dark contrast", "Form modeling", "Atmospheric perspective"],
            "cultural_references": ["Caravaggio tradition", "Dutch Golden Age"]
        },
        "critic_insights": ["Adequate chiaroscuro but could be stronger", "Good compositional sense"],
        "media_type": "image",
        "created_at": time.time() - 3600 * 0.1,
    },

    # ── Story 10: 南亚传统 — 用户不满意评分方式 ──
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}",
        "mode": "create",
        "intent": "Warli tribal art depicting harvest festival, using only white on terracotta",
        "tradition": "south_asian",
        "subject": "Warli harvest festival",
        "user_type": "human",
        "user_id": "curator-amita",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c3", "weighted_total": 0.58, "dimension_scores": {"L1": 0.62, "L2": 0.50, "L3": 0.55, "L4": 0.60, "L5": 0.55}, "decision": "stop", "latency_ms": 12000},
        ],
        "final_scores": {"L1": 0.62, "L2": 0.50, "L3": 0.55, "L4": 0.60, "L5": 0.55},
        "final_weighted_total": 0.58,
        "best_image_url": "",
        "risk_flags": ["tribal_art_evaluation_gap"],
        "recommendations": ["System may not have adequate training on tribal art forms"],
        "feedback": [{"type": "explicit", "liked": False, "comment": "Warli art is intentionally simple — stick figures and geometric shapes are the POINT, not a deficiency. L2 technical score penalizes simplicity unfairly.", "action": "stop", "final_score": 0.58, "rounds_used": 1, "total_cost_usd": 0.12}],
        "total_rounds": 1,
        "total_latency_ms": 12000,
        "total_cost_usd": 0.12,
        "candidate_choice_index": -1,
        "time_to_select_ms": 2000,
        "downloaded": False,
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.55/0.62, "avg_score": 0.564,
            "risk_level": 0.25, "cultural_depth": 0.55, "dimension_variance": 0.042,
            "l4_emphasis": 0.60/0.62, "generation_efficiency": 0.67,
            "emotional_tone": ["Community", "Celebration", "Earth connection"],
            "style_elements": ["Stick figures", "Geometric patterns", "White on terracotta"],
            "technique_markers": ["Rice paste medium", "Circle-triangle vocabulary", "Flat composition"],
            "cultural_references": ["Warli tribe", "Maharashtra tribal art", "Harvest rituals"]
        },
        "critic_insights": ["Simplicity is core to Warli aesthetic", "L2 may penalize intentional minimalism"],
        "media_type": "image",
        "created_at": time.time() - 3600 * 0.05,
    },

    # ── Stories 11-20: 快速多样场景 ──

    # 11: 第二个赛博朋克水墨（形成聚类趋势）
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}", "mode": "create",
        "intent": "neon dragon rising from ink wash clouds, traditional Chinese dragon form with digital effects",
        "tradition": "chinese_xieyi", "subject": "neon ink dragon", "user_type": "human", "user_id": "gamer-chen",
        "rounds": [{"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c1", "weighted_total": 0.75, "dimension_scores": {"L1": 0.82, "L2": 0.70, "L3": 0.68, "L4": 0.78, "L5": 0.72}, "decision": "accept", "latency_ms": 12000}],
        "final_scores": {"L1": 0.82, "L2": 0.70, "L3": 0.68, "L4": 0.78, "L5": 0.72},
        "final_weighted_total": 0.75, "best_image_url": "", "risk_flags": ["cultural_fusion_unverified"],
        "recommendations": [], "total_rounds": 1, "total_latency_ms": 12000, "total_cost_usd": 0.12,
        "candidate_choice_index": 0, "time_to_select_ms": 5000, "downloaded": True,
        "feedback": [{"type": "explicit", "liked": True, "comment": "Love the neon dragon! This fusion style is exactly what I wanted.", "action": "accept", "final_score": 0.75, "rounds_used": 1, "total_cost_usd": 0.12}],
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.72/0.82, "avg_score": 0.74, "risk_level": 0.25,
            "cultural_depth": 0.68, "dimension_variance": 0.053, "l4_emphasis": 0.78/0.82, "generation_efficiency": 0.67,
            "emotional_tone": ["Powerful", "Futuristic", "Mythic"],
            "style_elements": ["Ink wash (水墨)", "Neon effects", "Dragon motif", "Digital fusion"],
            "technique_markers": ["Digital ink", "Light-wash blend", "Mythic creature rendering"],
            "cultural_references": ["Dragon mythology", "当代水墨", "Digital art fusion"]
        }, "critic_insights": ["Strong fusion aesthetic", "Dragon form maintains traditional proportions"],
        "media_type": "image", "created_at": time.time() - 2400,
    },

    # 12: 第三个赛博朋克水墨（聚类加强）
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}", "mode": "create",
        "intent": "Shanghai Bund skyline rendered in digital ink wash, rain drops as ink splatter",
        "tradition": "chinese_xieyi", "subject": "Shanghai digital ink", "user_type": "human", "user_id": "photographer-liu",
        "rounds": [{"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c2", "weighted_total": 0.79, "dimension_scores": {"L1": 0.85, "L2": 0.75, "L3": 0.72, "L4": 0.82, "L5": 0.78}, "decision": "accept", "latency_ms": 11000}],
        "final_scores": {"L1": 0.85, "L2": 0.75, "L3": 0.72, "L4": 0.82, "L5": 0.78},
        "final_weighted_total": 0.79, "best_image_url": "", "risk_flags": [],
        "recommendations": [], "total_rounds": 1, "total_latency_ms": 11000, "total_cost_usd": 0.12,
        "candidate_choice_index": 1, "time_to_select_ms": 7000, "downloaded": True,
        "feedback": [{"type": "explicit", "liked": True, "comment": "Beautiful blend of traditional ink and urban landscape. The rain as ink splatter is genius.", "action": "accept", "final_score": 0.79, "rounds_used": 1, "total_cost_usd": 0.12}],
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.78/0.85, "avg_score": 0.784, "risk_level": 0.0,
            "cultural_depth": 0.72, "dimension_variance": 0.048, "l4_emphasis": 0.82/0.85, "generation_efficiency": 0.67,
            "emotional_tone": ["Urban nostalgia", "Rainy atmosphere", "Modern-traditional tension"],
            "style_elements": ["Ink wash (水墨)", "Urban skyline", "Rain effects", "Architectural silhouettes"],
            "technique_markers": ["Ink splatter (泼墨)", "Wet-on-wet urban wash", "Atmospheric perspective"],
            "cultural_references": ["当代水墨", "Shanghai cosmopolitan culture", "Urban ink movement"]
        }, "critic_insights": ["Effective urban-traditional fusion", "Rain as ink splatter is creative"],
        "media_type": "image", "created_at": time.time() - 2200,
    },

    # 13: 工笔人物 — 评价
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}", "mode": "evaluate",
        "intent": "evaluate this Gongbi portrait of a Tang dynasty court lady",
        "tradition": "chinese_gongbi", "subject": "Tang court lady portrait", "user_type": "human", "user_id": "professor-wu",
        "rounds": [{"round_num": 0, "candidates_generated": 0, "best_candidate_id": "", "weighted_total": 0.87, "dimension_scores": {"L1": 0.90, "L2": 0.92, "L3": 0.85, "L4": 0.83, "L5": 0.80}, "decision": "accept", "latency_ms": 8000}],
        "final_scores": {"L1": 0.90, "L2": 0.92, "L3": 0.85, "L4": 0.83, "L5": 0.80},
        "final_weighted_total": 0.87, "best_image_url": "", "risk_flags": [],
        "recommendations": ["Historically accurate costume details"], "total_rounds": 1, "total_latency_ms": 8000, "total_cost_usd": 0.08,
        "candidate_choice_index": -1, "time_to_select_ms": 0, "downloaded": False,
        "feedback": [{"type": "explicit", "liked": True, "comment": "Accurate evaluation. The L2 score correctly captures the fine brushwork quality.", "action": "accept", "final_score": 0.87, "rounds_used": 1, "total_cost_usd": 0.08}],
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.80/0.92, "avg_score": 0.86, "risk_level": 0.0,
            "cultural_depth": 0.85, "dimension_variance": 0.045, "l4_emphasis": 0.83/0.92, "generation_efficiency": 0.67,
            "emotional_tone": ["Graceful", "Historical", "Refined beauty"],
            "style_elements": ["Fine line (白描)", "Layered color", "Detailed costume", "Portrait composition"],
            "technique_markers": ["Hair-thin lines", "Mineral pigments", "Silk rendering"],
            "cultural_references": ["唐代仕女画", "周昉传统", "Gongbi portraiture"]
        }, "critic_insights": ["Excellent fine line quality", "Historically accurate details"],
        "media_type": "image", "created_at": time.time() - 2000,
    },

    # 14: 日本浮世绘风格
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}", "mode": "create",
        "intent": "Great wave off Kanagawa reimagined with modern ships",
        "tradition": "japanese_traditional", "subject": "modern great wave", "user_type": "human", "user_id": "illustrator-yuki",
        "rounds": [{"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c3", "weighted_total": 0.80, "dimension_scores": {"L1": 0.85, "L2": 0.78, "L3": 0.82, "L4": 0.80, "L5": 0.75}, "decision": "accept", "latency_ms": 12500}],
        "final_scores": {"L1": 0.85, "L2": 0.78, "L3": 0.82, "L4": 0.80, "L5": 0.75},
        "final_weighted_total": 0.80, "best_image_url": "", "risk_flags": [],
        "recommendations": [], "total_rounds": 1, "total_latency_ms": 12500, "total_cost_usd": 0.12,
        "candidate_choice_index": 2, "time_to_select_ms": 9000, "downloaded": True,
        "feedback": [{"type": "implicit", "liked": True, "action": "accept", "final_score": 0.80, "rounds_used": 1, "total_cost_usd": 0.12}],
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.75/0.85, "avg_score": 0.80, "risk_level": 0.0,
            "cultural_depth": 0.82, "dimension_variance": 0.034, "l4_emphasis": 0.80/0.85, "generation_efficiency": 0.67,
            "emotional_tone": ["Dramatic", "Power of nature", "Timeless"],
            "style_elements": ["Ukiyo-e composition", "Wave patterns", "Flat color blocks"],
            "technique_markers": ["Woodblock print style", "Bold outlines", "Prussian blue palette"],
            "cultural_references": ["Hokusai", "Ukiyo-e tradition", "Edo period art"]
        }, "critic_insights": ["Faithful to Hokusai style while adding modern elements"],
        "media_type": "image", "created_at": time.time() - 1800,
    },

    # 15: 非洲面具 — 第二个负面反馈（强化趋势）
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}", "mode": "create",
        "intent": "Dan mask from Côte d'Ivoire, ceremonial context, carved wood texture",
        "tradition": "african_traditional", "subject": "Dan ceremonial mask", "user_type": "human", "user_id": "anthropologist-james",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c1", "weighted_total": 0.55, "dimension_scores": {"L1": 0.60, "L2": 0.50, "L3": 0.48, "L4": 0.58, "L5": 0.52}, "decision": "stop", "latency_ms": 13000},
        ],
        "final_scores": {"L1": 0.60, "L2": 0.50, "L3": 0.48, "L4": 0.58, "L5": 0.52},
        "final_weighted_total": 0.55, "best_image_url": "", "risk_flags": ["cultural_stereotyping"],
        "recommendations": ["Mask proportions don't match Dan style"], "total_rounds": 1, "total_latency_ms": 13000, "total_cost_usd": 0.12,
        "candidate_choice_index": -1, "time_to_select_ms": 1500, "downloaded": False,
        "feedback": [{"type": "explicit", "liked": False, "comment": "This looks like a generic 'African mask' — not a Dan mask specifically. Dan masks have narrow eyes and smooth oval faces. System conflates all African art.", "action": "stop", "final_score": 0.55, "rounds_used": 1, "total_cost_usd": 0.12}],
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.52/0.60, "avg_score": 0.536, "risk_level": 0.25,
            "cultural_depth": 0.48, "dimension_variance": 0.044, "l4_emphasis": 0.58/0.60, "generation_efficiency": 0.67,
            "emotional_tone": ["Frustration", "Cultural erasure"],
            "style_elements": ["Carved wood texture", "Mask form", "Ceremonial context"],
            "technique_markers": ["Wood carving simulation", "Surface texture"],
            "cultural_references": ["Dan people", "Côte d'Ivoire", "Mask ceremony"]
        }, "critic_insights": ["Generic African aesthetic applied instead of Dan-specific features"],
        "media_type": "image", "created_at": time.time() - 1600,
    },

    # 16: 伊斯兰书法
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}", "mode": "create",
        "intent": "Thuluth calligraphy of Bismillah with floral illumination border",
        "tradition": "islamic_geometric", "subject": "Bismillah Thuluth calligraphy", "user_type": "human", "user_id": "calligrapher-omar",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c1", "weighted_total": 0.72, "dimension_scores": {"L1": 0.78, "L2": 0.80, "L3": 0.70, "L4": 0.65, "L5": 0.62}, "decision": "rerun", "latency_ms": 12000},
            {"round_num": 1, "candidates_generated": 4, "best_candidate_id": "c3", "weighted_total": 0.83, "dimension_scores": {"L1": 0.85, "L2": 0.88, "L3": 0.82, "L4": 0.80, "L5": 0.78}, "decision": "accept", "latency_ms": 11500},
        ],
        "final_scores": {"L1": 0.85, "L2": 0.88, "L3": 0.82, "L4": 0.80, "L5": 0.78},
        "final_weighted_total": 0.83, "best_image_url": "", "risk_flags": [],
        "recommendations": [], "total_rounds": 2, "total_latency_ms": 23500, "total_cost_usd": 0.24,
        "candidate_choice_index": 2, "time_to_select_ms": 14000, "downloaded": True,
        "feedback": [{"type": "explicit", "liked": True, "comment": "Much improved in round 2. The letter proportions in Thuluth script are now correct. Beautiful illumination.", "action": "accept", "final_score": 0.83, "rounds_used": 2, "total_cost_usd": 0.24}],
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.78/0.88, "avg_score": 0.826, "risk_level": 0.0,
            "cultural_depth": 0.82, "dimension_variance": 0.036, "l4_emphasis": 0.80/0.88, "generation_efficiency": 0.33,
            "emotional_tone": ["Sacred", "Devotional", "Contemplative"],
            "style_elements": ["Thuluth script", "Floral illumination", "Gold leaf accents"],
            "technique_markers": ["Calligraphic precision", "Letter proportion rules", "Tezhip border"],
            "cultural_references": ["Islamic calligraphy", "Quran illumination", "Ottoman tradition"]
        }, "critic_insights": ["Correct Thuluth proportions in second round", "Beautiful tezhip border work"],
        "media_type": "image", "created_at": time.time() - 1400,
    },

    # 17: 水彩抽象 — agent 用户
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}", "mode": "create",
        "intent": "abstract watercolor expressing the feeling of spring rain",
        "tradition": "watercolor", "subject": "spring rain abstract", "user_type": "agent", "user_id": "bot-creative-1",
        "rounds": [{"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c4", "weighted_total": 0.77, "dimension_scores": {"L1": 0.80, "L2": 0.75, "L3": 0.70, "L4": 0.82, "L5": 0.78}, "decision": "accept", "latency_ms": 10000}],
        "final_scores": {"L1": 0.80, "L2": 0.75, "L3": 0.70, "L4": 0.82, "L5": 0.78},
        "final_weighted_total": 0.77, "best_image_url": "", "risk_flags": [],
        "recommendations": [], "total_rounds": 1, "total_latency_ms": 10000, "total_cost_usd": 0.12,
        "candidate_choice_index": 3, "time_to_select_ms": 1000, "downloaded": False,
        "feedback": [{"type": "implicit", "liked": True, "action": "accept", "final_score": 0.77, "rounds_used": 1, "total_cost_usd": 0.12}],
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.78/0.82, "avg_score": 0.77, "risk_level": 0.0,
            "cultural_depth": 0.70, "dimension_variance": 0.042, "l4_emphasis": 0.82/0.82, "generation_efficiency": 0.67,
            "emotional_tone": ["Fresh", "Gentle", "Seasonal"], "style_elements": ["Wet-on-wet", "Color blooms", "Abstract composition"],
            "technique_markers": ["Water flow control", "Color diffusion", "Spontaneous marks"],
            "cultural_references": ["Abstract expressionism", "Watercolor tradition"]
        }, "critic_insights": ["Effective use of wet-on-wet for rain atmosphere"],
        "media_type": "image", "created_at": time.time() - 1200,
    },

    # 18: 写意 — 第四个赛博朋克融合（聚类确认）
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}", "mode": "create",
        "intent": "ancient Chinese scholar sitting in a holographic garden, ink wash + AR overlays",
        "tradition": "chinese_xieyi", "subject": "scholar in holographic garden", "user_type": "human", "user_id": "vr-artist-zhao",
        "rounds": [{"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c2", "weighted_total": 0.76, "dimension_scores": {"L1": 0.80, "L2": 0.72, "L3": 0.70, "L4": 0.82, "L5": 0.76}, "decision": "accept", "latency_ms": 13000}],
        "final_scores": {"L1": 0.80, "L2": 0.72, "L3": 0.70, "L4": 0.82, "L5": 0.76},
        "final_weighted_total": 0.76, "best_image_url": "", "risk_flags": [],
        "recommendations": [], "total_rounds": 1, "total_latency_ms": 13000, "total_cost_usd": 0.12,
        "candidate_choice_index": 1, "time_to_select_ms": 6000, "downloaded": True,
        "feedback": [{"type": "explicit", "liked": True, "comment": "This AR+ink wash fusion is a whole new aesthetic. The holographic garden feels like a natural extension of 文人画.", "action": "accept", "final_score": 0.76, "rounds_used": 1, "total_cost_usd": 0.12}],
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.76/0.82, "avg_score": 0.76, "risk_level": 0.0,
            "cultural_depth": 0.70, "dimension_variance": 0.045, "l4_emphasis": 0.82/0.82, "generation_efficiency": 0.67,
            "emotional_tone": ["Contemplative", "Futuristic-traditional", "Scholarly"],
            "style_elements": ["Ink wash (水墨)", "AR holographic overlay", "Scholar garden motif"],
            "technique_markers": ["Digital-traditional blend", "Transparency layers", "Ink texture + digital light"],
            "cultural_references": ["文人画", "Scholar's garden (文人园林)", "当代水墨", "AR art"]
        }, "critic_insights": ["Innovative fusion of 文人画 and AR", "Maintains scholarly contemplative mood"],
        "media_type": "image", "created_at": time.time() - 1000,
    },

    # 19: 西方学院派 — 三轮迭代，最终满意
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}", "mode": "create",
        "intent": "Renaissance-style portrait in the manner of Vermeer, pearl earring, soft window light",
        "tradition": "western_academic", "subject": "Vermeer-style portrait", "user_type": "human", "user_id": "painter-sophie",
        "rounds": [
            {"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c1", "weighted_total": 0.65, "dimension_scores": {"L1": 0.70, "L2": 0.60, "L3": 0.68, "L4": 0.62, "L5": 0.58}, "decision": "rerun", "latency_ms": 13000},
            {"round_num": 1, "candidates_generated": 4, "best_candidate_id": "c3", "weighted_total": 0.78, "dimension_scores": {"L1": 0.82, "L2": 0.75, "L3": 0.80, "L4": 0.78, "L5": 0.72}, "decision": "rerun", "latency_ms": 12000},
            {"round_num": 2, "candidates_generated": 4, "best_candidate_id": "c4", "weighted_total": 0.86, "dimension_scores": {"L1": 0.88, "L2": 0.85, "L3": 0.87, "L4": 0.85, "L5": 0.82}, "decision": "accept", "latency_ms": 11500},
        ],
        "final_scores": {"L1": 0.88, "L2": 0.85, "L3": 0.87, "L4": 0.85, "L5": 0.82},
        "final_weighted_total": 0.86, "best_image_url": "", "risk_flags": [],
        "recommendations": [], "total_rounds": 3, "total_latency_ms": 36500, "total_cost_usd": 0.40,
        "candidate_choice_index": 3, "time_to_select_ms": 20000, "downloaded": True,
        "feedback": [{"type": "explicit", "liked": True, "comment": "Third round nailed the Vermeer lighting. The soft diffused window light is perfect. Worth the extra rounds.", "action": "accept", "final_score": 0.86, "rounds_used": 3, "total_cost_usd": 0.40}],
        "cultural_features": {
            "tradition_specificity": 0.8, "l5_emphasis": 0.82/0.88, "avg_score": 0.854, "risk_level": 0.0,
            "cultural_depth": 0.87, "dimension_variance": 0.022, "l4_emphasis": 0.85/0.88, "generation_efficiency": 0.0,
            "emotional_tone": ["Intimate", "Luminous", "Timeless"],
            "style_elements": ["Vermeer lighting", "Pearl luminescence", "Window light diffusion"],
            "technique_markers": ["Pointillé highlights", "Glazing technique", "Camera obscura composition"],
            "cultural_references": ["Vermeer", "Dutch Golden Age", "Light painting tradition"]
        }, "critic_insights": ["Exceptional Vermeer-style lighting", "Pearl rendering quality is outstanding"],
        "media_type": "image", "created_at": time.time() - 800,
    },

    # 20: default 传统 — 用户不选特定传统
    {
        "session_id": f"usr-{uuid.uuid4().hex[:12]}", "mode": "create",
        "intent": "a dreamy fantasy landscape with floating islands and waterfalls",
        "tradition": "default", "subject": "fantasy floating islands", "user_type": "human", "user_id": "casual-user-alex",
        "rounds": [{"round_num": 0, "candidates_generated": 4, "best_candidate_id": "c1", "weighted_total": 0.73, "dimension_scores": {"L1": 0.78, "L2": 0.72, "L3": 0.60, "L4": 0.75, "L5": 0.70}, "decision": "accept", "latency_ms": 11000}],
        "final_scores": {"L1": 0.78, "L2": 0.72, "L3": 0.60, "L4": 0.75, "L5": 0.70},
        "final_weighted_total": 0.73, "best_image_url": "", "risk_flags": [],
        "recommendations": [], "total_rounds": 1, "total_latency_ms": 11000, "total_cost_usd": 0.12,
        "candidate_choice_index": 0, "time_to_select_ms": 4000, "downloaded": True,
        "feedback": [{"type": "implicit", "liked": True, "action": "accept", "final_score": 0.73, "rounds_used": 1, "total_cost_usd": 0.12}],
        "cultural_features": {
            "tradition_specificity": 0.3, "l5_emphasis": 0.70/0.78, "avg_score": 0.71, "risk_level": 0.0,
            "cultural_depth": 0.60, "dimension_variance": 0.060, "l4_emphasis": 0.75/0.78, "generation_efficiency": 0.67,
            "emotional_tone": ["Dreamy", "Fantastical", "Whimsical"],
            "style_elements": ["Fantasy landscape", "Floating islands", "Atmospheric depth"],
            "technique_markers": ["Digital painting style", "Atmospheric perspective", "Color gradients"],
            "cultural_references": ["Fantasy art genre", "Digital concept art"]
        }, "critic_insights": ["Good atmospheric quality", "Fantasy genre well executed"],
        "media_type": "image", "created_at": time.time() - 600,
    },
]


def main():
    """Append 20 realistic sessions and sync feedback."""
    import sys
    sys.path.insert(0, ".")

    from pathlib import Path

    sessions_path = Path("app/prototype/data/sessions.jsonl")
    before_count = sum(1 for _ in open(sessions_path)) if sessions_path.exists() else 0
    print(f"Sessions before: {before_count}")

    # Append raw JSONL (SessionStore.append expects SessionDigest objects)
    with open(sessions_path, "a", encoding="utf-8") as f:
        for sess in SESSIONS:
            f.write(json.dumps(sess, ensure_ascii=False) + "\n")

    after_count = sum(1 for _ in open(sessions_path))
    print(f"Sessions after: {after_count} (+{after_count - before_count})")

    # Re-init store singleton to pick up new data
    from app.prototype.session.store import SessionStore
    SessionStore._instance = None
    from app.prototype.feedback.feedback_store import FeedbackStore
    fb_store = FeedbackStore.get()

    # Sync feedback from the new sessions
    synced = fb_store.sync_from_sessions()
    print(f"Feedback synced: {synced} new records")

    fb_stats = fb_store.get_stats()
    print(f"Feedback total: {fb_stats}")

    print("\n=== Session Summaries ===")
    for i, s in enumerate(SESSIONS, 1):
        liked = any(f.get("liked") for f in s.get("feedback", []))
        comment = next((f.get("comment", "") for f in s.get("feedback", []) if f.get("comment")), "")
        print(f"  {i:2d}. [{s['tradition']:20s}] score={s['final_weighted_total']:.2f} "
              f"rounds={s['total_rounds']} {'👍' if liked else '👎'} "
              f"{'📥' if s.get('downloaded') else '  '} "
              f"{s['subject'][:30]}")
        if comment:
            print(f"      💬 {comment[:80]}{'...' if len(comment) > 80 else ''}")

    print(f"\nDone! {after_count - before_count} sessions added.")


if __name__ == "__main__":
    main()
