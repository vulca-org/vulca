    # QA Review Task — nighthawks

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `american_realism_painting`
    - Layers produced: 11
    - Status: `ok` (7/7 detected)

    ## Layers
    - z= 0 **street_buildings** (background)
- z=45 **diner_glass** (subject.diner.glass)
- z=45 **diner_interior** (subject.diner.interior)
- z=46 **person_solitary__cloth** (subject.person[3].cloth)
- z=50 **person_left_couple_1** (subject.person[0])
- z=50 **person_left_couple_2** (subject.person[1])
- z=50 **person_server** (subject.person[2])
- z=50 **person_solitary** (subject.person[3])
- z=52 **person_left_couple_1__skin** (subject.person[0].skin)
- z=53 **person_left_couple_1__hat** (subject.person[0].hat)
- z=54 **person_left_couple_1__hair** (subject.person[0].hair)

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
