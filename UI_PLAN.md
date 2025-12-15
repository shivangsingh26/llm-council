# LLM Council - Frontend UI Architecture Plan
**Next.js 15 App Router + shadcn/ui + Tailwind CSS**

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Tech Stack & Conventions](#tech-stack--conventions)
3. [Project Structure](#project-structure)
4. [Design System (shadcn/ui)](#design-system-shadcnui)
5. [Pages & Routes (v1 Scope)](#pages--routes-v1-scope)
6. [Component Architecture](#component-architecture)
7. [Server vs Client Components](#server-vs-client-components)
8. [Command Palette](#command-palette)
9. [Implementation Plan](#implementation-plan)

---

## 🏗️ Architecture Overview

### Core Principles
- **Next.js App Router**: Server-first, streaming, RSC
- **shadcn/ui**: Copy-paste components, full ownership
- **Server Components by default**: Client only when interactive
- **TypeScript strict mode**: Type safety throughout
- **Tailwind CSS**: Utility-first styling
- **Progressive enhancement**: Works without JS

### v1 Scope (MVP)
Focus on core functionality:
1. ✅ **Dashboard** - Overview and quick stats
2. ✅ **Research** - Main research interface
3. ✅ **History** - Past research browsing
4. ✅ **Settings** - Configuration and API keys

**Deferred to v2:**
- Compare page (complex state management)
- Analytics page (requires data aggregation)

---

## 🛠️ Tech Stack & Conventions

### Frontend Stack
```json
{
  "framework": "Next.js 15",
  "language": "TypeScript 5.3+",
  "ui": "shadcn/ui (Radix UI primitives)",
  "styling": "Tailwind CSS v4",
  "icons": "lucide-react",
  "forms": "react-hook-form + zod",
  "state": "zustand (client state only)",
  "http": "fetch API (Next.js extended)",
  "charts": "recharts (abstracted interface)"
}
```

### Backend Integration
- **API Layer**: FastAPI (Python SDK wrapper)
- **Communication**: REST API (`/api` routes or external)
- **Real-time**: Server-Sent Events (SSE) for live updates
- **Deployment**: Vercel (frontend) + separate backend

### shadcn/ui Conventions
- **Theme**: Use CSS variables in `globals.css`
- **Components**: Copy into `components/ui/`
- **No npm package**: Components are yours to modify
- **Radix primitives**: Accessible, unstyled base
- **Tailwind classes**: Direct styling, no CSS modules

---

## 📁 Project Structure

```
llm-council-frontend/          # Next.js app (separate from Python SDK)
├── app/                       # App Router
│   ├── layout.tsx            # Root layout (Server Component)
│   ├── page.tsx              # Dashboard page (/)
│   ├── research/
│   │   └── page.tsx          # Research page
│   ├── history/
│   │   └── page.tsx          # History page
│   ├── settings/
│   │   └── page.tsx          # Settings page
│   ├── api/                  # Optional API routes (if needed)
│   │   └── sdk/
│   │       └── route.ts      # Proxy to Python backend
│   └── globals.css           # Tailwind + shadcn theme
│
├── components/
│   ├── ui/                   # shadcn/ui components (copy-paste)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   └── ...
│   ├── layout/               # Layout components
│   │   ├── header.tsx        # (Server Component)
│   │   ├── sidebar.tsx       # (Server Component)
│   │   ├── main-nav.tsx      # (Server Component)
│   │   └── user-nav.tsx      # (Client Component - dropdown)
│   ├── research/             # Research page components
│   │   ├── research-form.tsx         # (Client - form state)
│   │   ├── agent-status-panel.tsx    # (Client - real-time)
│   │   ├── results-display.tsx       # (Server - static results)
│   │   └── analysis-panel.tsx        # (Server - static analysis)
│   ├── dashboard/            # Dashboard components
│   │   ├── stats-cards.tsx   # (Server)
│   │   └── recent-activity.tsx # (Server)
│   ├── history/              # History components
│   │   ├── history-list.tsx  # (Server)
│   │   ├── history-filters.tsx # (Client - filter state)
│   │   └── history-card.tsx  # (Server)
│   ├── settings/             # Settings components
│   │   ├── api-key-form.tsx  # (Client - form)
│   │   └── preferences.tsx   # (Client - toggles)
│   ├── command-palette.tsx   # (Client - Cmd+K)
│   └── providers.tsx         # (Client - context providers)
│
├── lib/
│   ├── sdk-client.ts         # SDK API client (fetch wrapper)
│   ├── utils.ts              # shadcn cn() utility
│   ├── validations.ts        # Zod schemas
│   └── charts/               # Chart abstraction layer
│       ├── index.ts          # Chart interface
│       └── recharts-adapter.ts # Recharts implementation
│
├── hooks/
│   ├── use-research.ts       # Research query hook
│   ├── use-history.ts        # History fetching hook
│   └── use-command-palette.ts # Cmd+K hook
│
├── types/
│   ├── sdk.ts                # SDK response types
│   └── ui.ts                 # UI-specific types
│
├── public/
│   └── ...
│
├── next.config.mjs
├── tailwind.config.ts
├── tsconfig.json
├── components.json           # shadcn/ui config
└── package.json
```

---

## 🎨 Design System (shadcn/ui)

### Theme Configuration (`globals.css`)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* shadcn/ui CSS variables */
    --background: 224 71% 4%;        /* #0a0e27 */
    --foreground: 0 0% 100%;         /* #ffffff */

    --card: 224 50% 10%;             /* #151932 */
    --card-foreground: 0 0% 100%;

    --popover: 224 50% 10%;
    --popover-foreground: 0 0% 100%;

    --primary: 244 63% 70%;          /* #667eea */
    --primary-foreground: 0 0% 100%;

    --secondary: 269 47% 55%;        /* #764ba2 */
    --secondary-foreground: 0 0% 100%;

    --muted: 224 40% 15%;
    --muted-foreground: 0 0% 70%;

    --accent: 244 63% 70%;
    --accent-foreground: 0 0% 100%;

    --destructive: 0 84% 60%;        /* #ef4444 */
    --destructive-foreground: 0 0% 100%;

    --border: 0 0% 100% / 0.1;
    --input: 0 0% 100% / 0.1;
    --ring: 244 63% 70%;

    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}
```

### Typography (Tailwind Config)

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)'],
        mono: ['var(--font-jetbrains-mono)'],
      },
      // shadcn/ui extends colors via CSS variables
    },
  },
  plugins: [require("tailwindcss-animate")],
}
export default config
```

### Component Library (shadcn/ui)

**Install via CLI:**
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input select textarea
npx shadcn-ui@latest add dropdown-menu dialog toast
npx shadcn-ui@latest add table badge avatar
npx shadcn-ui@latest add command  # For Cmd+K palette
```

---

## 🗺️ Pages & Routes (v1 Scope)

### 1. Dashboard (`app/page.tsx`) - Server Component

**Purpose**: Landing page with overview and quick actions

**Features:**
- 4 stat cards (queries, tokens, cost, success rate)
- Recent activity list (last 10 research items)
- Quick action button: "New Research"
- Domain usage breakdown

**Data Fetching:**
```typescript
// app/page.tsx (Server Component)
import { getStats, getRecentActivity } from '@/lib/sdk-client'

export default async function DashboardPage() {
  const stats = await getStats()
  const activity = await getRecentActivity({ limit: 10 })

  return (
    <div className="space-y-8">
      <StatsCards data={stats} />
      <RecentActivity items={activity} />
    </div>
  )
}
```

**Route:** `/`

---

### 2. Research (`app/research/page.tsx`) - Hybrid

**Purpose**: Main interface for running council research

**Features:**
- Input form (query + domain + tokens)
- Real-time agent status indicators
- 3-column results display
- Analysis section (consensus/disagreements)
- Metrics panel
- Save/export actions

**Component Split:**
- **Server Components**: Results display, analysis panel (static after load)
- **Client Components**: Research form, agent status (interactive/real-time)

**Data Flow:**
```typescript
// app/research/page.tsx (Server Component wrapper)
export default function ResearchPage() {
  return (
    <div className="space-y-8">
      {/* Client: Form with state */}
      <ResearchForm />

      {/* Client: Real-time status updates */}
      <AgentStatusPanel />

      {/* Server: Static results after research */}
      <Suspense fallback={<ResultsSkeleton />}>
        <ResultsDisplay />
      </Suspense>

      {/* Server: Analysis */}
      <AnalysisPanel />
    </div>
  )
}
```

**Route:** `/research`

---

### 3. History (`app/history/page.tsx`) - Hybrid

**Purpose**: Browse and manage past research

**Features:**
- Search bar (client-side filtering)
- Filters: domain, date range, status
- Card or table view toggle
- Pagination
- Actions: View details, Delete

**Component Split:**
- **Server**: Fetch initial data, render cards
- **Client**: Search/filter state, view toggle

**Data Fetching with Suspense:**
```typescript
// app/history/page.tsx (Server Component)
import { getHistory } from '@/lib/sdk-client'

export default async function HistoryPage({
  searchParams,
}: {
  searchParams: { page?: string; domain?: string }
}) {
  const page = Number(searchParams.page) || 1
  const domain = searchParams.domain

  const history = await getHistory({ page, domain, limit: 20 })

  return (
    <div className="space-y-6">
      {/* Client: Filters */}
      <HistoryFilters />

      {/* Server: List */}
      <Suspense fallback={<HistoryListSkeleton />}>
        <HistoryList items={history.items} />
      </Suspense>

      {/* Server: Pagination */}
      <Pagination total={history.total} perPage={20} />
    </div>
  )
}
```

**Route:** `/history`

---

### 4. Settings (`app/settings/page.tsx`) - Client Heavy

**Purpose**: Configuration and preferences

**Features:**
- API key management (add/test/delete)
- Default preferences (domain, tokens)
- Theme toggle
- Export data
- About/version info

**Component Split:**
- **Client**: All settings (forms, toggles, modals)
- Uses React Hook Form + Zod validation

**Tabs Structure:**
```typescript
'use client'

export default function SettingsPage() {
  return (
    <Tabs defaultValue="api-keys">
      <TabsList>
        <TabsTrigger value="api-keys">API Keys</TabsTrigger>
        <TabsTrigger value="preferences">Preferences</TabsTrigger>
        <TabsTrigger value="export">Export</TabsTrigger>
      </TabsList>

      <TabsContent value="api-keys">
        <APIKeyManager />
      </TabsContent>

      <TabsContent value="preferences">
        <PreferencesForm />
      </TabsContent>

      <TabsContent value="export">
        <ExportPanel />
      </TabsContent>
    </Tabs>
  )
}
```

**Route:** `/settings`

---

## 🧩 Component Architecture

### Layout Components (Server Components)

#### Root Layout (`app/layout.tsx`)
```typescript
// Server Component
import { Inter, JetBrains_Mono } from 'next/font/google'
import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'
import { CommandPalette } from '@/components/command-palette'
import { Toaster } from '@/components/ui/toaster'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-jetbrains-mono' })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body>
        <div className="flex min-h-screen">
          {/* Server Component */}
          <Sidebar />

          <div className="flex-1">
            {/* Server Component */}
            <Header />

            <main className="container mx-auto p-8">
              {children}
            </main>
          </div>
        </div>

        {/* Client Components for interactivity */}
        <CommandPalette />
        <Toaster />
      </body>
    </html>
  )
}
```

#### Header (`components/layout/header.tsx`)
```typescript
// Server Component (mostly static)
import { MainNav } from './main-nav'
import { UserNav } from './user-nav'  // Client for dropdown
import { Search } from './search'      // Client for input

export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur">
      <div className="container flex h-16 items-center justify-between">
        <MainNav />
        <div className="flex items-center gap-4">
          <Search />
          <UserNav />
        </div>
      </div>
    </header>
  )
}
```

#### Sidebar (`components/layout/sidebar.tsx`)
```typescript
// Server Component
import Link from 'next/link'
import { HomeIcon, FlaskIcon, HistoryIcon, SettingsIcon } from 'lucide-react'

export function Sidebar() {
  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Research', href: '/research', icon: FlaskIcon },
    { name: 'History', href: '/history', icon: HistoryIcon },
    { name: 'Settings', href: '/settings', icon: SettingsIcon },
  ]

  return (
    <aside className="w-64 border-r bg-card">
      <div className="flex h-16 items-center px-6">
        <h1 className="text-xl font-bold">🏛️ LLM Council</h1>
      </div>
      <nav className="space-y-1 px-3">
        {navigation.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-accent"
          >
            <item.icon className="h-5 w-5" />
            <span>{item.name}</span>
          </Link>
        ))}
      </nav>
    </aside>
  )
}
```

---

## ⚙️ Server vs Client Components

### Decision Matrix

| Component | Type | Reason |
|-----------|------|--------|
| Root Layout | Server | Static structure |
| Header | Server | Mostly static, minimal interactivity |
| Sidebar | Server | Navigation links (Next.js handles client-side routing) |
| User dropdown | **Client** | Dropdown state |
| Search input | **Client** | Input state |
| Dashboard stats | Server | Static data from API |
| Recent activity | Server | Static list |
| Research form | **Client** | Form state, validation |
| Agent status panel | **Client** | Real-time updates, SSE |
| Results display | Server | Static results after load |
| Analysis panel | Server | Static analysis |
| History list | Server | Server-fetched data |
| History filters | **Client** | Filter state, URL params |
| Settings forms | **Client** | Form state, mutations |
| Command palette | **Client** | Keyboard shortcuts, modal state |
| Charts | **Client** | Interactive visualizations |
| Toasts | **Client** | Notification state |

### Guidelines
- **Default to Server**: Render on server unless interactivity needed
- **Client for**: Forms, real-time updates, state, event handlers
- **Streaming**: Use `<Suspense>` for progressive loading
- **Actions**: Use Server Actions for mutations

---

## 🔍 Command Palette

### Features (Cmd+K)
- **Global shortcut**: Cmd+K (Mac) / Ctrl+K (Windows)
- **Quick navigation**: Jump to any page
- **Recent searches**: Show last 5 queries
- **Actions**: New research, view settings, export data
- **Fuzzy search**: Type to filter

### Implementation

```typescript
'use client'

