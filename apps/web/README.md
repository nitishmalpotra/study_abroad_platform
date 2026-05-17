# Study Abroad Platform

A comprehensive web platform designed to help Indian students navigate their study abroad journey, from university selection to education loans and visa guidance.

## Overview

This platform provides students with essential tools and resources for studying abroad, including:
- University and destination exploration
- Education loan EMI calculator
- Statement of Purpose (SOP) review service
- Comprehensive blog with expert guidance
- Lead capture for personalized assistance

## Features

- **Destination Guides**: Detailed information about popular study abroad destinations (USA, UK, Canada, Australia, Germany, Ireland)
- **University Database**: Explore top universities with program details, rankings, and admission requirements
- **EMI Calculator**: Calculate education loan EMIs with adjustable parameters
- **SOP Review Tool**: Professional review service for statement of purpose documents
- **Resource Center**: Downloadable guides, checklists, and templates
- **Blog**: Expert articles on loans, visas, test prep, scholarships, and more
- **Lead Management**: Integrated lead capture system with Supabase backend

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v7
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Database**: Supabase (PostgreSQL)
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

Create a `.env` file in the root directory with the following variables:
```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Replace the values with your actual Supabase project credentials.

## Database Setup

The project uses Supabase for data persistence. Migration files are located in `supabase/migrations/`:

- `20260214163103_create_tool_leads_table.sql` - Creates the initial tool leads table
- `20260214163845_add_target_intake_to_tool_leads.sql` - Adds target intake field
- `20260214170543_add_target_course_to_tool_leads.sql` - Adds target course field

These migrations will be automatically applied to your Supabase project.

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Building for Production

Build the project:
```bash
npm run build
```

The optimized production build will be created in the `dist/` directory.

Preview the production build locally:
```bash
npm run preview
```

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
│   ├── pages/           # Page components
│   ├── App.tsx          # Main app component with routing
│   ├── index.css        # Global styles and Tailwind directives
│   └── main.tsx         # Application entry point
├── supabase/
│   └── migrations/      # Database migration files
├── .env                 # Environment variables (create this)
├── index.html           # HTML entry point
├── package.json         # Project dependencies
├── tailwind.config.js   # Tailwind CSS configuration
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite configuration
```

## Key Pages

- `/` - Homepage with hero, journey steps, testimonials, and FAQ
- `/destinations` - List of study abroad destinations
- `/destinations/:country` - Detailed country information
- `/universities` - University database
- `/tools` - Available tools overview
- `/tools/emi-calculator` - Education loan EMI calculator
- `/tools/sop-review` - SOP review service
- `/resources` - Downloadable resources and guides
- `/blog` - Blog listing with category filters and search
- `/blog/:id` - Individual blog post pages

## Lead Capture System

The platform includes a comprehensive lead capture system that triggers at strategic points:
- Tool access (EMI calculator, SOP review)
- Resource downloads
- General inquiries

All leads are stored in Supabase with proper validation and Row Level Security (RLS) enabled.

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

## License

This project is proprietary and confidential.

## Support

For questions or issues, please contact the development team.
