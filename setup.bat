cd backend
mkdir routes
mkdir user_data
cd user_data
mkdir drivers_licenses
mkdir vehicle_registrations
cd ..
pip install -r requirements.txt
cd ..
cd trafero_data
python create_db_tables.py
python create_test_data.py
copy ".env1" "../frontend/.env"
copy ".env" "../backend/.env"
cd routes
copy "1bus_15_1.geojson" "../../backend/routes/1bus_15_1.geojson"
copy "2bus_15_2.geojson" "../../backend/routes/2bus_15_2.geojson"
copy "3beirut_saida_1.geojson" "../../backend/routes/3beirut_saida_1.geojson"
copy "4beirut_saida_2.geojson" "../../backend/routes/4beirut_saida_2.geojson"
copy "5van_4_1.geojson" "../../backend/routes/5van_4_1.geojson"
copy "6van_4_2.geojson" "../../backend/routes/6van_4_2.geojson"
copy "7van_sea_road_1.geojson" "../../backend/routes/7van_sea_road_1.geojson"
copy "8van_sea_road_2.geojson" "../../backend/routes/8van_sea_road_2.geojson"
copy "9bus_2_1.geojson" "../../backend/routes/9bus_2_1.geojson"
copy "10bus_2_2.geojson" "../../backend/routes/10bus_2_2.geojson"
copy "11van_10_1.geojson" "../../backend/routes/11van_10_1.geojson"
copy "12van_10_2.geojson" "../../backend/routes/12van_10_2.geojson"
copy "13bus_24_1.geojson" "../../backend/routes/13bus_24_1.geojson"
copy "14bus_24_2.geojson" "../../backend/routes/14bus_24_2.geojson"
cd ..
cd ..
cd frontend
npm i
cd ..

