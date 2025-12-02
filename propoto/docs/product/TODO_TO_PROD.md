# 🚀 Path to Production: Propoto MVP

This document outlines the remaining tasks required to take the Propoto MVP from a local development environment to a live production release.

## 🏗️ Infrastructure & Deployment

- [ ] **Frontend Deployment (Vercel/Netlify)**
    - [ ] Connect GitHub repo to Vercel.
    - [ ] Configure build settings (`npm run build`).
    - [ ] Set production environment variables (`NEXT_PUBLIC_CONVEX_URL`, `NEXT_PUBLIC_API_URL`).
    - [ ] Configure custom domain (e.g., `app.propoto.com`).

- [ ] **Backend API Deployment (Railway/Render/AWS)**
    - [ ] Dockerize the FastAPI application (create `Dockerfile`).
    - [ ] Set up CI/CD pipeline for auto-deployment.
    - [ ] Configure production environment variables (Secrets).
    - [ ] Set up persistent volume for logs (if not using external logging service).

- [ ] **Database (Convex)**
    - [ ] Promote Convex dev deployment to Production.
    - [ ] Verify schema indexes for performance.
    - [ ] Set up backup/snapshot schedule.

- [ ] **Telegram Bot**
    - [ ] Deploy bot as a background worker or separate service.
    - [ ] Ensure webhook or polling is robust against restarts.

## 🔒 Security & Auth

- [ ] **Authentication**
    - [ ] Verify Clerk/Convex Auth integration is production-ready.
    - [ ] Enforce strict Row Level Security (RLS) on all Convex tables.
    - [ ] Ensure `orgId` isolation is tested (Multi-tenancy check).

- [ ] **API Security**
    - [ ] Rotate `AGENT_SERVICE_KEY` for production.
    - [ ] Review CORS settings (restrict to production domain).
    - [ ] Tune `slowapi` rate limits for production traffic loads.

## 🧪 Testing & Quality Assurance

- [ ] **Automated Testing**
    - [ ] Set up GitHub Actions to run backend tests (`pytest`) on PRs.
    - [ ] Implement basic E2E smoke test for the "Happy Path" (Generate Proposal).

- [ ] **Monitoring & Logging**
    - [ ] Integrate **Sentry** for frontend and backend error tracking.
    - [ ] Set up **PostHog** or **Google Analytics** for user behavior tracking.
    - [ ] Configure structured logging aggregation (e.g., Datadog, or just persistent logs).

## 💎 UX Polish (Post-MVP)

- [ ] **Onboarding Flow**
    - [ ] Create a "Welcome" modal or tour for new users.
    - [ ] Add empty states for Dashboard/History views.

- [ ] **Editor Improvements**
    - [ ] Add "Regenerate Section" button (using AI) in the editor.
    - [ ] Improve mobile responsiveness for the proposal view.

- [ ] **Gamma Integration**
    - [ ] Re-enable Gamma (`ENABLE_GAMMA=true`) when credits are replenished.
    - [ ] Add user-facing error message if Gamma generation fails.

## 📜 Legal & Compliance

- [ ] **Documents**
    - [ ] Draft Terms of Service.
    - [ ] Draft Privacy Policy (especially regarding AI data usage).
    - [ ] Add cookie consent banner if required.

## 🏁 Go-Live Checklist

- [ ] Perform final security audit (dependency vulnerability scan).
- [ ] Load test with concurrent users (simulated).
- [ ] Verify all external API quotas (OpenRouter, Exa, Firecrawl).
- [ ] **LAUNCH!** 🚀
