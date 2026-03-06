# Contributing to VULCA

Thank you for your interest in contributing to VULCA! This guide focuses on the most impactful way to contribute: **adding new cultural traditions**.

## Adding a New Tradition

VULCA evaluates AI-generated art across cultural dimensions using `TRADITION.yaml` files. Each tradition defines evaluation weights, terminology, and cultural taboos.

### Quick Start (5 minutes)

1. **Fork** this repository
2. **Copy** the template:
   ```bash
   cp wenxin-backend/app/prototype/data/traditions/_template.yaml \
      wenxin-backend/app/prototype/data/traditions/your_tradition.yaml
   ```
3. **Edit** the YAML file with your tradition's data
4. **Validate** locally:
   ```bash
   cd wenxin-backend
   python -c "
   from app.prototype.cultural_pipelines.tradition_loader import validate_tradition_yaml
   errors = validate_tradition_yaml('app/prototype/data/traditions/your_tradition.yaml')
   print('PASS' if not errors else errors)
   "
   ```
5. **Submit** a Pull Request

### TRADITION.yaml Structure

```yaml
name: korean_minhwa              # snake_case unique ID
display_name:
  en: "Korean Folk Painting"     # required
  zh: "韩国民画"                  # optional
  ja: "韓国民画"                  # optional

weights:                          # must sum to 1.0
  L1: 0.15                       # Visual Perception
  L2: 0.20                       # Technical Analysis
  L3: 0.25                       # Cultural Context
  L4: 0.15                       # Critical Interpretation
  L5: 0.25                       # Philosophical Aesthetic

terminology:                      # minimum 3 entries
  - term: "chaesaek"
    term_zh: "五方色"
    definition:
      en: "The five-color system (blue, white, red, black, yellow) based on yin-yang cosmology."
    category: technique           # technique|aesthetics|composition|philosophy|material
    l_levels: [L2, L3]
    aliases: ["five cardinal colors"]
    source: "Korean painting tradition"

taboos:                           # minimum 1 entry
  - rule: "Do not apply Japanese ukiyo-e standards to Korean minhwa"
    severity: high                # low|medium|high|critical
    l_levels: [L3, L4]
    explanation: "Korean folk painting has distinct aesthetic values from Japanese woodblock prints."

pipeline:
  variant: default                # default|chinese_xieyi|western_academic
```

### L1-L5 Weight Guidelines

Choose weights that reflect your tradition's evaluative priorities:

| Dimension | What it measures | High weight when... |
|-----------|-----------------|---------------------|
| **L1** Visual Perception | Color, form, spatial layout | Visual precision is paramount (e.g., geometric art) |
| **L2** Technical Analysis | Medium mastery, brushwork, craft | Technical virtuosity defines quality (e.g., gongbi) |
| **L3** Cultural Context | Tradition-specific knowledge, symbolism | Cultural meaning is central (e.g., African traditional) |
| **L4** Critical Interpretation | Meaning-making, narrative | Interpretive depth matters (e.g., Western academic) |
| **L5** Philosophical Aesthetic | Worldview, beauty concept | Philosophical dimension is key (e.g., Chinese xieyi) |

Weights must sum to **1.0**. The CI will reject PRs where they don't.

### Quality Checklist

Before submitting your PR, verify:

- [ ] `name` is unique snake_case (check existing files in `traditions/`)
- [ ] `weights` L1-L5 sum to exactly 1.0
- [ ] At least 3 terminology entries with `term`, `definition`, and `l_levels`
- [ ] At least 1 taboo rule with `rule` and `severity`
- [ ] `definition` is accurate and sourced (cite references where possible)
- [ ] No duplicate terms across existing traditions (check with search)
- [ ] Taboo rules are specific, not generic platitudes

### What Makes a Good Contribution

**Excellent traditions include:**
- Terms with authoritative sources (academic texts, historical documents)
- Taboos that catch real evaluation mistakes AI systems make
- Weights that reflect genuine evaluative priorities of practitioners
- Multi-language display names (en + at least one other language)

**We will request changes if:**
- Definitions are vague or unsourced
- Taboos are too generic ("don't be insensitive")
- Weights seem arbitrary (explain your reasoning in the PR description)
- Content duplicates an existing tradition

## Other Contributions

### Bug Reports
Open an issue with reproduction steps and expected vs actual behavior.

### Code Contributions
For code changes beyond tradition YAML:
1. Open an issue describing the proposed change
2. Wait for maintainer feedback before implementing
3. Follow existing code style and patterns
4. Include tests for new functionality

### Translation
Help translate `display_name` and `definition` fields in existing traditions to more languages.

## Code of Conduct

Be respectful of all cultural traditions. VULCA exists to celebrate cultural diversity in art, not to rank cultures against each other. Contributions that demean, stereotype, or misrepresent any culture will be rejected.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
