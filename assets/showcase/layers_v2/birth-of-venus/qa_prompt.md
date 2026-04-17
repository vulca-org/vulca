    # QA Review Task — birth-of-venus

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `renaissance_painting`
    - Layers produced: 9
    - Status: `ok` (6/6 detected)

    ## Layers
    - z= 0 **sea_sky** (background)
- z=10 **trees** (background.trees)
- z=45 **shell** (subject.shell)
- z=50 **wind_figures** (subject.person[0])
- z=50 **venus** (subject.person[1])
- z=50 **flora** (subject.person[2])
- z=52 **wind_figures__skin** (subject.person[0].skin)
- z=53 **wind_figures__hat** (subject.person[0].hat)
- z=54 **wind_figures__hair** (subject.person[0].hair)

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
