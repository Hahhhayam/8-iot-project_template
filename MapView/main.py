import asyncio
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy_garden.mapview import MapMarker, MapView

from datasource import Datasource
from lineMapLayer import LineMapLayer


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        base_dir = Path(__file__).resolve().parent
        images_dir = base_dir / "images"

        self.datasource = Datasource(user_id=1)
        self.car_marker = MapMarker(source=str(images_dir / "car.png"))
        self.route_layer = LineMapLayer()
        self.pothole_markers = []
        self.bump_markers = []
        self._has_centered_map = False
        self._update_event = None
        self._marker_sources = {
            "pothole": str(images_dir / "pothole.png"),
            "bump": str(images_dir / "bump.png"),
        }

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        self.mapview.add_layer(self.route_layer, mode="scatter")
        self.mapview.add_marker(self.car_marker)
        self._update_event = Clock.schedule_interval(self.update, 0.5)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        new_points = self.datasource.get_new_points()
        if not new_points:
            return

        for point in new_points:
            lat, lon, road_state = point
            self.route_layer.add_point((lat, lon))
            self.update_car_marker((lat, lon))

            if road_state == "pothole":
                self.set_pothole_marker((lat, lon))
            elif road_state == "bump":
                self.set_bump_marker((lat, lon))

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        lat, lon = point
        self.car_marker.lat = lat
        self.car_marker.lon = lon

        if not self._has_centered_map:
            self.mapview.center_on(lat, lon)
            self._has_centered_map = True

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """
        marker = MapMarker(lat=point[0], lon=point[1], source=self._marker_sources["pothole"])
        self.pothole_markers.append(marker)
        self.mapview.add_marker(marker)

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """
        marker = MapMarker(lat=point[0], lon=point[1], source=self._marker_sources["bump"])
        self.bump_markers.append(marker)
        self.mapview.add_marker(marker)

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.mapview = MapView(zoom=16, lat=50.4501, lon=30.5234)
        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
