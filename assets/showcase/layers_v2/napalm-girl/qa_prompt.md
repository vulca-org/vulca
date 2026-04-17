    # QA Review Task — napalm-girl

    You are reviewing a segmentation pipeline output. Look at the contact sheet
    (original image + all extracted layers as transparent PNGs on a checkerboard).

    ## Context
    - Domain: `historical_bw_photo`
    - Layers produced: 25
    - Status: `ok` (10/10 detected)

    ## Layers
    - z= 0 **background** (background)
- z=46 **boy_screaming_left__cloth** (subject.person[0].cloth)
- z=50 **boy_screaming_left** (subject.person[0])
- z=50 **small_boy_behind** (subject.person[1])
- z=50 **soldier_center** (subject.person[2])
- z=50 **girl_center_nude** (subject.person[3])
- z=50 **boy_dirty_clothes** (subject.person[4])
- z=50 **soldier_middle_right** (subject.person[5])
- z=50 **girl_white_shirt** (subject.person[6])
- z=50 **soldier_far_right_1** (subject.person[7])
- z=50 **soldier_far_right_2** (subject.person[8])
- z=50 **boy_screaming_left__eye_g** (subject.person[0].eye_g)
- z=52 **boy_screaming_left__skin** (subject.person[0].skin)
- z=52 **girl_center_nude__skin** (subject.person[3].skin)
- z=52 **soldier_middle_right__skin** (subject.person[5].skin)
- z=52 **soldier_far_right_2__skin** (subject.person[8].skin)
- z=53 **boy_screaming_left__hat** (subject.person[0].hat)
- z=53 **soldier_center__hat** (subject.person[2].hat)
- z=53 **boy_dirty_clothes__hat** (subject.person[4].hat)
- z=53 **soldier_middle_right__hat** (subject.person[5].hat)
- z=53 **soldier_far_right_2__hat** (subject.person[8].hat)
- z=54 **boy_screaming_left__hair** (subject.person[0].hair)
- z=54 **soldier_far_right_2__hair** (subject.person[8].hair)
- z=60 **boy_screaming_left__nose** (subject.person[0].nose)
- z=62 **boy_screaming_left__lips** (subject.person[0].lips)

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
