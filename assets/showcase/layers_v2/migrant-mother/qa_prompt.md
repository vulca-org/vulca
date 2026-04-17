    # QA Review Task — migrant-mother

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `historical_bw_photo`
    - Layers produced: 27
    - Status: `ok` (4/4 detected)

    ## Layers
    - z= 0 **background** (background)
- z=46 **child_left__cloth** (subject.person[1].cloth)
- z=46 **mother__cloth** (subject.person[0].cloth)
- z=46 **child_right__cloth** (subject.person[2].cloth)
- z=48 **mother__neck** (subject.person[0].neck)
- z=48 **child_right__neck** (subject.person[2].neck)
- z=50 **child_left** (subject.person[1])
- z=50 **mother** (subject.person[0])
- z=50 **child_right** (subject.person[2])
- z=52 **child_left__skin** (subject.person[1].skin)
- z=52 **mother__skin** (subject.person[0].skin)
- z=52 **child_right__skin** (subject.person[2].skin)
- z=53 **child_left__hat** (subject.person[1].hat)
- z=54 **child_left__hair** (subject.person[1].hair)
- z=54 **mother__hair** (subject.person[0].hair)
- z=54 **child_right__hair** (subject.person[2].hair)
- z=56 **child_left__ears** (subject.person[1].ears)
- z=56 **mother__ears** (subject.person[0].ears)
- z=56 **child_right__ears** (subject.person[2].ears)
- z=58 **mother__eyebrows** (subject.person[0].eyebrows)
- z=58 **child_right__eyebrows** (subject.person[2].eyebrows)
- z=60 **mother__nose** (subject.person[0].nose)
- z=60 **child_right__nose** (subject.person[2].nose)
- z=62 **mother__lips** (subject.person[0].lips)
- z=62 **mother__eyes** (subject.person[0].eyes)
- z=62 **child_right__lips** (subject.person[2].lips)
- z=62 **child_right__eyes** (subject.person[2].eyes)

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
