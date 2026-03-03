"""Random US city generator for weather display."""

import random
from typing import Tuple

# List of US cities with coordinates (name, state, latitude, longitude)
# Covers diverse geographic regions across the US
US_CITIES = [
    # Northeast
    ("New York", "NY", 40.7128, -74.0060),
    ("Boston", "MA", 42.3601, -71.0589),
    ("Philadelphia", "PA", 39.9526, -75.1652),
    ("Pittsburgh", "PA", 40.4406, -79.9959),
    ("Buffalo", "NY", 42.8864, -78.8784),
    ("Portland", "ME", 43.6591, -70.2568),
    ("Burlington", "VT", 44.4759, -73.2121),
    
    # Southeast
    ("Miami", "FL", 25.7617, -80.1918),
    ("Atlanta", "GA", 33.7490, -84.3880),
    ("Charlotte", "NC", 35.2271, -80.8431),
    ("Nashville", "TN", 36.1627, -86.7816),
    ("New Orleans", "LA", 29.9511, -90.0715),
    ("Tampa", "FL", 27.9506, -82.4572),
    ("Jacksonville", "FL", 30.3322, -81.6557),
    ("Charleston", "SC", 32.7765, -79.9311),
    ("Savannah", "GA", 32.0809, -81.0912),
    ("Key West", "FL", 24.5551, -81.7800),
    
    # Midwest
    ("Chicago", "IL", 41.8781, -87.6298),
    ("Detroit", "MI", 42.3314, -83.0458),
    ("Minneapolis", "MN", 44.9778, -93.2650),
    ("St. Louis", "MO", 38.6270, -90.1994),
    ("Kansas City", "MO", 39.0997, -94.5786),
    ("Cleveland", "OH", 41.4993, -81.6944),
    ("Cincinnati", "OH", 39.1031, -84.5120),
    ("Indianapolis", "IN", 39.7684, -86.1581),
    ("Milwaukee", "WI", 43.0389, -87.9065),
    ("Madison", "WI", 43.0731, -89.4012),
    ("Des Moines", "IA", 41.5868, -93.6250),
    ("Omaha", "NE", 41.2565, -95.9345),
    ("Fargo", "ND", 46.8772, -96.7898),
    ("Duluth", "MN", 46.7867, -92.1005),
    
    # Southwest
    ("Phoenix", "AZ", 33.4484, -112.0740),
    ("Las Vegas", "NV", 36.1699, -115.1398),
    ("Albuquerque", "NM", 35.0844, -106.6504),
    ("Tucson", "AZ", 32.2226, -110.9747),
    ("El Paso", "TX", 31.7619, -106.4850),
    ("Santa Fe", "NM", 35.6870, -105.9378),
    ("Flagstaff", "AZ", 35.1983, -111.6513),
    
    # Texas
    ("Houston", "TX", 29.7604, -95.3698),
    ("Dallas", "TX", 32.7767, -96.7970),
    ("San Antonio", "TX", 29.4241, -98.4936),
    ("Austin", "TX", 30.2672, -97.7431),
    ("Fort Worth", "TX", 32.7555, -97.3308),
    
    # Mountain/Rocky
    ("Denver", "CO", 39.7392, -104.9903),
    ("Salt Lake City", "UT", 40.7608, -111.8910),
    ("Boise", "ID", 43.6150, -116.2023),
    ("Billings", "MT", 45.7833, -108.5007),
    ("Cheyenne", "WY", 41.1400, -104.8202),
    ("Colorado Springs", "CO", 38.8339, -104.8214),
    ("Missoula", "MT", 46.8721, -113.9940),
    ("Jackson", "WY", 43.4799, -110.7624),
    
    # Pacific Northwest
    ("Seattle", "WA", 47.6062, -122.3321),
    ("Portland", "OR", 45.5152, -122.6784),
    ("Spokane", "WA", 47.6588, -117.4260),
    ("Eugene", "OR", 44.0521, -123.0868),
    ("Tacoma", "WA", 47.2529, -122.4443),
    
    # California
    ("Los Angeles", "CA", 34.0522, -118.2437),
    ("San Francisco", "CA", 37.7749, -122.4194),
    ("San Diego", "CA", 32.7157, -117.1611),
    ("Sacramento", "CA", 38.5816, -121.4944),
    ("San Jose", "CA", 37.3382, -121.8863),
    ("Fresno", "CA", 36.7378, -119.7871),
    ("Oakland", "CA", 37.8044, -122.2712),
    ("Palm Springs", "CA", 33.8303, -116.5453),
    ("Eureka", "CA", 40.8021, -124.1637),
    
    # Alaska
    ("Anchorage", "AK", 61.2181, -149.9003),
    ("Fairbanks", "AK", 64.8378, -147.7164),
    ("Juneau", "AK", 58.3019, -134.4197),
    
    # Hawaii
    ("Honolulu", "HI", 21.3069, -157.8583),
    ("Hilo", "HI", 19.7074, -155.0885),
    ("Kahului", "HI", 20.8893, -156.4729),
    
    # Other interesting places
    ("Death Valley", "CA", 36.5323, -116.9325),
    ("Mount Washington", "NH", 44.2706, -71.3033),
    ("International Falls", "MN", 48.6011, -93.4103),
    ("Barrow", "AK", 71.2906, -156.7886),
    ("Brownsville", "TX", 25.9017, -97.4975),
]


def get_random_city() -> Tuple[str, str, float, float]:
    """Get a random US city.
    
    Returns:
        Tuple of (city_name, state, latitude, longitude)
    """
    return random.choice(US_CITIES)


def get_random_city_name() -> str:
    """Get a formatted random city name.
    
    Returns:
        City name formatted as "City, ST"
    """
    city, state, _, _ = get_random_city()
    return f"{city}, {state}"
