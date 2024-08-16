INSERT INTO passenger 
    (password_hash, first_name, last_name, phone_number, email, date_of_birth) VALUES
    ('$2b$12$UV.jCkFpPt2DVMWp4RjLN..p0yXZuxFZsbqqmK5xQ1pdnBdjByLo6', 'p1f', 'p1l', '12345678', 'p1@mail.com', '1111-11-11'),
    ('$2b$12$EmxAwWZZLxbA6ABF6jErQO.tGddTSYDwB9TzdQ2n2QKdmszxJEWiO', 'p2f', 'p2l', NULL, 'p2@mail.com', '1111-22-22'),
    ('$2b$12$PRX4BGK5vvyuIcBsIGaz4Ou4uHscFuk2tefTimAMKm9z5WphFw8VG', 'p3f', 'p3l', '33333333', NULL, '1111-33-33');
    
    

INSERT INTO route (file_name, route_name, description, working_hours, active_days, company_name, expected_price, company_phone_number, distance, estimated_travel_time, route_type) VALUES 
    ('bus_15_1.geojson', 'Bus 15 (Dawra - Nahr al Mot)', 'Dawra - Port - Biel - Ain el Mrayse - Raouche - Unesco - Cola - Corniche el Mazraa - Barbir - Mathaf - Adliye - Souk el Ahad - Nahr el Mot', '6:00 AM - 8:00 PM', 'Monday -> Sunday', 'Rabah Transport','80.000 LL', '03 302355', '17.5 km', 90, 'Coverage commuter'), 
    ('bus_15_2.geojson', 'Bus 15 (Nahr al Mot - Dawra)', 'Nahr al Mot - Souk el Ahad - Adliye - Mathaf - Barbir - Corniche el Mazraa - Cola - Unesco - Raouche - Ain el Mrayse - Biel - Port - Dawra', '6:00 AM - 8:00 PM', 'Monday -> Sunday', 'Rabah Transport','80.000 LL', '03 302355', '17.2 km', 90, 'Coverage commuter'), 
    ('beirut_saida_1.geojson', 'Van Saida (Beirut - Saida)', 'Cola - Madine al Riyadiye - Airport Highway - Khalde - Doha - Nahmeh - Damour - Jiye - Jadra - Saida (sehit nejme)', '5:00 AM - 9:00 PM', 'Monday -> Sunday', 'individual operators', '140.000 LL', 'NA', '49 km', 50, 'Intercity'), 
    ('beirut_saida_2.geojson', 'Van Saida (Saida - Beirut)', 'Saida (Sehit Nejme) - Jadra - Jiye - Damour - Nahmeh - Doha - Khalde - Airport Highway - Madine al Riyadiye - Cola', '5:00 AM - 9:00 PM', 'Monday -> Sunday', 'individual operators', '140.000 LL', 'NA', '49 km', 50, 'Intercity'),
    ('van_4_1.geojson', 'Van 4 (Hamra - Hay el Selom)', 'Hamra - Spears - Bechara el Khoury - Horsh Beirut - Old Saida Road - Haret Hreik - Hadath - Lailake - Hay el Selom', '5:00 AM - 11:00 PM', 'Monday -> Sunday', 'individual operators', '100.000 LL', 'NA', '12.3 km', 45, 'Rapid commuter'), 
    ('van_4_2.geojson', 'Van 4 (Hay el Selom - Hamra)', 'Hay el Selom - Lailake - Hadath - Haret Hreik - Old Saida Road - Horsh Beirut - Bechara el Khoury - Spears - Hamra', '5:00 AM - 11:00 PM', 'Monday -> Sunday', 'individual operators', '100.000 LL', 'NA', '12.1 km', 45, 'Rapid commuter'), 
    ('van_sea_road_1.geojson', 'Van (Ain el Mrayse - Jesr al Matar)', 'Ain el Mrayse - Manara - Raouche - Unesco - Jnah - Bir Hassan - Rihab - Jesr al Matar', '6:00 AM - 8:00 PM', 'Monday -> Sunday', 'individual operators', '100.000 LL', 'NA', '9.5 km', 30, 'Local commuter'), 
    ('van_sea_road_2.geojson', 'Van (Jesr al Matar - Ain el Mrayse)', 'Jesr al Matar - Rihab - Bir Hassan - Jnah - Unesco - Raouche - Manara - Ain el Mrayse', '6:00 AM - 8:00 PM', 'Monday -> Sunday', 'individual operators', '100.000 LL', 'NA', '9.5 km', 30, 'Local commuter'),
    ('bus_2_1.geojson', 'Bus 2 (Hamra - Antelias)', 'Hamra - Tallet al Drouz - Mar Elias - Basta al Tahta - Achrafiye - Karantina - Borj Hammoud - Baouchriyeh - Jdeideh - Zalqa - Jal el Dib - Antelias', '5:00 AM - 7:00 PM', 'Monday -> Sunday', 'Rabah Transport', '70.000 LL', '03 302355', '14.2', 90, 'Coverage commuter'), 
    ('bus_2_2.geojson', 'Bus 2 (Antelias - Hamra)', 'Antelias - Jal el Dib - Zalqa - Jdeideh - Baouchriyeh - Borj Hammoud - Karantina - Achrafiye - Basta al Tahta - Mar Elias - Tallet al Drouz - Hamra', '5:00 AM - 7:00 PM', 'Monday -> Sunday', 'Rabah Transport', '70.000 LL', '03 302355', '13.9', 90, 'Coverage commuter'), 
    ('van_10_1.geojson', 'Van 10 (Dawra - Matar)', 'Dawra - Port - Bechara el Khoury - Horsh beirut - Borj al Barajne - Tohwitet el Ghadir - Airport', '5:00 AM - 11:00 PM', 'Monday -> Sunday', 'Individual operators', '70.000 LL', 'NA', '13.1 km', 35, 'Airport express'), 
    ('van_10_2.geojson', 'Van 10 (Matar - Dawra)', 'Airport - Tohwitet el Ghadir - Borj al Barajne - Horsh Beirut - Bechara el Khoury - Port - Dawra', '5:00 AM - 11:00 PM', 'Monday -> Sunday', 'Individual operators', '70.000 LL', 'NA', '12.8 km', 35, 'Airport express'),
    ('bus_24_1.geojson', 'Bus 24 (Hamra - Badaro)', 'Hamra - Verdun - Corniche el Mazraa - Mathaf - Adliye - Badaro', '6:00 AM - 7:00 PM', 'Monday -> Sunday', 'Rabah Transport', '60.000 LL', '03 302355', '5.3 km', 30, 'Local commuter'), 
    ('bus_24_2.geojson', 'Bus 24 (Badaro - Hamra)', 'Badaro - Adliye - Mathaf - Corniche el Mazraa - Verdun - Hamra', '6:00 AM - 7:00 PM', 'Monday -> Sunday',  'Rabah Transport', '60.000 LL', '03 302355', '5.7 km', 30, 'Local commuter');

