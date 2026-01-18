# AstraMark AI - Complete Implementation

## Status
- **Backend**: Fully Operational (Enhanced Mode)
- **Frontend**: Built & Ready
- **AI Engine**: Google Gemini 1.5 Flash (Active)
- **Market Data**: SERP API (Mock Fallback Active)
- **Blockchain**: Polygon Amoy (Database Fallback Active)

## Quick Start
Double-click `START_ASTRAMARK.bat` to launch everything.

## Manual Start
1. **Backend**:
   ```bash
   cd backend
   python server_enhanced.py
   # Runs on http://localhost:8000
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm start
   # Runs on http://localhost:3000
   ```

## Key Features
1. **AI Marketing Analysis**: Generates strategies, personas, and revenue models.
2. **Content Generation**: Creates pitch decks (JSON), content calendars, and email sequences.
3. **PDF Export**: Generates professional PDF reports.
4. **Live Market Signals**: Background scanner monitors trends (simulated if no API key).
5. **Blockchain Proof**: Verifies analysis integrity.

## API Keys
To enable live features, add these keys to `backend/.env`:
- `GOOGLE_API_KEY`: Required for AI (Already configured)
- `SERP_API_KEY`: Optional for real market data
- `POLYGON_RPC_URL` & `WALLET_PRIVATE_KEY`: Optional for real blockchain transactions
