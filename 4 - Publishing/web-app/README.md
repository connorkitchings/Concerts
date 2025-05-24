# Jam Band Predictions Web Application

This web application provides a modern interface for exploring song predictions for various jam bands including Widespread Panic, Phish, Goose, and Umphrey's McGee. It displays prediction data based on historical performance analytics.

## Architecture

This project uses a modern web application architecture:

- **Backend**: FastAPI Python API server
  - Serves prediction data via RESTful endpoints
  - Loads data from local files
  - Includes robust error handling and type validation

- **Frontend**: React with TypeScript and Material UI
  - Responsive design works on mobile and desktop
  - Interactive charts for data visualization
  - Tab-based navigation for different prediction models

## Getting Started

### Prerequisites

- Python 3.8+ with pip
- Node.js and npm (for frontend development)

### Installation

1. Make the run script executable:
   ```
   chmod +x run.sh
   ```

2. Run the setup command to install dependencies:
   ```
   ./run.sh setup
   ```

### Running the Application

You can run the backend and frontend separately or together:

- Start both services:
  ```
  ./run.sh both
  ```

- Start only the backend:
  ```
  ./run.sh backend
  ```

- Start only the frontend:
  ```
  ./run.sh frontend
  ```

The frontend will be available at http://localhost:3000 and the API at http://localhost:8000.

## API Endpoints

- `GET /api/bands` - List all available bands
- `GET /api/bands/{band_id}` - Get information for a specific band
- `GET /api/bands/{band_id}/next-show` - Get upcoming show information
- `GET /api/predictions/{band_id}/{prediction_type}` - Get predictions for a band

## Deployment

For production deployment, the frontend can be deployed to a static hosting service like Netlify or Vercel, while the backend can be deployed to a service like Heroku, Railway, or a cloud provider like AWS/GCP/Azure.

## Future Enhancements

- User accounts for saving favorite songs
- Song history visualization
- Venue-specific prediction insights
- Integration with streaming services
- Public API for third-party applications
