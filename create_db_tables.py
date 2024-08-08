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
                    DROP TABLE IF EXISTS vehicle_location;
                    DROP TABLE IF EXISTS vehicle;
                    DROP TABLE IF EXISTS passenger;
                    DROP TABLE IF EXISTS waypoint;
                    DROP TABLE IF EXISTS route;
                    DROP TABLE IF EXISTS account;
                
                    CREATE TABLE account    (id SERIAL PRIMARY KEY,
                                            account_type VARCHAR(15) NOT NULL, 
                                            username VARCHAR(255) NOT NULL UNIQUE,
                                            password_hash TEXT NOT NULL,
                                            first_name VARCHAR(255) NOT NULL,
                                            last_name VARCHAR(255) NOT NULL,
                                            phone_number VARCHAR(20) NOT NULL UNIQUE,
                                            CONSTRAINT unique_account UNIQUE(id, account_type),
                                            CONSTRAINT valid_types CHECK (account_type IN ('driver', 'passenger'))
                                            );
                    CREATE TABLE passenger  (id INT NOT NULL UNIQUE PRIMARY KEY,  
                                            account_type VARCHAR(15) NOT NULL DEFAULT 'passenger',
                                            CONSTRAINT fk_account
                                                FOREIGN KEY (id, account_type) REFERENCES account(id, account_type),
                                            CONSTRAINT account_is_passenger CHECK (account_type = 'passenger')
                                            );
                
                    CREATE TABLE route (id SERIAL PRIMARY KEY,
                                        file_name VARCHAR(30) NOT NULL
                                        );
                
                    CREATE TABLE vehicle   (id INT NOT NULL UNIQUE PRIMARY KEY,
                                            account_type VARCHAR(15) NOT NULL DEFAULT 'driver',
                                            route_id INT NOT NULL,
                                            status BOOLEAN,
                                            CONSTRAINT fk_route
                                                FOREIGN KEY(route_id) REFERENCES route(id),
                                            CONSTRAINT fk_account
                                                FOREIGN KEY(id, account_type) REFERENCES account(id, account_type),
                                            CONSTRAINT account_is_driver CHECK (account_type = 'driver')
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
                """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    recreate_tables()