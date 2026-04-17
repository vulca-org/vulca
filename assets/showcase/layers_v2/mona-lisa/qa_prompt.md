    # QA Review Task — mona-lisa

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `renaissance_painting`
    - Layers produced: 9
    - Status: `ok` (3/3 detected)

    ## Layers
    - z= 0 **background** (background)
- z=50 **mona_lisa** (subject.person[0])
- z=52 **mona_lisa__skin** (subject.person[0].skin)
- z=54 **mona_lisa__hair** (subject.person[0].hair)
- z=58 **mona_lisa__eyebrows** (subject.person[0].eyebrows)
- z=60 **mona_lisa__nose** (subject.person[0].nose)
- z=62 **mona_lisa__eyes** (subject.person[0].eyes)
- z=62 **mona_lisa__lips** (subject.person[0].lips)
- z=80 **chair_parapet** (foreground.furniture)

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