import { CommandDialog } from '@/components/ui/command'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }
    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        <CommandGroup heading="Pages">
          <CommandItem onSelect={() => router.push('/')}>
            <HomeIcon className="mr-2 h-4 w-4" />
            <span>Dashboard</span>
          </CommandItem>
          <CommandItem onSelect={() => router.push('/research')}>
            <FlaskIcon className="mr-2 h-4 w-4" />
            <span>New Research</span>
          </CommandItem>
          {/* ... */}
        </CommandGroup>

        <CommandGroup heading="Recent">
          {recentSearches.map((search) => (
            <CommandItem key={search.id}>
              <HistoryIcon className="mr-2 h-4 w-4" />
              <span>{search.query}</span>
            </CommandItem>
          ))}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}
```

---

## 📊 Chart Abstraction Layer

### Purpose
- **Flexibility**: Swap chart library without rewriting components
- **Type safety**: Consistent chart interface
- **Future-proof**: Easy to migrate from Recharts to others

### Interface (`lib/charts/index.ts`)

```typescript
export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'area' | 'radar'
  data: any[]
  options?: {
    xKey?: string
    yKey?: string
    colors?: string[]
    legend?: boolean
    tooltip?: boolean
  }
}

export interface ChartAdapter {
  render(config: ChartConfig): React.ReactNode
}

