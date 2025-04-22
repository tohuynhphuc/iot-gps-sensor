import math
from datetime import datetime, timedelta

def haversine(lat1, lon1, lat2, lon2):
    R = 6371e3
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def interpolate_coords(start, end, num_points):
    lat1, lon1 = start
    lat2, lon2 = end
    return [
        (
            lat1 + (lat2 - lat1) * i / (num_points - 1),
            lon1 + (lon2 - lon1) * i / (num_points - 1)
        )
        for i in range(num_points)
    ]

def decimal_to_nmea_lat(deg):
    d = int(abs(deg))
    m = (abs(deg) - d) * 60
    return f"{d:02d}{m:07.4f}"

def decimal_to_nmea_lon(deg):
    d = int(abs(deg))
    m = (abs(deg) - d) * 60
    return f"{d:03d}{m:07.4f}"

def calculate_checksum(nmea_sentence):
    checksum = 0
    for char in nmea_sentence[1:]:  # skip the initial '$'
        checksum ^= ord(char)
    return f"*{checksum:02X}"

def generate_nmea_gga(lat, lon, timestamp):
    lat_hem = 'N' if lat >= 0 else 'S'
    lon_hem = 'E' if lon >= 0 else 'W'
    lat_nmea = decimal_to_nmea_lat(lat)
    lon_nmea = decimal_to_nmea_lon(lon)
    time_str = timestamp.strftime("%H%M%S")
    sentence_body = f"GPGGA,{time_str}.00,{lat_nmea},{lat_hem},{lon_nmea},{lon_hem},1,08,0.9,10.0,M,46.9,M,,"
    checksum = calculate_checksum(f"${sentence_body}")
    return f"${sentence_body}{checksum}"

def generate_path_nmea(waypoints, total_points):
    segment_lengths = [haversine(*waypoints[i], *waypoints[i+1]) for i in range(len(waypoints)-1)]
    total_length = sum(segment_lengths)
    segment_points = [max(2, round((length / total_length) * total_points)) for length in segment_lengths]
    difference = total_points - sum(segment_points)
    segment_points[0] += difference

    all_points = []
    for i in range(len(waypoints) - 1):
        points = interpolate_coords(waypoints[i], waypoints[i+1], segment_points[i])
        if i != 0:
            points = points[1:]
        all_points.extend(points)

    now = datetime.utcnow()
    nmea_sentences = [generate_nmea_gga(lat, lon, now + timedelta(seconds=i)) for i, (lat, lon) in enumerate(all_points)]
    return nmea_sentences

waypoints = [
    
]

nmea_data = generate_path_nmea(waypoints, 100)
filename = "output_demo.nmea"
# Write to file
with open(filename, "w") as f:
    for line in nmea_data:
        f.write(line + "\n")

print("NMEA data written to", filename)
