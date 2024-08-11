DROP TABLE IF EXISTS station;
DROP TABLE IF EXISTS vehicle_routes;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS passenger;
DROP TABLE IF EXISTS vehicle_location;
DROP TABLE IF EXISTS vehicle;
DROP TABLE IF EXISTS waypoint;
DROP TABLE IF EXISTS route;

CREATE TABLE passenger (id SERIAL PRIMARY KEY,
                        username VARCHAR(255) NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL,
                        first_name VARCHAR(255) NOT NULL,
                        last_name VARCHAR(255) NOT NULL,
                        phone_number VARCHAR(20) UNIQUE,
                        email VARCHAR(50) UNIQUE,
                        CONSTRAINT phone_or_email
                        CHECK ((phone_number IS NOT NULL) OR (email IS NOT NULL))
                        );

CREATE TABLE route (id SERIAL PRIMARY KEY,
                    file_name VARCHAR(30) NOT NULL,
                    route_name VARCHAR(50),
                    description VARCHAR(255),
                    working_hours VARCHAR(50),
                    active_days VARCHAR(50),
                    company_name VARCHAR(50),
                    expected_price VARCHAR(50),
                    company_phone_number VARCHAR(30) DEFAULT 'company phone marc',
                    distance DECIMAL DEFAULT 10.0,
                    estimated_travel_time INT DEFAULT 100.0,
                    route_type VARCHAR(20) DEFAULT 'intercity marc'
                    );


CREATE TABLE vehicle   (id SERIAL PRIMARY KEY,
                        username VARCHAR(255) NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL,
                        first_name VARCHAR(255) NOT NULL,
                        last_name VARCHAR(255) NOT NULL,
                        phone_number VARCHAR(20) UNIQUE,
                        email VARCHAR(50) UNIQUE,
                        cur_route_id INT NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        type VARCHAR(30),
                        brand VARCHAR(30),
                        model VARCHAR(30),
                        license_plate VARCHAR(30) NOT NULL,
                        color VARCHAR(20),
                        CONSTRAINT fk_route
                            FOREIGN KEY(cur_route_id) REFERENCES route(id),
                        CONSTRAINT legal_statuses
                        CHECK (status IN ('active', 'waiting', 'unavailable', 'inactive', 'unknown')),
                        CONSTRAINT phone_or_email
                        CHECK ((phone_number IS NOT NULL) OR (email IS NOT NULL))
                        );

CREATE TABLE vehicle_routes (
                        vehicle_id INT NOT NULL,
                        route_id INT NOT NULL,
                        CONSTRAINT fk_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicle(id),
                        CONSTRAINT fk_route FOREIGN KEY (route_id) REFERENCES route(id),
                        CONSTRAINT pk PRIMARY KEY (vehicle_id, route_id)
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

CREATE TABLE station   (id SERIAL PRIMARY KEY,
                        route_id INT NOT NULL,
                        station_name VARCHAR(50),
                        longitude DECIMAL NOT NULL,
                        latitude DECIMAL NOT NULL,
                            CONSTRAINT fk_route
                                FOREIGN KEY(route_id)
                                    REFERENCES route(id)
                            );