    # QA Review Task — trump-shooting

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `news_photograph_2024`
    - Layers produced: 10
    - Status: `ok` (6/6 detected)

    ## Layers
    - z= 0 **sky_flag** (background)
- z=46 **trump__cloth** (subject.person[0].cloth)
- z=46 **agent_bottom__cloth** (subject.person[3].cloth)
- z=50 **agent_left** (subject.person[1])
- z=50 **trump** (subject.person[0])
- z=50 **agent_right** (subject.person[2])
- z=50 **agent_bottom** (subject.person[3])
- z=52 **trump__skin** (subject.person[0].skin)
- z=54 **trump__hair** (subject.person[0].hair)
- z=80 **stage_railing** (foreground.stage)

    ## Output Format (strict JSON)

    ```json
    {
      "overall": {"quality": "excellent|good|fair|poor", "summary": "..."},
      "layers": [
        {
          "name": "<layer name>",
          "quality": "good|leak|incomplete|wrong|empty",
          "issue": "<if not good, describe briefly>",
          "fix": "<concrete suggestion, e.g. 'tighten bbox right edge', 'raise threshold to 0.3', 'merge with <other layer>'>"
        }
      ],
      "missing_concepts": ["<things in the original that have NO layer>"],
      "recommended_reruns": [
        {"entity": "<name>", "action": "<what to change in plan>"}
      ]
    }
    ```

    ## Quality Rubric
    - **good**: mask cleanly captures entity, no leaks, no holes
    - **leak**: includes pixels from neighboring objects (e.g. hands include sleeve)
    - **incomplete**: misses significant parts of entity (e.g. missed a leg)
    - **wrong**: captured the wrong thing entirely
    - **empty**: mask is nearly blank (<1% pixels)
