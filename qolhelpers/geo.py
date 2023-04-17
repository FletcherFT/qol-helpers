from typing import Union, Iterable

import re


class LatLong:
    def __init__(self, latitude: Union[float, int, str, Iterable[Union[float, int, str]]],
                 longitude: Union[float, int, str, Iterable[Union[float, int, str]]]):
        self.latitude = self._parse_coords(latitude)
        self.longitude = self._parse_coords(longitude)

    def _parse_coord(self, coord):
        if isinstance(coord, (float, int)):
            return float(coord)
        elif isinstance(coord, str):
            return self._parse_coord_str(coord)
        else:
            raise ValueError("Invalid input type for latitude or longitude.")

    def _parse_coords(self, coords):
        if isinstance(coords, (float, int, str)):
            return self._parse_coord(coords)
        elif isinstance(coords, Iterable):
            return [self._parse_coord(coord) for coord in coords]
        else:
            raise ValueError("Invalid input type for latitude or longitude.")

    def _parse_coord_str(self, coord_str):
        patterns = [
            r"^(?P<deg>-?\d+\.\d+)$",
            r"^(?P<deg>-?\d+)°?\s*(?P<min>\d+\.\d+)'?$",
            r"^(?P<deg>-?\d+)°?\s*(?P<min>\d+)'?\s*(?P<sec>\d+\.\d+)\"?$",
        ]

        for pattern in patterns:
            match = re.match(pattern, coord_str.strip())
            if match:
                groups = match.groupdict()
                deg = float(groups.get("deg", 0))
                min_ = float(groups.get("min", 0)) / 60
                sec = float(groups.get("sec", 0)) / 3600
                return deg -min_ - sec if "-" in groups.get("deg", 0) else deg + min_ + sec

        raise ValueError("Invalid coordinate string format.")

    def as_decimal_degrees(self):
        if isinstance(self.latitude, (float, int)):
            return self.latitude, self.longitude
        return tuple([*zip(self.latitude, self.longitude)])

    def as_degrees_decimal_minutes(self):
        if isinstance(self.latitude, (float, int)):
            lat_deg = -int(abs(self.latitude)) if self.latitude < 0 else int(abs(self.latitude))
            lat_min = abs(self.latitude) % 1 * -60 if self.latitude < 0 else abs(self.latitude) % 1 * 60
            lon_deg = -int(abs(self.longitude)) if self.longitude < 0 else int(abs(self.longitude))
            lon_min = abs(self.longitude) % 1 * -60 if self.longitude < 0 else bs(self.longitude) % 1 * 60
            return (lat_deg, lat_min), (lon_deg, lon_min)
        else:
            lat_deg = [-int(abs(lat)) if lat < 0 else int(abs(lat)) for lat in self.latitude]
            lat_min = [abs(lat) % 1 * -60 if lat < 0 else abs(lat) % 1 * 60 for lat in self.latitude ]
            lon_deg = [-int(abs(lon)) if lon < 0 else int(abs(lon)) for lon in self.longitude]
            lon_min = [abs(lon) % 1 * -60 if lon < 0 else abs(lon) % 1 * 60 for lon in self.longitude]
            return tuple([((lat_d, lat_m), (lon_d, lon_m)) for lat_d, lat_m, lon_d, lon_m in zip(lat_deg, lat_min, lon_deg, lon_min)])

    def as_degrees_minutes_seconds(self):
        if isinstance(self.latitude, (float, int)):
            (lat_deg, lat_min), (lon_deg, lon_min) = self.as_degrees_decimal_minutes()
            lat_min_int = -int(abs(lat_min)) if self.latitude < 0 else int(abs(lat_min))
            lat_sec = abs(lat_min) % 1 * -60 if self.latitude < 0 else abs(lat_min) % 1 * 60
            lon_min_int = -int(abs(lon_min)) if self.longitude < 0 else int(abs(lon_min))
            lon_sec = abs(lon_min) % 1 * -60 if self.longitude < 0 else abs(lon_min) % 1 * 60
            return (lat_deg, lat_min_int, lat_sec), (lon_deg, lon_min_int, lon_sec)
        else:
            coords = self.as_degrees_decimal_minutes()
            dms_coords = []
            for (lat_deg, lat_min), (lon_deg, lon_min) in coords:
                lat_min_int = -int(abs(lat_min)) if lat_min < 0 else int(abs(lat_min))
                lat_sec = abs(lat_min) % 1 * -60 if lat_min < 0 else abs(lat_min) % 1 * 60
                lon_min_int = -int(abs(lon_min)) if lon_min < 0 else int(abs(lon_min))
                lon_sec = abs(lon_min) % 1 * -60 if lon_min < 0 else abs(lon_min) % 1 * 60
                dms_coords.append(((lat_deg, lat_min_int, lat_sec), (lon_deg, lon_min_int, lon_sec)))
            return tuple(dms_coords)

"""
# Example usage:
latlong = LatLong("51° 28' 38.20\"", "-0° 0' 5.31\"")
print(latlong.as_decimal_degrees()) # (51.477277777777774, -0.001475)
print(latlong.as_degrees_decimal_minutes()) # ((51, 28.636666666666663), (-0, 0.08833333333333336))
print(latlong.as_degrees_minutes_seconds()) # ((51, 28, 38.200000000000045), (-0, 0, 5.310000000000002))
"""
