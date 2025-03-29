# Kalshi Trading Assistant

A trading assistant application for Kalshi prediction markets, featuring AI-powered recommendations.

## Project Structure

- **Frontend**: Next.js application (React)
- **Backend**: FastAPI Python API

## Backend API Endpoints

The backend API provides the following endpoints:

### Health Check

```
GET /api/health
```

Returns the health status of the API.

### Market Feed

```
GET /api/feed
```

Returns the latest market data from Kalshi (currently returning stub data).

### Trade Recommendations

```
POST /api/recommendations
```

Generates trade recommendations based on the provided strategy.

Request body:
```json
{
  "strategy": "string"
}
```

### Execute Trade

```
POST /api/execute
```

Executes a trade on Kalshi (currently a stub implementation).

Request body:
```json
{
  "trade_id": "string"
}
```

## Running the Application

### Development

To run the application in development mode:

```bash
# Start both frontend and backend
npm run dev

# Start only the backend
npm run fastapi-dev

# Start only the frontend
npm run next-dev
```

The backend runs on port 8000 by default, and the frontend runs on port 3000. 