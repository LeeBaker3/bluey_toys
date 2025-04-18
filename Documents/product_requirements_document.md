# 🧸 Bluey Toys Affiliate Website – Product Requirements Document (PRD)

## 1. Overview

A dynamic, one-page website that showcases toys related to the children’s TV show **Bluey**, using the Amazon Product Advertising API. The site supports multiple regions and helps users discover relevant products using filtering, search, and geolocation. It monetizes via the Amazon Associates program with affiliate links.

---

## 2. Goals

- Provide an engaging, playful experience for users looking for Bluey-themed toys.
- Display affiliate links from multiple Amazon marketplaces (US, UK, AU, CA, NZ).
- Support both dynamic filtering and free-text search.
- Refresh data daily and allow manual refreshes.
- Track usage via Google Analytics and social media ad platforms.
- Optimize for SEO and mobile responsiveness.

---

## 3. Key Features

### 🌍 Multi-Region Support

- Support for Amazon US, UK, Australia, Canada, and New Zealand.
- Automatically detect user's region via IP.
- Allow manual region selection override.

### 🎁 Product Discovery

- Use Amazon Associate API to fetch toys related to Bluey.
- Product list refreshes daily (automated job).
- Admin-level manual refresh capability.

### 🔍 Search & Filter

- Filter by dynamically-pulled Amazon categories (configurable).
- Free-text search (e.g., "Bluey campervan").

### 📱 UI/UX Design

- Playful and fun interface using the Bluey color palette (sky blue, orange, cream).
- Responsive/mobile-first design.
- Simple one-page scroll layout.

### 💼 Affiliate Integration

- All products link to regional Amazon affiliate URLs.
- Visible affiliate disclosure banner or footer.

### 📈 SEO & Analytics

- SEO-optimized HTML tags, meta descriptions, and structure.
- Tracking integration for:
  - Google Analytics
  - Facebook Pixel
  - Instagram Ad Tracking

### ⚙️ Admin & Backend

- Scheduled daily update job (e.g., via AWS Lambda or cron).
- Secure endpoint or interface for manual refresh.
- Logging for API requests and errors.

---

## 4. Technical Requirements

### Frontend

- Framework: React (Next.js) or Vue.js
- Styling: TailwindCSS or SCSS
- Localization: Region-aware frontend via IP detection + manual selector

### Backend

- Language: Python (FastAPI / Flask)
- Hosting: AWS (S3 + Lambda or EC2 + RDS setup)
- API: Amazon Product Advertising API

### Database

- Store configuration, logs, refresh times
- Options: PostgreSQL (via RDS), DynamoDB (if serverless)

---

## 5. Non-Functional Requirements

| Requirement   | Description                                      |
|---------------|--------------------------------------------------|
| Performance   | Fast loading (especially on mobile)              |
| Scalability   | Handle traffic spikes (e.g., holidays)           |
| Security      | Protect API keys, validate input, log activity   |
| Accessibility | WCAG 2.1 compliance where feasible               |
| Compliance    | GDPR, Cookie notice, Affiliate disclosure        |

---

## 6. Milestones

| Phase        | Description                                     |
|--------------|-------------------------------------------------|
| Planning     | Finalize architecture and design                |
| Design       | Mockups using Bluey theme and responsive layout |
| Development  | Build frontend, backend, API, and admin tools   |
| Testing      | Cross-browser, region detection, product feeds  |
| Launch       | Deploy site, configure tracking & SEO, promote  |