// Factory function
export function createChart(adapter: ChartAdapter) {
  return (config: ChartConfig) => adapter.render(config)
}
```

### Recharts Adapter (`lib/charts/recharts-adapter.ts`)

```typescript
import {
  LineChart,
  BarChart,
  PieChart,
  // ...
} from 'recharts'

export const rechartsAdapter: ChartAdapter = {
  render(config) {
    switch (config.type) {
      case 'line':
        return <LineChart data={config.data} {...config.options} />
      case 'bar':
        return <BarChart data={config.data} {...config.options} />
      // ...
    }
  }
}
```

### Usage in Components

```typescript
'use client'

import { createChart } from '@/lib/charts'
import { rechartsAdapter } from '@/lib/charts/recharts-adapter'

const Chart = createChart(rechartsAdapter)

export function TokenUsageChart({ data }: { data: any[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Token Usage</CardTitle>
      </CardHeader>
      <CardContent>
        <Chart
          type="bar"
          data={data}
          options={{
            xKey: 'agent',
            yKey: 'tokens',
            colors: ['#667eea', '#10a37f', '#8b5cf6'],
          }}
        />
      </CardContent>
    </Card>
  )
}
```

**Future Migration:**
```typescript
// Just swap the adapter
import { chartjsAdapter } from '@/lib/charts/chartjs-adapter'
const Chart = createChart(chartjsAdapter)
// No component changes needed!
```

---

## 🚀 Implementation Plan

### Phase 1: Foundation (Week 1)
**Goal**: Set up Next.js project with shadcn/ui

✅ **Tasks:**
1. Initialize Next.js 15 with App Router
   ```bash
   npx create-next-app@latest llm-council-frontend --typescript --tailwind --app
   ```
2. Configure shadcn/ui
   ```bash
   npx shadcn-ui@latest init
   ```
3. Set up CSS variables theme in `globals.css`
4. Install core components:
   ```bash
   npx shadcn-ui@latest add button card input select textarea
   npx shadcn-ui@latest add command dialog toast table badge
   ```
5. Create root layout with Header + Sidebar
6. Set up routing structure (empty pages)
7. Configure fonts (Inter + JetBrains Mono)

**Deliverable**: Working Next.js app with navigation

---

### Phase 2: Dashboard & Research Pages (Week 2)
**Goal**: Core functionality - view stats and run research

✅ **Tasks:**
1. **SDK Client Layer** (`lib/sdk-client.ts`)
   - Fetch wrapper for Python backend
   - Type definitions for API responses

2. **Dashboard Page**
   - Stats cards (Server Component)
   - Recent activity list (Server Component)
   - "New Research" button → `/research`

3. **Research Page**
   - Research form (Client Component with react-hook-form)
   - Agent status panel (Client Component with SSE)
   - Results display (Server Component)
   - Analysis panel (Server Component)
   - Implement chart abstraction layer

4. **Command Palette**
   - Cmd+K modal
   - Navigation shortcuts
   - Recent searches (from localStorage)

**Deliverable**: Can run research and view results

---

### Phase 3: History & Settings (Week 3)
**Goal**: Complete v1 scope

✅ **Tasks:**
1. **History Page**
   - Server Component for list rendering
   - Client Component for filters
   - Search functionality
   - Pagination
   - View/delete actions

2. **Settings Page**
   - API key management (Client Component)
   - Preferences form (Client Component)
   - Export functionality
   - Theme toggle

3. **Polish**
   - Loading states (`<Suspense>` + skeletons)
   - Error boundaries
   - Toast notifications
   - Empty states

**Deliverable**: Complete v1 application

---

### Phase 4: Backend Integration & Deploy (Week 4)
**Goal**: Connect to Python SDK and deploy

✅ **Tasks:**
1. **Backend API Setup**
   - FastAPI wrapper around Python SDK
   - CORS configuration
   - SSE endpoint for real-time updates

2. **Integration**
   - Connect all frontend API calls to backend
   - Test end-to-end flows
   - Handle error states

3. **Deployment**
   - Deploy frontend to Vercel
   - Deploy backend (Railway/Render/fly.io)
   - Configure environment variables
   - Set up HTTPS

4. **Documentation**
   - User guide
   - Deployment guide
   - Developer docs

**Deliverable**: Production-ready v1

---

## 📚 References & Resources

### Official Documentation
- [Next.js 15 App Router](https://nextjs.org/docs/app)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Radix UI Primitives](https://www.radix-ui.com/)

### Design Inspiration
- [shadcn-admin Template](https://github.com/satnaing/shadcn-admin)
- [Claude.ai Interface](https://claude.ai/)
- [Vercel Dashboard](https://vercel.com/dashboard)

### Architecture Patterns
- [Next.js Server Components Patterns](https://nextjs.org/docs/app/building-your-application/rendering/composition-patterns)
- [React Server Components RFC](https://github.com/reactjs/rfcs/blob/main/text/0188-server-components.md)

---

## ✅ Key Decisions

### Why Next.js App Router over Vite?
- **Server Components**: Reduce client bundle, faster loads
- **Streaming**: Progressive rendering with Suspense
- **Built-in routing**: File-based, no config
- **API routes**: Optional backend proxy
- **Deployment**: Seamless Vercel integration

### Why shadcn/ui over Component Library?
- **Full ownership**: Modify components freely
- **No dependencies**: Copy-paste, no npm bloat
- **Type safe**: TypeScript throughout
- **Accessible**: Radix UI primitives (ARIA compliant)
- **Customizable**: Tailwind classes, not CSS-in-JS

### Why Server Components by Default?
- **Performance**: Less JavaScript to download
- **SEO**: Fully rendered HTML
- **Security**: Sensitive logic stays on server
- **Caching**: Better caching strategies
- **Simplicity**: No useState/useEffect unless needed

### Why Chart Abstraction?
- **Flexibility**: Change library without refactoring
- **Consistency**: Same interface everywhere
- **Testing**: Mock charts easily
- **Bundle**: Swap for lighter alternative if needed

---

## 🎯 v1 Success Criteria

- ✅ Users can run research queries
- ✅ Results from 3 agents displayed clearly
- ✅ Analysis shows consensus/disagreements
- ✅ History browsable and searchable
- ✅ Settings configurable (API keys, defaults)
- ✅ Command palette works (Cmd+K)
- ✅ Responsive (mobile, tablet, desktop)
- ✅ Accessible (keyboard nav, screen readers)
- ✅ Fast (<2s page loads, <100ms interactions)

---

**Last Updated**: 2025-12-15
**Version**: 2.0 (Next.js App Router Edition)
**Status**: Architecture Approved - Ready for Implementation

---

## 📝 Next Steps

1. **Review & Approve**: Confirm architecture decisions
2. **Initialize Project**: Set up Next.js + shadcn/ui
3. **Build Phase 1**: Layout and navigation
4. **Iterate**: Build incrementally, one page at a time

**Ready to start building?** 🚀
