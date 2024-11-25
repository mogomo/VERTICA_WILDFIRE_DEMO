-- Usage:    vsql -f create_schema_for_Vertica_wildfire_demo.sql
-- Written by Moshe Goldberg
--
-- In the below schema the wind_direction represents one of the 8 wind directions:
-- 1 = North (N)
-- 2 = North-East (NE)
-- 3 = East (E)
-- 4 = South-East (SE)
-- 5 = South (S)
-- 6 = South-West (SW)
-- 7 = West (W)
-- 8 = North-West (NW)

-- Fire events table:
DROP TABLE IF EXISTS fire_events CASCADE;
CREATE TABLE fire_events ( 
	fire_location_id IDENTITY(1,1), event_id INT, event_time TIMESTAMP, 
	fire_latitude FLOAT, fire_longitude FLOAT, 
	wind_direction int, wind_speed_m_per_sec FLOAT, 
	sensor_temp_degrees_celsius int
) ORDER BY fire_location_id, event_id, event_time;

COPY fire_events (event_id, event_time, fire_latitude, fire_longitude, wind_direction, wind_speed_m_per_sec, sensor_temp_degrees_celsius)
FROM STDIN
DELIMITER ','
ENCLOSED BY '"'
ABORT ON ERROR;
1,"2024-07-24 14:00:00",39.7685,-121.7375,3,6.2,300
1,"2024-07-24 14:30:00",39.7682,-121.7361,3,3.8,450
1,"2024-07-24 15:00:00",39.7666,-121.7365,3,8.1,600
1,"2024-07-24 15:30:00",39.7707,-121.7377,2,5.5,750
1,"2024-07-24 16:00:00",39.7668,-121.7388,2,7.0,850
1,"2024-07-24 16:30:00",39.7659,-121.7397,2,5.3,900
1,"2024-07-24 17:00:00",39.7670,-121.7411,3,8.7,950
1,"2024-07-24 17:30:00",39.7701,-121.7415,3,5.1,1000
1,"2024-07-24 18:00:00",39.7672,-121.7431,3,9.6,950
1,"2024-07-24 18:30:00",39.7673,-121.7344,3,4.2,900
1,"2024-07-24 19:00:00",39.7695,-121.7390,4,6.8,800
1,"2024-07-24 19:30:00",39.7710,-121.7405,4,7.5,700
1,"2024-07-24 20:00:00",39.7725,-121.7420,5,8.2,600
1,"2024-07-24 20:30:00",39.7740,-121.7435,5,7.8,500
1,"2024-07-24 21:00:00",39.7755,-121.7450,6,6.5,400
\.

-- Fire trucks location table
DROP TABLE IF EXISTS fire_trucks_location CASCADE;
CREATE TABLE fire_trucks_location (
    fire_truck_id IDENTITY(1,1),
    event_id INT, event_time TIMESTAMP,
    litres_of_water INT default 1893,  -- max: 5,678 litres
    litres_of_fuel INT default 1500,   -- max: 3785 litres
    fire_truck_name VARCHAR(50),
    latitude FLOAT, longitude FLOAT,
    valid BOOLEAN DEFAULT TRUE
) ORDER BY event_id, fire_truck_id, event_time;

COPY fire_trucks_location (
event_id, event_time, litres_of_water, litres_of_fuel, fire_truck_name, latitude, longitude
)
FROM STDIN
DELIMITER ','
ENCLOSED BY '"'
ABORT ON ERROR;
1,"2024-07-24 14:00:00",5678,3785,"CalFire Engine 5371",39.7705,-121.7385
1,"2024-07-24 14:30:00",4500,3500,"CalFire Engine 5372",39.7665,-121.7351
1,"2024-07-24 15:00:00",3200,3200,"CalFire Engine 5373",39.7696,-121.7345
1,"2024-07-24 15:30:00",1800,2900,"CalFire Engine 5374",39.7717,-121.7387
1,"2024-07-24 16:00:00",500,2600,"CalFire Engine 5375",39.7658,-121.7398
1,"2024-07-24 16:30:00",5678,3785,"CalFire Engine 5376",39.7679,-121.7415
1,"2024-07-24 17:00:00",4200,3500,"CalFire Engine 5377",39.7661,-121.7357
1,"2024-07-24 17:30:00",2800,3200,"CalFire Engine 5378",39.7702,-121.7425
1,"2024-07-24 18:00:00",1400,2900,"CalFire Engine 5379",39.7662,-121.7331
1,"2024-07-24 18:30:00",100,2600,"CalFire Engine 5380",39.7694,-121.7354
1,"2024-07-24 19:00:00",5678,3785,"CalFire Engine 5381",39.7715,-121.7445
1,"2024-07-24 19:10:00",5678,3785,"Butte County Fire Engine 64",39.7685,-121.7405
1,"2024-07-24 19:11:00",4000,3400,"Butte County Fire Engine 65",39.7655,-121.7375
1,"2024-07-24 20:00:00",2300,3000,"Butte County Fire Engine 66",39.7675,-121.7335
1,"2024-07-24 20:10:00",600,2600,"Butte County Fire Engine 67",39.7727,-121.7377
1,"2024-07-24 20:15:00",5678,3785,"Butte County Fire Engine 68",39.7648,-121.7388
1,"2024-07-24 20:16:00",3900,3400,"Butte County Fire Engine 69",39.7729,-121.7422
1,"2024-07-24 20:20:00",2100,3000,"Butte County Fire Engine 70",39.7651,-121.7347
1,"2024-07-24 21:00:00",300,2600,"Butte County Fire Engine 71",39.7712,-121.7415
1,"2024-07-24 21:10:00",5678,3785,"USFS Wildland Engine 42",39.7652,-121.7341
1,"2024-07-24 21:15:00",3800,3300,"USFS Wildland Engine 43",39.7704,-121.7344
1,"2024-07-24 21:17:00",1900,2800,"USFS Wildland Engine 44",39.7715,-121.7355
1,"2024-07-24 21:19:00",100,2300,"USFS Wildland Engine 45",39.7675,-121.7395
1,"2024-07-24 21:22:00",5678,3785,"USFS Wildland Engine 46",39.7745,-121.7445
1,"2024-07-24 21:30:00",3700,3300,"USFS Wildland Engine 47",39.7659,-121.7415
1,"2024-07-24 21:33:00",5678,3785,"Chico Fire Engine 21",39.7751,-121.7457
1,"2024-07-24 22:03:00",3500,3200,"Chico Fire Engine 22",39.7712,-121.7334
1,"2024-07-24 22:12:00",1300,2600,"Chico Fire Engine 23",39.7758,-121.7445
1,"2024-07-24 22:14:00",5678,3785,"Chico Fire Engine 24",39.7665,-121.7395
1,"2024-07-24 22:20:00",5678,3785,"CalFire Truck 2554",39.7735,-121.7455
1,"2024-07-24 22:24:00",2800,3000,"CalFire Truck 2555",39.7725,-121.7434
1,"2024-07-24 22:31:00",100,2200,"CalFire Truck 2556",39.7735,-121.7455
1,"2024-07-24 22:47:00",5678,3785,"CalFire Truck 2557",39.7655,-121.7405
\.

SELECT * FROM fire_events ORDER BY fire_location_id, event_id, event_time;
SELECT * FROM fire_trucks_location ORDER BY fire_truck_id, event_id, event_time, fire_truck_name;

