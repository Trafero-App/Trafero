DROP TABLE IF EXISTS app_feedback;
DROP TABLE IF EXISTS passenger_saved_route;
DROP TABLE IF EXISTS driver_saved_route;
DROP TABLE IF EXISTS passenger_saved_vehicle;
DROP TABLE IF EXISTS driver_saved_vehicle;
DROP TABLE IF EXISTS passenger_saved_location;
DROP TABLE IF EXISTS driver_saved_location;
DROP TABLE IF EXISTS driver;
DROP TABLE IF EXISTS vehicle_status_history;
DROP TABLE IF EXISTS vehicle_location_history;
DROP TABLE IF EXISTS feedback_fixed_complaint;
DROP TABLE IF EXISTS other_complaint;
DROP TABLE IF EXISTS fixed_complaint;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS station;
DROP TABLE IF EXISTS intersection;
DROP TABLE IF EXISTS vehicle_route;
DROP TABLE IF EXISTS passenger;
DROP TABLE IF EXISTS vehicle_location;
DROP TABLE IF EXISTS vehicle;
DROP TABLE IF EXISTS waypoint;
DROP TABLE IF EXISTS "route";

CREATE TABLE passenger (id SERIAL PRIMARY KEY,
                        password_hash TEXT NOT NULL,
                        first_name VARCHAR(255) NOT NULL,
                        last_name VARCHAR(255) NOT NULL,
                        date_of_birth VARCHAR(10) NOT NULL,
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
                    distance VARCHAR(10),
                    estimated_travel_time INT DEFAULT 100.0,
                    route_type VARCHAR(20) DEFAULT 'intercity marc'
                    );


CREATE TABLE vehicle   (id SERIAL PRIMARY KEY,
                        cur_route_id INT NOT NULL,
                        "status" VARCHAR(20) NOT NULL DEFAULT 'inactive',
                        "type" VARCHAR(30) NOT NULL,
                        brand VARCHAR(30) NOT NULL,
                        model VARCHAR(30) NOT NULL,
                        license_plate VARCHAR(30) NOT NULL,
                        color VARCHAR(20) NOT NULL,
                        CONSTRAINT fk_route
                            FOREIGN KEY(cur_route_id) REFERENCES route(id),
                        CONSTRAINT legal_statuses
                        CHECK (status IN ('active', 'waiting', 'unavailable', 'inactive', 'unknown'))
                        );

CREATE TABLE driver (id SERIAL PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    first_name VARCHAR(255) NOT NULL,
                    last_name VARCHAR(255) NOT NULL,
                    date_of_birth VARCHAR(10) NOT NULL,
                    phone_number VARCHAR(20) UNIQUE NOT NULL,
                    email VARCHAR(50) UNIQUE,
                    vehicle_id INT NOT NULL REFERENCES vehicle(id));

CREATE TABLE vehicle_route (
                        vehicle_id INT NOT NULL,
                        route_id INT NOT NULL,
                        CONSTRAINT fk_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicle(id),
                        CONSTRAINT fk_route FOREIGN KEY (route_id) REFERENCES route(id),
                        CONSTRAINT vehicle_routes_pk PRIMARY KEY (vehicle_id, route_id)
                        );

CREATE TABLE vehicle_location (id SERIAL PRIMARY KEY,
                            longitude DECIMAL,
                            latitude DECIMAL,
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
                        reaction VARCHAR(11),
                        CONSTRAINT fk_passenger
                            FOREIGN KEY(passenger_id)
                                REFERENCES passenger(id),
                        CONSTRAINT fk_vehicle
                            FOREIGN KEY(vehicle_id)
                                REFERENCES vehicle(id),
                        CONSTRAINT not_empty
                            CHECK  (reaction IS NOT NULL),
                        CONSTRAINT unique_feedback
                            UNIQUE(passenger_id, vehicle_id),
                        CONSTRAINT legal_reactions CHECK (reaction IN ('thumbs_up', 'thumbs_down'))
                            );

CREATE TABLE fixed_complaint (id SERIAL PRIMARY KEY,
                        complaint_details VARCHAR(255) NOT NULL
                        );

