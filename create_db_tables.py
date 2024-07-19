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

    cur.execute(""" DROP TABLE IF EXISTS passenger;
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
                                        file_name VARCHAR(30) NOT NULL
                                        );
                
                    CREATE TABLE vehicle   (id SERIAL PRIMARY KEY,
                                            route_id INT NOT NULL,
                                            phone_number VARCHAR(20) NOT NULL,
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
                                           CONSTRAINT fk_route
                                                FOREIGN KEY(route_id)
                                                    REFERENCES route(id)
                                                );
                """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    recreate_tables()