# VULCA - Cultural AI Evaluation Platform

**VULCA** (Visually-grounded Understanding and Learning for Cultural Aesthetics) is a comprehensive 47-dimension evaluation framework for assessing AI models' cultural and artistic understanding across 8 cultural perspectives.

## Key Features

- **47-Dimension Evaluation**: Comprehensive framework covering creativity, technique, emotion, context, innovation, and impact
- **8 Cultural Perspectives**: Eastern (Chinese, Japanese, Islamic, South Asian) + Western (Classical, Contemporary, Latin American) + Universal (African)
- **Reproducible Benchmarking**: Version-controlled evaluations with BibTeX citation support
- **Enterprise Reports**: Detailed diagnostic reports for model selection and release decisions
- **Public Demo**: Free access to leaderboards, VULCA demo, and cross-cultural exhibitions

## Tech Stack

- **Frontend**: React 19 + TypeScript 5.8 + Vite 7.1
- **Styling**: Tailwind CSS 4.1 with iOS Design System
- **State**: Zustand 4.4
- **Charts**: Recharts 3.1
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

## Project Structure

```
src/
├── components/
│   ├── ios/           # iOS Design System components
│   ├── vulca/         # VULCA evaluation components
│   ├── report/        # Report generation components
│   └── common/        # Shared components
├── pages/
│   ├── HomePage.tsx           # Marketing landing
│   ├── LeaderboardPage.tsx    # Model rankings
│   ├── ModelDetailPage.tsx    # Model details + report
│   ├── vulca/                 # VULCA demo pages
│   ├── solutions/             # Solution pages
│   └── exhibitions/           # Cross-cultural exhibitions
├── hooks/             # Custom React hooks
├── services/          # API services
├── utils/             # Utilities
└── types/             # TypeScript definitions
```

## URL Structure

```
/                    - Marketing homepage
/product             - Product overview
/solutions/*         - Solution pages (AI Labs, Research, Museums)
/customers           - Customer cases
/pricing             - Pricing tiers
/trust               - Trust & Security
/demo                - Book a demo

/models              - Public leaderboard
/model/:id           - Model details
/model/:id/report    - Evaluation report
/vulca               - VULCA demo
/exhibitions         - Cross-cultural evidence

/methodology         - Framework documentation
/dataset             - Dataset access
/papers              - Academic papers
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

- **Frontend**: GCP Cloud Storage (static hosting)
- **Backend**: GCP Cloud Run
- **Database**: Cloud SQL (PostgreSQL)
- **CI/CD**: GitHub Actions

## License

MIT

## Contact

- GitHub: [EMNLP2025-VULCA](https://github.com/vulca-org/vulca)
- Email: hello@vulca.ai
