import unittest
from qolhelpers.geo import LatLong


class TestLatLong(unittest.TestCase):
    def setUp(self) -> None:
        self._lat_dd = 51.477277777777774
        self._lon_dd = -0.001475
        self._lat_ddm = (51, 28.63667)
        self._lon_ddm = (-0, -0.0885)
        self._lat_dms = (51, 28, 38.2)
        self._lon_dms = (-0, -0, -5.31)
        self._lats_dd = [51.477277777777774, -012.3456789]
        self._lons_dd = [-0.001475, 0.123456789]
        self._lats_ddm = [(51, 28.63667), (-12, -20.740734)]
        self._lons_ddm = [(-0, -0.0885), (0, 7.40740734)]
        self._lats_dms = [(51, 28, 38.2), (-12, -20, -44.44404)]
        self._lons_dms = [(-0, -0, -5.31), (0, 7, 24.4444404)]

    def test_array_input_decimal_degrees(self):
        latlong = LatLong(self._lats_dd, self._lons_dd)
        for i, (lat, lon) in enumerate(zip(latlong.latitude, latlong.longitude)):
            self.assertAlmostEqual(lat, self._lats_dd[i])
            self.assertAlmostEqual(lon, self._lons_dd[i])

    def test_array_input_degrees_decimal_minutes(self):
        latlong = LatLong(["51° 28.63667'", "-012° 20.740734'"], ["-0° 0.0885'", "0° 7.40740734'"])
        for i, (lat, lon) in enumerate(zip(latlong.latitude, latlong.longitude)):
            self.assertAlmostEqual(lat, self._lats_dd[i], places=5)
            self.assertAlmostEqual(lon, self._lons_dd[i], places=5)

    def test_array_input_degrees_minutes_seconds(self):
        latlong = LatLong(["51° 28' 38.20\"", "-012° 20' 44.44404\""], ["-0° 0' 5.31\"", "0° 7' 24.4444404\""])
        for i, (lat, lon) in enumerate(zip(latlong.latitude, latlong.longitude)):
            self.assertAlmostEqual(lat, self._lats_dd[i], places=5)
            self.assertAlmostEqual(lon, self._lons_dd[i], places=5)

    def test_as_decimal_degrees_array(self):
        latlong = LatLong(self._lats_dd, self._lons_dd)
        coords = latlong.as_decimal_degrees()
        for i, (lat, lon) in enumerate(coords):
            self.assertAlmostEqual(lat, self._lats_dd[i])
            self.assertAlmostEqual(lon, self._lons_dd[i])

    def test_as_degrees_decimal_minutes_array(self):
        latlong = LatLong(self._lats_dd, self._lons_dd)
        coords = latlong.as_degrees_decimal_minutes()
        for i, ((lat_deg, lat_min), (lon_deg, lon_min)) in enumerate(coords):
            self.assertEqual(lat_deg, self._lats_ddm[i][0])
            self.assertAlmostEqual(lat_min, self._lats_ddm[i][1], places=5)
            self.assertEqual(lon_deg, self._lons_ddm[i][0])
            self.assertAlmostEqual(lon_min, self._lons_ddm[i][1], places=5)

    def test_as_degrees_minutes_seconds_array(self):
        latlong = LatLong(self._lats_dd, self._lons_dd)
        coords = latlong.as_degrees_minutes_seconds()
        for i, ((lat_deg, lat_min, lat_sec), (lon_deg, lon_min, lon_sec)) in enumerate(coords):
            self.assertEqual(lat_deg, self._lats_dms[i][0])
            self.assertEqual(lat_min, self._lats_dms[i][1])
            self.assertAlmostEqual(lat_sec, self._lats_dms[i][2], places=2)
            self.assertEqual(lon_deg, self._lons_dms[i][0])
            self.assertEqual(lon_min, self._lons_dms[i][1])
            self.assertAlmostEqual(lon_sec, self._lons_dms[i][2], places=2)

    def test_decimal_degrees_input(self):
        latlong = LatLong(self._lat_dd, self._lon_dd)
        self.assertAlmostEqual(latlong.latitude, self._lat_dd)
        self.assertAlmostEqual(latlong.longitude, self._lon_dd)

    def test_degrees_decimal_minutes_input(self):
        latlong = LatLong("51° 28.63667'", "-0° 0.08833'")
        self.assertAlmostEqual(latlong.latitude, self._lat_dd, places=5)
        self.assertAlmostEqual(latlong.longitude, self._lon_dd, places=5)
        latlong = LatLong("51 28.63667", "-0 0.08833")
        self.assertAlmostEqual(latlong.latitude, self._lat_dd, places=5)
        self.assertAlmostEqual(latlong.longitude, self._lon_dd, places=5)

    def test_degrees_minutes_seconds_input(self):
        latlong = LatLong("51° 28' 38.20\"", "-0° 0' 5.31\"")
        self.assertAlmostEqual(latlong.latitude, self._lat_dd, places=5)
        self.assertAlmostEqual(latlong.longitude, self._lon_dd, places=5)
        latlong = LatLong("51 28 38.20", "-0 0 5.31")
        self.assertAlmostEqual(latlong.latitude, self._lat_dd, places=5)
        self.assertAlmostEqual(latlong.longitude, self._lon_dd, places=5)

    def test_as_decimal_degrees(self):
        latlong = LatLong(self._lat_dd, self._lon_dd)
        lat, lon = latlong.as_decimal_degrees()
        self.assertAlmostEqual(lat, self._lat_dd)
        self.assertAlmostEqual(lon, self._lon_dd)

    def test_as_degrees_decimal_minutes(self):
        latlong = LatLong(self._lat_dd, self._lon_dd)
        (lat_deg, lat_min), (lon_deg, lon_min) = latlong.as_degrees_decimal_minutes()
        self.assertEqual(lat_deg, self._lat_ddm[0])
        self.assertAlmostEqual(lat_min, self._lat_ddm[1], places=5)
        self.assertEqual(lon_deg, self._lon_ddm[0])
        self.assertAlmostEqual(lon_min, self._lon_ddm[1], places=5)

    def test_as_degrees_minutes_seconds(self):
        latlong = LatLong(self._lat_dd, self._lon_dd)
        (lat_deg, lat_min, lat_sec), (lon_deg, lon_min, lon_sec) = latlong.as_degrees_minutes_seconds()
        self.assertEqual(lat_deg, self._lat_dms[0])
        self.assertEqual(lat_min, self._lat_dms[1])
        self.assertAlmostEqual(lat_sec, self._lat_dms[2])
        self.assertEqual(lon_deg, self._lon_dms[0])
        self.assertEqual(lon_min, self._lon_dms[1])
        self.assertAlmostEqual(lon_sec, self._lon_dms[2])


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
