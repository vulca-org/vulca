    # QA Review Task — creation-of-adam

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `renaissance_fresco`
    - Layers produced: 10
    - Status: `ok` (5/5 detected)

    ## Layers
    - z= 0 **sky** (background)
- z=10 **green_ground** (background.ground)
- z=45 **red_cloak** (subject.drapery)
- z=46 **adam__cloth** (subject.person[0].cloth)
- z=50 **adam** (subject.person[0])
- z=50 **god_angels_cluster** (subject.person[1])
- z=52 **adam__skin** (subject.person[0].skin)
- z=53 **god_angels_cluster__hat** (subject.person[1].hat)
- z=54 **god_angels_cluster__hair** (subject.person[1].hair)
- z=60 **adam__nose** (subject.person[0].nose)

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
