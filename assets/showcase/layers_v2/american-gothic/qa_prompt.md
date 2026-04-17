    # QA Review Task — american-gothic

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `american_regionalist_painting`
    - Layers produced: 23
    - Status: `ok` (4/4 detected)

    ## Layers
    - z= 0 **farmhouse** (background)
- z=46 **woman__cloth** (subject.person[0].cloth)
- z=46 **man__cloth** (subject.person[1].cloth)
- z=48 **woman__neck** (subject.person[0].neck)
- z=48 **man__neck** (subject.person[1].neck)
- z=50 **woman** (subject.person[0])
- z=50 **man** (subject.person[1])
- z=50 **man__eye_g** (subject.person[1].eye_g)
- z=52 **woman__skin** (subject.person[0].skin)
- z=52 **man__skin** (subject.person[1].skin)
- z=54 **woman__hair** (subject.person[0].hair)
- z=54 **man__hair** (subject.person[1].hair)
- z=56 **woman__ears** (subject.person[0].ears)
- z=56 **man__ears** (subject.person[1].ears)
- z=58 **woman__eyebrows** (subject.person[0].eyebrows)
- z=58 **man__eyebrows** (subject.person[1].eyebrows)
- z=60 **woman__nose** (subject.person[0].nose)
- z=60 **man__nose** (subject.person[1].nose)
- z=62 **woman__eyes** (subject.person[0].eyes)
- z=62 **woman__lips** (subject.person[0].lips)
- z=62 **man__eyes** (subject.person[1].eyes)
- z=62 **man__lips** (subject.person[1].lips)
- z=80 **pitchfork** (foreground.tool)

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
