    # QA Review Task — trump-mugshot

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `booking_photograph`
    - Layers produced: 9
    - Status: `ok` (2/2 detected)

    ## Layers
    - z= 0 **wall** (background)
- z=46 **trump__cloth** (subject.person[0].cloth)
- z=50 **trump** (subject.person[0])
- z=52 **trump__skin** (subject.person[0].skin)
- z=54 **trump__hair** (subject.person[0].hair)
- z=56 **trump__ears** (subject.person[0].ears)
- z=60 **trump__nose** (subject.person[0].nose)
- z=62 **trump__eyes** (subject.person[0].eyes)
- z=62 **trump__lips** (subject.person[0].lips)

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
