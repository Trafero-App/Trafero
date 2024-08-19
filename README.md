

# Trafero

**Trafero** is the best way to navigate public transportation in Lebanon. It offers real-time tracking, estimated time of arrivals (ETAs), and a convenient way to find and chain routes to get you to your destination.

## Motivation

We believe that navigating public transportation should be seamless, efficient, and stress-free. Our mission is to address the longstanding challenges faced by commuters and bus drivers in Lebanon by providing a cutting-edge solution that enhances the public transportation experience for everyone.

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

2. **Set Up the Data:**
You should have received a `Trafero.zip` file from the WIE team. Please unzip the file, and add the folder `trafero_data` to the `Trafero` directory. If you run:
	```bash
	ls
	```
	You should see:
	```bash
	d----- 8/20/2024 12:18 AM backend
	d----- 8/20/2024 12:15 AM frontend
	d----- 8/19/2024 11:59 PM trafero_data
	```

	These 3 directories. None of them should be contained within the other. Note that you might have more directories (if you're running a virtual environment for example).
Make sure you are in the root `Trafero` directory and run:
	```bash
	./setup.bat
	```
This should add necessary files, and directories to the project. It should also install dependencies and populate the database with tables and test data.
   
3. **Start the Backend Server:**
   Run the FastAPI backend.
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
4. **Set Up the Frontend:**
   In another terminal, navigate to the frontend directory and install the necessary npm packages.
   ```bash
   cd frontend
   npm i
   npm run dev
   ```
## Usage

Once everything is set up, you can access the **Trafero** platform via your local development server:

- **Backend:** FastAPI serves the API at `http://localhost:8000`.
- **Frontend:** The React application runs at `http://localhost:3000`.

Use the frontend to interact with the public transportation system, track vehicles in real-time, find routes, and plan your journey across Lebanon.
