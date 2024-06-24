import psycopg2
import os 

conn = psycopg2.connect(database=os.getenv("db_name"),
                        user=os.getenv("db_user"),
                        host= os.getenv("db_host"),
                        password = os.getenv("password"),
                        port = int(os.getenv("db_port"))
                        )

cur = conn.cursor()

cur.execute("""
            CREATE TABLE passenger (id SERIAL PRIMARY KEY,
                                    user_name VARCHAR(255),
                                    password TEXT,
                                    first_name VARCHAR(255),
                                    last_name VARCHAR(255),
                                    phone_number VARCHAR(20)
                                    );
            CREATE TABLE vehicle   (id SERIAL PRIMARY KEY,
                                    route_number INT,
                                    phone_number VARCHAR(20)
                                    );
            CREATE TABLE vehicle_locations (id SERIAL PRIMARY KEY,
                                            longitude DECIMAL,
                                            latitude DECIMAL,
                                            vehicle_id INT,
                                            CONSTRAINT fk_vehicle
                                                FOREIGN KEY(vehicle_id) 
                                                    REFERENCES vehicle(id)
                                                    ON DELETE SET NULL
                                    );
            """)

conn.commit()
cur.close()
conn.close()