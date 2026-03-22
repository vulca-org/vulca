# Cultural Tradition Guide

Explore cultural traditions, their evaluation criteria, terminology, and taboos.

TRIGGER when: user says "show traditions", "list traditions", "what traditions", "cultural guide", "vulca traditions", or asks about a specific cultural tradition's evaluation criteria.

## Instructions

1. If user wants an overview: call `list_traditions` to show all 13+ traditions with weights
2. If user asks about a specific tradition: call `get_tradition_guide(tradition="...", view="detailed", format="markdown")`
3. Present the guide with:
   - L1-L5 weight distribution and emphasis
   - Key terminology with original language terms
   - Cultural taboos to avoid
   - Evolved weights (if available) showing how the system has learned
4. If user asks about evolution: call `get_evolution_status(tradition="...")`

## Example

User: "Tell me about Islamic geometric art evaluation"

Response flow:
1. Call `get_tradition_guide(tradition="islamic_geometric", view="detailed")`
2. Explain the L1-L5 weights (heavy on L1/L2 technical precision)
3. Share key terminology (tessellation, arabesque, etc.)
4. List taboos (e.g., figurative representation in sacred contexts)