INSERT INTO vehicle (cur_route_id, "status", license_plate, "type", brand, model, color) VALUES
(2, 'active', 'B 12345',  'bus', 'some_brand1', 'some_model1', 'red'),
(2, 'active', 'A 12345',  'bus', 'some_brand2', 'some_model2', 'black'),
(2, 'active', 'C 1',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 2',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 3',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 4',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 5',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 6',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 7',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 8',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 9',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 10',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 11',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 12',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 13',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 14',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 15',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 16',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'C 17',  'van', 'some_brand3', 'some_model3', 'white'),
(2, 'active', 'D 56789',  'bus', 'some_brand4', 'some_model4', 'black');


INSERT INTO driver (password_hash, first_name, last_name, date_of_birth, phone_number, email, vehicle_id) VALUES
    ('$2b$12$ipMawf8bhVJSH2mvcFIx..PjeCbMrlZqwZAWWupp.qcKxwCfEfp0G', 'v1f', 'v1l', '1111-11-22', '12345678', NULL, 1), 
    ('$2b$12$DzT92dyevkLveACbcnJzz.6c4a.fwXoriW9Uhz0Wq99Kjbb7WKCMy', 'v2f', 'v2l', '1111-22-33', '12345096', NULL, 2), 
    ('$2b$12$XKoRYKz/UGvgff6Sg8JCIOwuR3FRebIP4F.WypDwj57j0v24r6wH6', 'v3f', 'v3l', '1111-33-44', '12045079', NULL, 3);

INSERT INTO vehicle_location (longitude, latitude, vehicle_id) VALUES
    (35.5149, 33.8966, 1),
    (35.5295, 33.8987, 2),
    (35.5119, 33.8979, 3),
    (35.4970823636782,
          33.901215844914276, 4),
    (35.49073744262566,
          33.90141839418621, 5),
    (35.48422983129038,
          33.90209355495037, 6),
    (       35.478372981088114,
          33.90229610213716, 7),
    (  35.47414303371929,
          33.90135087781553, 8),
    (35.47129595376006,
          33.90040564301478, 9),
    (35.470807882909725,
          33.89858266059262, 10),
    (35.47040115720074,
          33.89621947722301, 11),
    (35.47040115720074,
          33.894261361391045, 12),
    (35.47015712177563,
          33.892910910483806, 13),
    ( 35.472190750318106,
          33.889737266682346, 14),
    ( 35.477071458819836,
          33.88548304827681, 15),
    (35.483985795865294,
          33.882309128115594, 16),
    (35.48976130092626,
          33.881228617717284, 17),
    (35.49691967339564,
          33.87927015774419, 18),
    (35.50773857724093,
          33.878257143568774, 19),
    (35.516198471978555,
          33.87866235068171, 20);
INSERT INTO vehicle_route (vehicle_id, route_id) VALUES (1, 1), (1, 2), (1, 3);
INSERT INTO waypoint (longitude, latitude, route_id, projection_index) VALUES 
(35.549782, 33.893595, 1, 0), (35.546651, 33.894754, 1, 72), (35.540836, 33.896257, 1, 132),
    (35.531785, 33.898479, 1, 223), (35.522762, 33.898484, 1, 317), (35.508671, 33.899558, 1, 487),
    (35.499918, 33.9022, 1, 600), (35.480682, 33.902845, 1, 841), (35.470241, 33.895071, 1, 1017),
    (35.477784, 33.884366, 1, 1225), (35.489824, 33.880914, 1, 1359), (35.503598, 33.877785, 1, 1505),
    (35.512224, 33.878551, 1, 1596), (35.521562, 33.879485, 1, 1689), (35.525905, 33.881088, 1, 1734),
    (35.529818, 33.883615, 1, 1789), (35.534974, 33.87901, 1, 1884), (35.540011, 33.879761, 1, 1975),
    
(35.540002, 33.879845, 2, 0), (35.538117, 33.878337, 2, 48), (35.531328, 33.883102, 2, 160),
(35.528302, 33.88242, 2, 220), (35.515335, 33.878857, 2, 358), (35.507801, 33.878318, 2, 432),
(35.491437, 33.880566, 2, 606), (35.4738, 33.887265, 2, 820), (35.470343, 33.89493, 2, 966),
(35.475335, 33.90162, 2, 1089), (35.485492, 33.90172, 2, 1199), (35.493217, 33.90122, 2, 1288),
(35.503917, 33.901601, 2, 1418), (35.512446, 33.897487, 2, 1543), (35.52458, 33.899189, 2, 1685),
(35.541633, 33.895861, 2, 1859), (35.549835, 33.893719, 2, 1947), (35.549777, 33.893579, 2, 1948),
    
(35.494902, 33.875663, 3, 0), (35.493856, 33.862894, 3, 155), (35.493563, 33.848623, 3, 348),
(35.497731, 33.833362, 3, 555), (35.4982, 33.81763, 3, 797), (35.486706, 33.802825, 3, 997),
(35.477275, 33.784659, 3, 1248), (35.464307, 33.766235, 3, 1506), (35.453198, 33.741679, 3, 1829),
(35.441053, 33.701633, 3, 2342), (35.424672, 33.676096, 3, 2765), (35.423999, 33.656983, 3, 3016),
(35.402034, 33.630558, 3, 3479), (35.390934, 33.599087, 3, 3955), (35.386787, 33.588114, 3, 4099),
(35.38496, 33.582172, 3, 4171), (35.376466, 33.567235, 3, 4386), (35.37488, 33.565158, 3, 4423),
    
(35.374861, 33.565187, 4, 0), (35.376099, 33.567906, 4, 74), (35.381682, 33.576067, 4, 194),
(35.402032, 33.60738, 4, 675), (35.419141, 33.651847, 4, 1351), (35.424938, 33.684284, 4, 1795),
(35.453706, 33.739151, 4, 2594), (35.466136, 33.767748, 4, 2971), (35.479172, 33.787295, 4, 3237),
(35.499392, 33.819022, 4, 3667), (35.502908, 33.830236, 4, 3825), (35.494105, 33.841819, 4, 4012),
(35.493976, 33.86115, 4, 4236), (35.495241, 33.875001, 4, 4403),
    

(35.485447, 33.89684,  5, 0), (35.488068, 33.896187, 5, 32), (35.488936, 33.894374, 5, 72),
(35.495857, 33.894776, 5, 141), (35.506346, 33.891462, 5, 275), (35.506776, 33.883904, 5, 370),
(35.507143, 33.879831, 5, 419), (35.5084, 33.87567, 5, 480), (35.514994, 33.869782, 5, 573),
(35.516584, 33.865282, 5, 635), (35.519448, 33.85828, 5, 732), (35.519599, 33.856966, 5, 751),
(35.520861, 33.854238, 5, 789), (35.521598, 33.851316, 5, 828), (35.521288, 33.848443, 5, 870),
(35.515816, 33.848674, 5, 927), (35.516324, 33.844047, 5, 982), (35.517079, 33.837222, 5, 1075),
(35.517256, 33.833051, 5, 1137), (35.517322, 33.831661, 5, 1153), (35.517267, 33.830332, 5, 1183),
(35.515608, 33.829198, 5, 1210),
    
(35.515581, 33.829171, 6, 0), (35.517508, 33.830229, 6, 33), (35.516949, 33.839385, 6, 181),
(35.515951, 33.848554, 6, 288), (35.521355, 33.848458, 6, 345), (35.520842, 33.854544, 6, 433),
(35.519701, 33.859151, 6, 499), (35.516476, 33.867362, 6, 615), (35.508585, 33.875683, 6, 745),
(35.507298, 33.879817, 6, 802), (35.506878, 33.884931, 6, 864), (35.506686, 33.890938, 6, 947),
(35.506919, 33.894014, 6, 995), (35.505105, 33.892552, 6, 1049), (35.496095, 33.895225, 6, 1166),
(35.495225, 33.895679, 6, 1183), (35.490888, 33.895315, 6, 1229), (35.488928, 33.895307, 6, 1249),
(35.484921, 33.895319, 6, 1292), (35.485421, 33.896841, 6, 1310),
    
(35.491032, 33.901888, 7, 0), (35.483411, 33.902415, 7, 86), (35.471658, 33.900443, 7, 214), (35.477483, 33.884814, 7, 494),
(35.485399, 33.881194, 7, 593), (35.486209, 33.877556, 7, 649), (35.486155, 33.876384, 7, 663), (35.486208, 33.873462, 7, 702),
(35.485911, 33.863582, 7, 819), (35.486289, 33.860093, 7, 879), (35.493569, 33.859781, 7, 954), (35.493712, 33.858154, 7, 982),
(35.499498, 33.859456, 7, 1066), (35.50302, 33.859115, 7, 1104),
    

(35.502304, 33.859348, 8, 0), (35.49441, 33.859983, 8, 77), (35.486012, 33.860569, 8, 175),
(35.486422, 33.866935, 8, 254), (35.486383, 33.873178, 8, 348), (35.486779, 33.879689, 8, 434),
(35.484797, 33.882053, 8, 474), (35.473984, 33.886964, 8, 615), (35.470563, 33.895946, 8, 780),
(35.475335, 33.90162, 8, 889), (35.490564, 33.901384, 8, 1054),

(35.483562, 33.893968, 9, 0), (35.484361, 33.892556, 9, 29), (35.484483, 33.890219, 9, 70),
(35.491667, 33.889563, 9, 148), (35.500984, 33.888823, 9, 253), (35.506302, 33.887186, 9, 314),
(35.516141, 33.88674, 9, 437), (35.520856, 33.88903, 9, 512), (35.520633, 33.893019, 9, 571),
(35.51913, 33.893899, 9, 608), (35.519604, 33.895171, 9, 625), (35.523653, 33.896005, 9, 671),
(35.527177, 33.897398, 9, 717), (35.527653, 33.899118, 9, 739), (35.542167, 33.895717, 9, 887),
(35.551764, 33.892753, 9, 999), (35.554893, 33.889869, 9, 1072), (35.560622, 33.892323, 9, 1140),
(35.563748, 33.893042, 9, 1200), (35.569848, 33.898139, 9, 1314), (35.575792, 33.903067, 9, 1410),
(35.580226, 33.906865, 9, 1478), (35.584881, 33.912213, 9, 1571), (35.589516, 33.916571, 9, 1653),
    
(35.58947, 33.916611, 10, 0), (35.586792, 33.909081, 10, 147), (35.576571, 33.895227, 10, 364),
(35.565785, 33.890843, 10, 598), (35.558937, 33.892439, 10, 707), (35.551222, 33.893203, 10, 798),
(35.54156, 33.896073, 10, 910), (35.51822, 33.892648, 10, 1227), (35.520407, 33.887169, 10, 1344),
(35.508123, 33.886815, 10, 1475), (35.496394, 33.889314, 10, 1611), (35.484711, 33.890204, 10, 1740),
(35.483487, 33.892736, 10, 1780), (35.483562, 33.893968, 10, 1798),

(35.549782, 33.893596, 11, 0), (35.542988, 33.895705, 11, 109), (35.523046, 33.898627, 11, 313),
(35.507177, 33.8973, 11, 487), (35.506332, 33.888945, 11, 591), (35.507249, 33.87847, 11, 718),
(35.506918, 33.867797, 11, 851), (35.504698, 33.86258, 11, 923), (35.502182, 33.856487, 11, 999),
(35.498361, 33.844467, 11, 1150), (35.496027, 33.837095, 11, 1243), (35.492738, 33.826098, 11, 1411),
    

(35.493105, 33.826017, 12, 0), (35.494425, 33.831323, 12, 113), (35.496585, 33.838183, 12, 200),
(35.501264, 33.853002, 12, 388), (35.504629, 33.862086, 12, 501), (35.507228, 33.869704, 12, 598),
(35.506888, 33.88482, 12, 786), (35.507663, 33.89716, 12, 961), (35.526202, 33.899282, 12, 1173),
(35.549852, 33.893721, 12, 1418), (35.549771, 33.893577, 12, 1419),
    
(35.487638, 33.893756, 13, 0), (35.486497, 33.892562, 13, 22), (35.484351, 33.890838, 13, 56),
(35.483221, 33.888509, 13, 91), (35.4832, 33.883082, 13, 163), (35.485811, 33.881659, 13, 201),
(35.494389, 33.879549, 13, 296), (35.504843, 33.877539, 13, 406), (35.519881, 33.879005, 13, 559),
(35.518277, 33.876596, 13, 610),
    
(35.518277, 33.876596, 14, 0), (35.512011, 33.878626, 14, 76), (35.497042, 33.878941, 14, 229),
(35.486205, 33.881807, 14, 349), (35.485441, 33.883307, 14, 373), (35.486451, 33.885695, 14, 409),
(35.486998, 33.888785, 14, 448), (35.483837, 33.891497, 14, 524), (35.483317, 33.893952, 14, 559),
(35.487638, 33.893756, 14, 611);
    
    

INSERT INTO station (route_id, station_name, longitude, latitude) VALUES
    (1, 'Dawra 15', 35.5498, 33.8936), (2, 'Naher el Mot 15', 35.5402, 33.8798),
    (3, 'Cola-Saida', 35.4948, 33.8756), (4, 'Saida-Beirut', 35.3748, 33.5651),
    (5, 'Hamra 4', 35.4855, 33.8969), (6, 'Hay el Selom 4', 35.5156, 33.8292),
    (7, 'Sea road', 35.4917, 33.9023), (8, 'Sea road', 35.5025, 33.8591),
    (9, 'Hamra 2', 35.4836, 33.8939), (10, 'Antelias 2', 35.5896, 33.9165),
    (11, 'Dawra 10', 35.5501, 33.8941), (12, 'Airport 10', 35.4929, 33.8261),
    (13, 'Hamra 24', 35.4877, 33.8938), (14, 'Badaro 24', 35.5189, 33.8769);


INSERT INTO intersection (route_id, local_index, auxiliary_route, auxiliary_index) VALUES
    (1, 14, 10, 804),
    (1, 264, 9, 739),
    (1, 429, 12, 1025),
    (1, 1306, 7, 501),
    (1, 1320, 8, 460),
    (1, 1291, 13, 173),
    (1, 1319, 14, 351),
    (1, 1421, 3, 0),
    (1, 1421, 4, 4403),
    (1, 1546, 5, 433),
    (1, 1546, 6, 781),
    (1, 1549, 11, 722),
    (1, 1548, 12, 706),
    (2, 436, 11, 721),
    (2, 436, 12, 709),
    (2, 433, 5, 436),
    (2, 433, 6, 780),
    (2, 563, 3, 0),
    (2, 563, 4, 4403),
    (2, 693, 13, 172),
    (2, 664, 14, 351),
    (2, 678, 7, 581),
    (2, 664, 8, 461),
    (2, 1549, 11, 420),
    (2, 1718, 9, 739),
    (2, 1610, 10, 1165),
    (3, 0, 1, 1421),
    (3, 0, 2, 563),
    (3, 0, 13, 308),
    (3, 0, 14, 248),
    (3, 198, 7, 953),
    (3, 187, 8, 95),
    (3, 526, 11, 1274),
    (3, 526, 12, 153),
    (4, 3919, 11, 1274),
    (4, 3919, 12, 153),
    (4, 4219, 7, 1006),
    (4, 4219, 8, 95),
    (4, 4403, 1, 1421),
    (4, 4403, 2, 563),
    (4, 4403, 13, 308),
    (4, 4403, 14, 248),
    (5, 59, 13, 0),
    (5, 59, 14, 598),
    (5, 270, 11, 556),
    (5, 270, 12, 885),
    (5, 331, 9, 317),
    (5, 331, 10, 1494),
    (5, 433, 1, 1546),
    (5, 436, 2, 433),
    (5, 438, 13, 436),
    (5, 438, 14, 121),
    (5, 464, 11, 746),
    (6, 758, 11, 746),
    (6, 758, 12, 681),
    (6, 782, 13, 436),
    (6, 782, 14, 121),
    (6, 781, 1, 1546),
    (6, 780, 2, 433),
    (6, 893, 9, 317),
    (6, 893, 10, 1494),
    (6, 962, 12, 885),
    (6, 1262, 13, 0),
    (7, 566, 13, 174),
    (7, 581, 14, 352),
    (7, 581, 1, 1306),
    (7, 581, 2, 678),
    (7, 953, 3, 198),
    (7, 1006, 4, 4219),
    (7, 1104, 11, 967),
    (7, 1104, 12, 462),
    (8, 0, 11, 967),
    (8, 0, 12, 462),
    (8, 95, 3, 187),
    (8, 95, 4, 4219),
    (8, 460, 1, 1320),
    (8, 461, 2, 664),
    (8, 491, 13, 171),
    (8, 462, 14, 352),
    (9, 61, 13, 60),
    (9, 103, 14, 466),
    (9, 316, 11, 615),
    (9, 316, 12, 817),
    (9, 317, 5, 331),
    (9, 317, 6, 893),
    (9, 739, 1, 264),
    (9, 739, 2, 1718),
    (9, 739, 11, 266),
    (9, 739, 12, 1187),
    (10, 804, 1, 14),
    (10, 1165, 2, 1610),
    (10, 1163, 11, 366),
    (10, 1165, 12, 1080),
    (10, 1494, 5, 331),
    (10, 1494, 6, 893),
    (10, 1495, 11, 615),
    (10, 1492, 12, 817),
    (10, 1750, 13, 60),
    (11, 266, 9, 739),
    (11, 366, 10, 1163),
    (11, 420, 2, 1549),
    (11, 556, 5, 270),
    (11, 615, 9, 316),
    (11, 615, 10, 1495),
    (11, 722, 1, 1549),
    (11, 721, 2, 436),
    (11, 723, 13, 435),
    (11, 723, 14, 120),
    (11, 746, 5, 464),
    (11, 746, 6, 758),
    (11, 967, 7, 1104),
    (11, 967, 8, 0),
    (11, 1274, 3, 526),
    (11, 1274, 4, 3919),
    (12, 153, 3, 526),
    (12, 153, 4, 3919),
    (12, 462, 7, 1104),
    (12, 462, 8, 0),
    (12, 681, 6, 758),
    (12, 707, 13, 435),
    (12, 709, 14, 121),
    (12, 706, 1, 1548),
    (12, 709, 2, 436),
    (12, 817, 9, 316),
    (12, 817, 10, 1492),
    (12, 885, 5, 270),
    (12, 885, 6, 962),
    (12, 1025, 1, 429),
    (12, 1187, 9, 739),
    (12, 1080, 10, 1165),
    (13, 0, 5, 59),
    (13, 0, 6, 1262),
    (13, 60, 9, 61),
    (13, 60, 10, 1750),
    (13, 174, 7, 566),
    (13, 171, 8, 491),
    (13, 173, 1, 1291),
    (13, 203, 2, 664),
    (13, 308, 3, 0),
    (13, 308, 4, 4403),
    (13, 436, 5, 438),
    (13, 436, 6, 782),
    (13, 435, 11, 723),
    (13, 435, 12, 707),
    (14, 120, 11, 723),
    (14, 121, 12, 709),
    (14, 121, 5, 438),
    (14, 121, 6, 782),
    (14, 248, 3, 0),
    (14, 248, 4, 4403),
    (14, 351, 1, 1319),
    (14, 351, 2, 664),
    (14, 352, 7, 581),
    (14, 352, 8, 462),
    (14, 466, 9, 103),
    (14, 598, 5, 59);
    

INSERT INTO fixed_complaint (complaint_details) VALUES
('drives too slow'), ('reckless driving'), ('rude behavior'), ('uncomfortable'),
('bad condition'), ('unpleasant smell'), ('waits too much'), ('other');

INSERT INTO feedback (passenger_id, vehicle_id, reaction) VALUES 
(1, 1, 'thumbs_up'), (2, 1, 'thumbs_up'), (3, 1, 'thumbs_down'),
(2, 2, 'thumbs_down'), (3, 2, 'thumbs_down');

INSERT INTO feedback_fixed_complaint (feedback_id, fixed_complaint_id) VALUES
(3, 1), (3, 2), (3, 3), (4, 1), (4, 5), (4, 6), (5, 1), (5, 5), (5, 6);

INSERT INTO other_complaint (feedback_id, complaint_details) VALUES 
(3, 'other1'), (4, 'other2'), (5, 'other5');

INSERT INTO passenger_saved_route (passenger_id, route_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4);
INSERT INTO passenger_saved_vehicle (passenger_id, vehicle_id, nickname) VALUES
(1, 1, 'HI'), (1, 3, 'BYE');
INSERT INTO passenger_saved_location (passenger_id, longitude, latitude, "name", icon) VALUES
(1, 1, 1, 'Z', 'home'), (1, 2, 1, 'A', 'marker'), (1, 3, 1, 'B', 'home'), (1, 4, 1, 'C', 'school');