import psycopg2
import os 
from dotenv import load_dotenv, find_dotenv

def recreate_tables():
    load_dotenv(find_dotenv())

    conn = psycopg2.connect(database=os.getenv("db_name"),
                            user=os.getenv("db_user"),
                            host= os.getenv("db_host"),
                            password = os.getenv("db_password"),
                            port = int(os.getenv("db_port"))
                            )

    cur = conn.cursor()

    cur.execute(""" 
                    DROP TABLE IF EXISTS feedback;
                    DROP TABLE IF EXISTS passenger;
                    DROP TABLE IF EXISTS vehicle_location;
                    DROP TABLE IF EXISTS vehicle;
                    DROP TABLE IF EXISTS waypoint;
                    DROP TABLE IF EXISTS route;
                
                    CREATE TABLE passenger (id SERIAL PRIMARY KEY,
                                            user_name VARCHAR(255) NOT NULL UNIQUE,
                                            password TEXT NOT NULL,
                                            first_name VARCHAR(255) NOT NULL,
                                            last_name VARCHAR(255) NOT NULL,
                                            phone_number VARCHAR(20) NOT NULL UNIQUE
                                            );
                
                    CREATE TABLE route (id SERIAL PRIMARY KEY,
                                        file_name VARCHAR(30) NOT NULL,
                                        route_name VARCHAR(50),
                                        description VARCHAR(255),
                                        working_hours VARCHAR(50),
                                        active_days VARCHAR(50),
                                        capacity VARCHAR(50),
                                        company_name VARCHAR(50),
                                        expected_price VARCHAR(50)
                                        );
                
                    CREATE TABLE vehicle   (id SERIAL PRIMARY KEY,
                                            route_id INT NOT NULL,
                                            phone_number VARCHAR(20) NOT NULL,
                                            status BOOLEAN,
                                            type VARCHAR(30),
                                            brand VARCHAR(30),
                                            model VARCHAR(30),
                                            license_plate VARCHAR(30),
                                            color VARCHAR(20),
                                            CONSTRAINT fk_route
                                                FOREIGN KEY(route_id) REFERENCES route(id)
                                            );
                
                    CREATE TABLE vehicle_location (id SERIAL PRIMARY KEY,
                                                longitude DECIMAL NOT NULL,
                                                latitude DECIMAL NOT NULL,
                                                vehicle_id INT NOT NULL UNIQUE,
                                                CONSTRAINT fk_vehicle
                                                        FOREIGN KEY(vehicle_id) 
                                                            REFERENCES vehicle(id)
                                                );
                
                    CREATE TABLE waypoint (id SERIAL PRIMARY KEY,
                                           longitude DECIMAL NOT NULL,
                                           latitude DECIMAL NOT NULL,
                                           route_id INT NOT NULL,
                                           projection_index INT NOT NULL DEFAULT 0,
                                           CONSTRAINT fk_route
                                                FOREIGN KEY(route_id)
                                                    REFERENCES route(id)
                                                );
                    CREATE TABLE feedback  (id SERIAL PRIMARY KEY,
                                            passenger_id INT NOT NULL,
                                            vehicle_id INT NOT NULL,
                                            reaction BOOLEAN,
                                            complaint VARCHAR(255),
                                            CONSTRAINT fk_passenger
                                                FOREIGN KEY(passenger_id)
                                                    REFERENCES passenger(id),
                                            CONSTRAINT fk_vehicle
                                                FOREIGN KEY(vehicle_id)
                                                    REFERENCES vehicle(id),
                                            CONSTRAINT not_empty
                                                CHECK  ((reaction IS NOT NULL) OR
                                                        (complaint IS NOT NULL)),
                                            CONSTRAINT unique_feedback
                                                UNIQUE(passenger_id, vehicle_id)
                                                );
                """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    recreate_tables()