CREATE TABLE feedback_fixed_complaint (feedback_id INT NOT NULL,
                                 fixed_complaint_id INT NOT NULL,
                                 CONSTRAINT feedback_complaint_pk PRIMARY KEY (feedback_id, fixed_complaint_id),
                                 CONSTRAINT feedback_fk FOREIGN KEY (feedback_id) REFERENCES feedback(id) ON DELETE CASCADE,
                                 CONSTRAINT fixed_complaint_fk FOREIGN KEY (fixed_complaint_id) REFERENCES fixed_complaint(id));

CREATE TABLE other_complaint (feedback_id INT NOT NULL,
                               complaint_details VARCHAR(255) NOT NULL,
                               CONSTRAINT fk_feedback FOREIGN KEY (feedback_id) REFERENCES feedback(id) ON DELETE CASCADE);

CREATE TABLE station   (id SERIAL PRIMARY KEY,
                        route_id INT NOT NULL,
                        station_name VARCHAR(50),
                        longitude DECIMAL NOT NULL,
                        latitude DECIMAL NOT NULL,
                            CONSTRAINT fk_route
                                FOREIGN KEY(route_id)
                                    REFERENCES route(id)
                            );


CREATE TABLE vehicle_location_history (id SERIAL PRIMARY KEY,
                                       time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                       vehicle_id INT NOT NULL,
                                       old_lat DECIMAL,
                                       old_long DECIMAL,
                                       new_lat DECIMAL NOT NULL,
                                       new_long DECIMAL NOT NULL,
                                       CONSTRAINT vehicle_fk FOREIGN KEY (vehicle_id) REFERENCES vehicle(id)
                                      );

CREATE TABLE vehicle_status_history (id SERIAL PRIMARY KEY,
                                       time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                       vehicle_id INT NOT NULL,
                                       old_status VARCHAR(20) NOT NULL,
                                       new_status VARCHAR(20) NOT NULL,
                                       CONSTRAINT legal_new_status CHECK
                                       (new_status IN ('active', 'waiting', 'unavailable', 'inactive', 'unknown')),
                                       CONSTRAINT legal_old_status CHECK
                                       (old_status IN ('active', 'waiting', 'unavailable', 'inactive', 'unknown')),
                                       CONSTRAINT vehicle_fk FOREIGN KEY (vehicle_id) REFERENCES vehicle(id)
                                      ); 
CREATE TABLE intersection (id SERIAL PRIMARY KEY,
                            route_id INT NOT NULL,
                            local_index INT NOT NULL,
                            auxiliary_route INT NOT NULL,
                            auxiliary_index INT NOT NULL,
                                CONSTRAINT fk_route
                                    FOREIGN KEY(route_id)
                                        REFERENCES route(id)
                            );


CREATE TABLE passenger_saved_route (passenger_id INT NOT NULL REFERENCES passenger(id),
                                     route_id INt NOT NULL REFERENCES route(id));

CREATE TABLE driver_saved_route (driver_id INt NOT NULL REFERENCES driver(id),
                                     route_id INt NOT NULL REFERENCES route(id));

CREATE TABLE passenger_saved_vehicle (passenger_id INt NOT NULL REFERENCES passenger(id),
                                       vehicle_id INt NOT NULL REFERENCES vehicle(id),
                                       nickname VARCHAR(50) NOT NULL);

CREATE TABLE driver_saved_vehicle (driver_id INt NOT NULL REFERENCES driver(id),
                                       vehicle_id INt NOT NULL REFERENCES vehicle(id),
                                       nickname VARCHAR(50) NOT NULL);

CREATE TABLE passenger_saved_location (passenger_id INt NOT NULL REFERENCES passenger(id),
                                       longitude DECIMAL NOT NULL,
                                       latitude DECIMAL NOT NULL,
                                       "name" VARCHAR(20) NOT NULL,
                                       icon VARCHAR(10) NOT NULL);

CREATE TABLE driver_saved_location (driver_id INt NOT NULL REFERENCES driver(id),
                                       longitude DECIMAL NOT NULL,
                                       latitude DECIMAL NOT NULL,
                                       "name" VARCHAR(20) NOT NULL,
                                       icon VARCHAR(10) NOT NULL);


CREATE TABLE app_feedback (id SERIAL PRIMARY KEY,
                            feedback VARCHAR(1000) NOT NULL)