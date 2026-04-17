    # QA Review Task — the-scream

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `expressionist_painting`
    - Layers produced: 4
    - Status: `ok` (4/4 detected)

    ## Layers
    - z= 0 **sky_water** (background)
- z=45 **bridge** (subject.bridge)
- z=50 **background_figures** (subject.person[1])
- z=50 **screaming_figure** (subject.person[0])

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
