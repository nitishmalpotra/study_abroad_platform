# Study Abroad Platform

A comprehensive web platform designed to help Indian students navigate their study abroad journey, from university selection to education loans and visa guidance.

## Overview

This platform provides students with essential tools and resources for studying abroad, including:
- University and destination exploration
- Education loan EMI calculator
- API-backed live and demo Statement of Purpose (SOP) review experience
- Comprehensive blog with expert guidance
- Lead capture for personalized assistance

## Features

- **Destination Guides**: Detailed information about popular study abroad destinations (USA, UK, Canada, Australia, Germany, Ireland)
- **University Database**: Explore top universities with program details, rankings, and admission requirements
- **EMI Calculator**: Calculate education loan EMIs with adjustable parameters
- **SOP Review Tool**: Live backend SOP review plus deterministic demo mode
- **Resource Center**: Downloadable guides, checklists, and templates
- **Blog**: Expert articles on loans, visas, test prep, scholarships, and more
- **Lead Management**: Lead capture submitted to the FastAPI backend and stored in Neon Postgres

## Tech Stack

- **Framework**: Next.js with React 18 and TypeScript
- **Styling**: Tailwind CSS
- **Routing**: Next.js App Router
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Backend**: FastAPI (`apps/api`) with Neon Postgres for tool records and lead capture
- **Type Checking**: TypeScript 5.5

## Prerequisites

Before you begin, ensure you have the following installed:
- Node.js 18.x or higher
- npm 9.x or higher

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:

Create a `.env` file in the root directory with the following variable:
```env
NEXT_PUBLIC_STUDY_ABROAD_API_URL=http://localhost:8000
```

`NEXT_PUBLIC_STUDY_ABROAD_API_URL` should point at the FastAPI backend; it is not a secret and must never contain the DeepSeek key. The web app needs no database credentials.

## Database Setup

The frontend has no database of its own. AI tool records and lead capture are stored in Neon Postgres by the FastAPI backend (`apps/api`); see `apps/api/migrations` and run them with `uv run python -m app.persistence.migrations`.

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Building for Production

Build the project:
```bash
npm run test
npm run build
```

The optimized production build is created by Next.js in `.next/`.

## Code Quality

Run TypeScript type checking:
```bash
npm run typecheck
```

Run ESLint:
```bash
npm run lint
```

## Project Structure

```
├── public/               # Static assets
├── src/
│   ├── components/       # React components
│   │   ├── home/        # Homepage-specific components
│   │   └── layout/      # Layout components (Navbar, Footer)
│   ├── context/         # React context providers
│   ├── data/            # Static data files
│   ├── lib/             # Utility libraries and configurations
│   ├── app/             # Next.js App Router entry points
│   ├── screens/         # Reused page-level components
│   └── index.css        # Global styles and Tailwind directives
├── .env                 # Environment variables (create this)
├── package.json         # Project dependencies
├── tailwind.config.js   # Tailwind CSS configuration
├── tsconfig.json        # TypeScript configuration
└── next.config.ts       # Next.js configuration
```

## Key Pages

- `/` - Homepage with hero, journey steps, testimonials, and FAQ
- `/destinations` - List of study abroad destinations
- `/destinations/:country` - Detailed country information
- `/universities` - University database
- `/tools` - Available tools overview
- `/tools/emi-calculator` - Education loan EMI calculator
- `/tools/sop-review` - SOP review service
- `/tools/resources` - Downloadable resources and guides
- `/blog` - Blog listing with category filters and search
- `/blog/:id` - Individual blog post pages

## Lead Capture System

The platform includes a comprehensive lead capture system that triggers at strategic points:
- Tool access (EMI calculator, SOP review)
- Resource downloads
- General inquiries

All leads are submitted to the FastAPI backend (`POST /api/v1/leads`), validated server-side, and stored in the Neon `tool_leads` table. The browser never connects to the database directly.

## Color Scheme

The design uses a custom color palette:
- **Brand**: Deep purple tones for primary UI elements
- **Accent**: Orange tones for CTAs and highlights
- **Gold**: Used for premium features
- **Neutral**: Slate grays for text and backgrounds

## Browser Support

The application supports all modern browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Migration notes

- Routes are now file-based under `src/app`; public URLs are preserved from the Vite app.
- `resources` remains at `/tools/resources`, matching the pre-migration implementation.
- Static assets continue to live in `public/`; `logo.png` remains available at `/logo.png`.
- Lead capture moved from a browser-direct Supabase client to the FastAPI backend (`POST /api/v1/leads` → Neon); the web app no longer needs any database credentials.

## Monorepo note

This package now lives inside the public Study Abroad Platform monorepo. See the root README and `docs/MIGRATION_BLUEPRINT.md` for the current migration plan.
