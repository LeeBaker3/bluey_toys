# Project Plan: Bluey Toys Affiliate Website

**Phase 1: Setup & Configuration (Week 1)**

1.  **Project Initialization:**
    *   Set up Git repository.
    *   Initialize Frontend project (Next.js/React).
    *   Initialize Backend project (Python/FastAPI).
    *   Configure development environments (linters, formatters, dependencies).
2.  **Credentials & Accounts:**
    *   Obtain Amazon Product Advertising API keys.
    *   Obtain Amazon Associates IDs for US, UK, AU, CA, NZ.
    *   Set up Google Analytics, Facebook Pixel, Instagram Ad Tracking accounts.
3.  **Infrastructure Setup (Initial):**
    *   Set up basic AWS resources (e.g., IAM user, S3 bucket for planning). Decide on final architecture (Lambda vs. EC2, RDS vs. DynamoDB).

**Phase 2: Backend Development (Weeks 2-4)**

1.  **Amazon API Integration:**
    *   Implement service to fetch Bluey products using the Amazon API.
    *   Handle regional API endpoints and credentials.
    *   Implement caching mechanism for product data.
2.  **API Endpoints:**
    *   Create FastAPI application.
    *   Develop `/products` endpoint (with region support).
    *   Develop `/categories` endpoint.
    *   Develop secure `/refresh` endpoint for manual updates.
3.  **Database & Data Handling:**
    *   Design database schema (PostgreSQL or DynamoDB).
    *   Implement logic to store/update product data.
    *   Implement configuration storage.
4.  **Scheduled Job:**
    *   Create script for daily product data refresh.
    *   Configure scheduling (AWS Lambda scheduled event or cron).
5.  **Region Detection:**
    *   Implement IP-based region detection logic or integrate a third-party service.
6.  **Logging:**
    *   Implement logging for API requests, errors, and job execution.

**Phase 3: Frontend Development (Weeks 3-6)**

1.  **UI Foundation:**
    *   Set up Next.js project structure.
    *   Implement base layout using Bluey color palette and TailwindCSS/SCSS.
    *   Ensure responsive/mobile-first design.
2.  **Product Display:**
    *   Create components for product lists and individual product details.
    *   Fetch and display product data from the backend `/products` endpoint.
3.  **Region Handling:**
    *   Integrate backend region detection.
    *   Implement manual region selector UI.
    *   Ensure API calls use the selected region.
4.  **Search & Filter:**
    *   Implement category filtering based on data from `/categories`.
    *   Implement free-text search input and logic.
    *   Update product display based on filters/search.
5.  **Affiliate Integration:**
    *   Generate correct regional Amazon affiliate links.
    *   Add affiliate disclosure banner/footer.
6.  **Analytics & Compliance:**
    *   Integrate Google Analytics, Facebook Pixel, Instagram Ad Tracking snippets.
    *   Implement cookie consent banner.
7.  **SEO:**
    *   Implement dynamic meta tags and necessary SEO optimizations.

**Phase 4: Admin & Testing (Weeks 6-7)**

1.  **Admin Interface:**
    *   Develop a simple, secure way to trigger the `/refresh` endpoint.
    *   Provide access to view logs if necessary.
2.  **Testing:**
    *   Write unit tests for backend logic and frontend components.
    *   Perform integration testing between frontend and backend.
    *   Conduct end-to-end testing covering all key features (product display, filtering, search, region switching, affiliate links, responsiveness).
    *   Perform accessibility checks.
    *   Test tracking script integration.

**Phase 5: Deployment & Launch (Week 8)**

1.  **Infrastructure Finalization:**
    *   Provision final AWS resources (Lambda/EC2, RDS/DynamoDB, CloudFront).
2.  **CI/CD:**
    *   Set up automated build and deployment pipelines.
3.  **Deployment:**
    *   Deploy backend application.
    *   Deploy frontend application.
    *   Configure database and scheduled jobs in the production environment.
4.  **Final Checks:**
    *   Configure DNS and HTTPS.
    *   Perform final smoke testing in production.
    *   Verify analytics tracking.
5.  **Launch:**
    *   Go live.
    *   Begin promotional activities.

**Phase 6: Post-Launch (Ongoing)**

1.  **Monitoring:**
    *   Monitor application performance, errors, and logs.
    *   Monitor AWS costs and API usage.
    *   Track analytics data.
2.  **Maintenance:**
    *   Apply security patches and updates.
    *   Address any bugs found post-launch.
3.  **Iteration:**
    *   Gather user feedback.
    *   Plan and implement future enhancements based on data and feedback.

**Open Questions:**

1.  Final decision on Frontend Framework (React/Next.js vs Vue.js)? (Plan assumes Next.js)
2.  Final decision on Backend Framework (FastAPI vs Flask)? (Plan assumes FastAPI)
3.  Final decision on Database (PostgreSQL vs DynamoDB)? (Plan assumes PostgreSQL)
4.  Are design mockups available, or is design creation part of Phase 3?
5.  Who is responsible for obtaining/managing Amazon API keys and Associates IDs?