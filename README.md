# Technical Demonstration

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/) 
[![Django](https://img.shields.io/badge/Django-5.2-success.svg)](https://www.djangoproject.com/) 
[![HTMX](https://img.shields.io/badge/Frontend-HTMX%20%2B%20Alpine.js-lightblue.svg)](https://htmx.org/) 
[![Docker](https://img.shields.io/badge/Container-Docker-blue.svg)](https://www.docker.com/) 
[![Deploy to Render](https://img.shields.io/badge/Deploy-Render-purple.svg)](https://render.com/deploy)

---

A small Django-based application created as a technical challenge to demonstrate:  
- **Web scraping** from Spain’s official government website ([BOE.es](https://www.boe.es/)).  
- **Storing structured data** into a database.  
- **Displaying results** with a lightweight **HTMX + Alpine.js** frontend.  
- **Simulated AI analysis** of documents (mock, ready for OpenAI integration).  
- **CSV Export** for quick data extraction.  
- **Containerization with Docker** (optimized for Render deployment).

---

## **Features**
- **Web Scraping**: Fetches today's BOE published documents directly from [BOE.es](https://www.boe.es/) and stores them in the database.
- **Document Model**: Stores title, number, date, status, and URL.
- **Dynamic Frontend**:
  - **Search** by document title.
  - **Pagination** (10 items per page).
  - **Dynamic Refresh** without full page reload using **HTMX**.
  - **AI Analysis Modal** powered by Alpine.js (mocked but ready for OpenAI API).
- **CSV Export**: Download all records as CSV.
- **Docker**: Fully containerized and ready for Render deployment.

---

## **Architecture**
```mermaid
flowchart TD
    A[BOE.es Public Website] -->|Scraping| B[Scraper Module]
    B -->|Data| C[(Database)]
    C --> D[Django Backend]
    D -->|HTML + JSON| E[HTMX + Alpine.js Frontend]
    D -->|Optional| F[OpenAI API AI Analysis]

