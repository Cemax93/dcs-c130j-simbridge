"""Coordinate conversion and C-130J route formatting helpers."""

import math
import re
def parse_coordinate(val):
    """Parses a coordinate into decimal degrees."""
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip()
    try:
        return float(val_str)
    except ValueError:
        pass

    m1 = re.match(r"^([NSEWnsew])\s*(\d{1,3})[\^°\s]+(\d+(?:\.\d+)?)\'?$", val_str)
    if m1:
        hemi = m1.group(1).upper()
        deg, minute = float(m1.group(2)), float(m1.group(3))
        dec = deg + (minute / 60.0)
        return -dec if hemi in ("S", "W") else dec

    m2 = re.match(r"^(\d{1,3})[\^°\s]+(\d+(?:\.\d+)?)\'?\s*([NSEWnsew])$", val_str)
    if m2:
        deg, minute, hemi = float(m2.group(1)), float(m2.group(2)), m2.group(3).upper()
        dec = deg + (minute / 60.0)
        return -dec if hemi in ("S", "W") else dec

    raise ValueError(f"Cannot parse coordinate string: '{val}'")


def dec_to_c130_coord(lat, lon):
    """Converts decimal lat/lon to C-130J CNI-MU format: N45^00.29 E037^20.88"""
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"
    lat_abs = abs(lat)
    lon_abs = abs(lon)
    lat_deg = int(lat_abs)
    lat_min = (lat_abs - lat_deg) * 60.0
    lon_deg = int(lon_abs)
    lon_min = (lon_abs - lon_deg) * 60.0
    return f"{lat_dir}{lat_deg:02d}^{lat_min:05.2f} {lon_dir}{lon_deg:03d}^{lon_min:05.2f}"


def calculate_distance_nm(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points in Nautical Miles."""
    r_nm = 3440.065
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2.0) ** 2)
    return r_nm * (2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a))))


def generate_approach_fix(lat, lon, rwy_str, dist_nm=10.0):
    """Calculates FAF coordinates on extended runway centerline."""
    m = re.search(r"(\d+)", str(rwy_str))
    if not m:
        return None
    rwy_num = int(m.group(1))
    hdg_deg = (rwy_num * 10) % 360
    reciprocal_brng = (hdg_deg + 180) % 360

    r_km = 6371.0
    dist_km = dist_nm * 1.852
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    brng = math.radians(reciprocal_brng)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(dist_km / r_km) +
        math.cos(lat1) * math.sin(dist_km / r_km) * math.cos(brng)
    )
    lon2 = lon1 + math.atan2(
        math.sin(brng) * math.sin(dist_km / r_km) * math.cos(lat1),
        math.cos(dist_km / r_km) - math.sin(lat1) * math.sin(lat2)
    )
    return math.degrees(lat2), math.degrees(lon2)


def format_c130_waypoint(name, wp_type, lat, lon, rwy="", elev="-999"):
    """Formats a waypoint record string for C-130J CNI routes table."""
    flag_10 = 1 if wp_type in (1, 2) else 0
    flag_29 = 0 if wp_type == 2 else 1
    rwy_str = f"{rwy:>7}" if rwy else "       "
    elev_str = f"{elev:>5}" if str(elev) != "-999" else " -999"
    return (
        f"({name}|{wp_type}|{lat: 9.5f}|{lon: 9.5f}|  0|0|-999|0||3|"
        f"{flag_10}|{rwy_str}|      |      |      |-99|-99|0|0|000000|      |"
        f"  0.0|    0|-99999|0|0|0|0|    0|    0|    0|    0|    0|{flag_29}|"
        f"0|    0|{elev_str}|    0| -999|    0)"
    )


# -----------------------------------------------------------------------------
# DIALOG FOR ADDING / EDITING WAYPOINTS
# -----------------------------------------------------------------------------
