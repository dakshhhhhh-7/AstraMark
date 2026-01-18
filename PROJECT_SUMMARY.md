# AstraMark AI - Project Summary & Functional Overview

## 🚀 Project Overview
**AstraMark** is an advanced, production-grade **AI Marketing Intelligence Platform**. It functions as an autonomous "CMO-in-a-Box," allowsing users to input basic business details and receive a comprehensive, data-backed marketing strategy, financial projections, and execution-ready content assets in seconds.

The system is built on a modern **FastAPI + React** architecture and leverages **Google's Gemini 2.0 Flash** model for high-speed, intelligent reasoning.

---

## 🌟 Key Functionalities

### 1. 🧠 Core AI Intelligence Engine
- **Automated Strategy Generation**: transform simple inputs (Business Type, Budget, Goals) into deep strategic insights.
- **Market Analysis**: Generates detailed Market Size, Growth Rates, Entry Barriers, and SWOT Analysis.
- **User Persona Creation**: Identifies 3 distinct target avatars with demographics, psychographics, and pain points.
- **Revenue Modeling**: AI-predicted Min/Max revenue projections with growth timelines.

### 2. 📊 Interactive Dashboard (Frontend)
- **Visual Analytics**: Professional UI with progress bars for Confidence, Virality, and Retention scores.
- **Strategy Tabs**: Detailed breakdowns for SEO, Content Marketing, Paid Ads, and Social Media channels.
- **Live Ad Preview**: Generates mockups of what social media ads would look like for the specific business.
- **Actionable Insights**: Highlights the "Biggest Opportunity," "Biggest Risk," and immediate "Next Best Action."

### 3. 📝 Content Generation Suite
- **Pitch Deck Generator**: Creates a structure for a 10-slide investor pitch deck based on the analysis.
- **Content Calendar**: Generates a 4-week, day-by-day posting schedule across multiple platforms.
- **Email Sequences**: Writes a 5-email "Onboarding" or "Sales" drip campaign tailored to the user personas.

### 4. 📄 Reporting & Export
- **PDF Report Generation**: Users can download a verified, professional PDF report of their entire strategy.
- **Exportable Assets**: All generated content (calendars, decks) is structured for easy export.

### 5. 🌐 Advanced Features (Background Services)
- **Live Market Scanner**: A background service that periodically scans for "Market Signals" (e.g., CPC changes, competitor moves).
- **Blockchain Verification**: Times-stamps every analysis on the **Polygon Blockchain** (with Database fallback) to prove the authenticity and timing of the insights. Competitor monitoring integration.

---

## 🛠️ Technical Architecture

### **Frontend**
- **Framework**: React.js (Create React App)
- **Styling**: Tailwind CSS + Shadcn UI (Components)
- **State Management**: React Hooks (useState, useEffect)
- **API Communication**: Axios

### **Backend**
- **Framework**: FastAPI (Python)
- **Database**: MongoDB (Motor Async Client) - *Falls back to In-Memory if Mongo is offline*
- **AI Engine**: `google-generativeai` (Gemini 2.0 Flash) with **Tenacity** for robust rate-limit handling.
- **PDF Engine**: `reportlab` for dynamic PDF generation.
- **Blockchain**: `web3.py` for Polygon interaction.
- **Scheduler**: `APScheduler` for background market scanning tasks.

---

## 🔄 Project Flow
1. **Input**: User submits business data via Frontend.
2. **Process**: 
   - Backend saves profile.
   - AI constructs a specialized prompt and queries Gemini 2.0.
   - Scanner Service checks for live signals.
3. **Output**: comprehensive JSON analysis is returned.
4. **Action**: User interacts with the dashboard to generate further assets (PDFs, Decks, Calendars), triggering specific sub-endpoints.

---

## 📂 Key File Structure
- `backend/server_enhanced.py`: Main API application & AI logic.
- `backend/content_service.py`: Dedicated service for generating Decks, Calendars, & Emails.
- `backend/pdf_service.py`: PDF generation engine.
- `frontend/src/components/AnalysisDashboard.jsx`: Main UI for displaying results.
- `frontend/src/components/BusinessInputForm.jsx`: User input interface.

---

## 🚀 How to Run
We have simplified the launch process to a single script:
1. Navigate to the project root.
2. Double-click **`START_ASTRAMARK.bat`**.
   - This launches both the **Python Backend** (Port 8000) and **React Frontend** (Port 3000) automatically.
