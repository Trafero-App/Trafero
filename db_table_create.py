import psycopg2
import os 

conn = psycopg2.connect(database=os.getenv("db_name"),
                        user=os.getenv("db_user"),
                        host= os.getenv("db_host"),
                        password = os.getenv("db_password"),
                        port = int(os.getenv("db_port"))
                        )

cur = conn.cursor()

cur.execute("""
            DROP TABLE passenger;
            DROP TABLE vehicle_location;
            DROP TABLE vehicle;
            CREATE TABLE passenger (id SERIAL PRIMARY KEY,
                                    user_name VARCHAR(255) NOT NULL UNIQUE,
                                    password TEXT NOT NULL,
                                    first_name VARCHAR(255) NOT NULL,
                                    last_name VARCHAR(255) NOT NULL,
                                    phone_number VARCHAR(20) NOT NULL UNIQUE
                                    );
            CREATE TABLE vehicle   (id SERIAL PRIMARY KEY,
                                    route_number INT NOT NULL,
                                    phone_number VARCHAR(20) NOT NULL UNIQUE
                                    );
            CREATE TABLE vehicle_location (id SERIAL PRIMARY KEY,
                                           longitude DECIMAL NOT NULL,
                                           latitude DECIMAL NOT NULL,
                                           vehicle_id INT NOT NULL UNIQUE,
                                           CONSTRAINT fk_vehicle
                                                FOREIGN KEY(vehicle_id) 
                                                    REFERENCES vehicle(id)
                                    );
            """)

conn.commit()
cur.close()
conn.close()