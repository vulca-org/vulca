# VULCA - AI-Native Creation Organism

Create, critique, and evolve cultural art through multi-agent AI pipelines.

## Key Features

- **Multi-Agent Pipeline**: Scout, Draft, Critic, and Queen agents collaborate in real time
- **13 Cultural Traditions**: Chinese Xieyi, Chinese Gongbi, Japanese, Islamic, South Asian, Western Academic, Watercolor, African, Contemporary Art, Photography, Brand Design, UI/UX Design, Default
- **L1-L5 Evaluation**: Five-level cultural understanding assessment (Visual Perception to Philosophical Aesthetic)
- **Node Editor**: Visual pipeline editor for Canvas workflows
- **Open Source**: Apache 2.0 licensed

## Tech Stack

- **Frontend**: React 19 + TypeScript 5.8 + Vite 7.1
- **Styling**: Tailwind CSS 4.1 with Art Professional Design System
- **State**: Zustand 4.4
- **Animation**: Framer Motion 12.23
- **Testing**: Playwright E2E

## Quick Start

```bash
# Install dependencies
npm install --legacy-peer-deps

# Start development server
npm run dev

# Build for production
npm run build

# Run E2E tests
npm run test:e2e
```

## URL Structure

```
/                    - Homepage
/canvas              - Creation + evaluation (core product)
/gallery             - Community gallery
/models              - Model rankings
/model/:id           - Model details
/research            - Methodology, dataset, papers
```

## VULCA Framework

### L1-L5 Evaluation Framework
| Level | Dimension | Description |
|-------|-----------|-------------|
| L1 | Visual Perception | Surface-level visual understanding |
| L2 | Technical Analysis | Mastery of artistic forms and technique |
| L3 | Cultural Context | Historical and cultural understanding |
| L4 | Critical Interpretation | Interpretive depth and reasoning |
| L5 | Philosophical Aesthetic | Deep aesthetic and philosophical insight |

### 13 Cultural Traditions
- **Chinese**: Xieyi (Freehand), Gongbi (Meticulous)
- **East Asian**: Japanese Traditional
- **Western**: Western Academic, Watercolor, Contemporary Art
- **Design**: Brand Design, UI/UX Design, Photography
- **Other**: Islamic Geometric, South Asian, African Traditional, Default

## Deployment

- **Frontend**: Firebase Hosting (vulcaart.art)
- **Backend**: GCP Cloud Run (asia-east1)
- **Database**: Supabase PostgreSQL
- **CI/CD**: GitHub Actions

## License

Apache 2.0

## Links

- GitHub: [vulca-org/vulca](https://github.com/vulca-org/vulca)
- Website: [vulcaart.art](https://vulcaart.art)
