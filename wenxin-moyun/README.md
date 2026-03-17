# VULCA - AI-Native Creation Organism

Create, critique, and evolve cultural art through multi-agent AI pipelines.

## Key Features

- **Multi-Agent Pipeline**: Scout, Draft, Critic, and Queen agents collaborate in real time
- **8 Cultural Traditions**: Chinese, Japanese, Islamic, South Asian, Classical, Contemporary, Latin American, African
- **47-Dimension Evaluation**: Comprehensive cultural understanding assessment
- **Node Editor**: Visual pipeline editor with 30 node types
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

### 6D Core Dimensions
| Dimension | Description |
|-----------|-------------|
| Creativity | Originality and imagination |
| Technique | Mastery of artistic forms |
| Emotion | Emotional expression and resonance |
| Context | Historical and cultural understanding |
| Innovation | Breaking traditional boundaries |
| Impact | Social influence potential |

### 8 Cultural Perspectives
- **Eastern**: Chinese, Japanese, Islamic, South Asian
- **Western**: Classical, Contemporary, Latin American
- **Universal**: African

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
