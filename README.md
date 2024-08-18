

# Trafero

**Trafero** is the best way to navigate public transportation in Lebanon. It offers real-time tracking, estimated time of arrivals (ETAs), and a convenient way to find and chain routes to get you to your destination.

## Features

- **Live Tracking of Vehicles:** Monitor the location of public transportation vehicles in real time.
- **ETAs on Vehicle Arrivals:** Know exactly when your ride will arrive.
- **Find Nearby Routes:** Easily discover public transportation routes close to your location.
- **Chain Routes:** Combine multiple routes to unlock even more possibilities and reach even more destinations.
- **Save Frequent Routes:** Quickly access your most-used routes, locations, or vehicles.
- **Easy to navigate**: Our platform is made with the public in mind, so it's designed to be easy to use and requires very little knowledge in technology.
## Installation Instructions

To set up Trafero locally, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Trafero-App/Trafero.git
   ```
2. **Install Backend Dependencies:**
   Navigate to the backend directory and install the required Python packages.
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. **Start the Backend Server:**
   Run the FastAPI backend.
   ```bash
   uvicorn main:app --reload
   ```
4. **Set Up the Frontend:**
   Navigate to the frontend directory and install the necessary npm packages.
   ```bash
   cd ../frontend
   npm i
   npm run dev
   ```
Alternatively, you could run the `start.bat` batch file, to startup both the backend and the frontend:
* (Alternative to steps 3 and 4) Make sure you're in the **Trafero** directory and run:
```bash
./start.bat
```
   
## Usage

Once everything is set up, you can access the **Trafero** platform via your local development server:

- **Backend:** FastAPI serves the API at `http://localhost:8000`.
- **Frontend:** The React application runs at `http://localhost:3000`.

Use the frontend to interact with the public transportation system, track vehicles in real-time, find routes, and plan your journey across Lebanon.
