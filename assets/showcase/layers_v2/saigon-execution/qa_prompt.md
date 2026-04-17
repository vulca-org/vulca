    # QA Review Task — saigon-execution

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `historical_bw_photo`
    - Layers produced: 12
    - Status: `ok` (4/4 detected)

    ## Layers
    - z= 0 **street_buildings** (background)
- z=46 **soldier_left__cloth** (subject.person[0].cloth)
- z=46 **victim__cloth** (subject.person[2].cloth)
- z=48 **victim__neck** (subject.person[2].neck)
- z=50 **soldier_left** (subject.person[0])
- z=50 **executioner** (subject.person[1])
- z=50 **victim** (subject.person[2])
- z=52 **victim__skin** (subject.person[2].skin)
- z=53 **soldier_left__hat** (subject.person[0].hat)
- z=54 **victim__hair** (subject.person[2].hair)
- z=58 **victim__eyebrows** (subject.person[2].eyebrows)
- z=60 **victim__nose** (subject.person[2].nose)

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
