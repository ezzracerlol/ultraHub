import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, pyqtSlot


MAP_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>body,html{margin:0;padding:0;background:#1e1f22;}#map{width:100%;height:100vh;}</style>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
<div id="map"></div>
<script>
var map = L.map('map').setView([55.75, 37.61], 15);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'OpenStreetMap'
}).addTo(map);

var trackPoints = [];
var polyline = L.polyline([], {color: '#4fc3f7', weight: 3}).addTo(map);
var droneMarker = null;

var droneIcon = L.divIcon({
    html: '<div style="width:14px;height:14px;background:#f44336;border:2px solid white;border-radius:50%;"></div>',
    iconSize: [14, 14], iconAnchor: [7, 7]
});

function updatePosition(lat, lng) {
    var pos = [lat, lng];
    trackPoints.push(pos);
    polyline.setLatLngs(trackPoints);
    if (!droneMarker) {
        droneMarker = L.marker(pos, {icon: droneIcon}).addTo(map);
    } else {
        droneMarker.setLatLng(pos);
    }
    map.panTo(pos);
}

function clearTrack() {
    trackPoints = [];
    polyline.setLatLngs([]);
    if (droneMarker) { map.removeLayer(droneMarker); droneMarker = null; }
}
</script>
</body>
</html>
"""


class GpsMapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        self.status_label = QLabel("GPS: нет сигнала")
        self.lat_label = QLabel("Lat: --")
        self.lon_label = QLabel("Lon: --")
        self.alt_label = QLabel("Alt: -- м")
        self.sats_label = QLabel("Спутники: --")
        self.clear_btn = QPushButton("Очистить трек")
        self.clear_btn.clicked.connect(self.clear_track)
        for w in [self.status_label, self.lat_label, self.lon_label,
                  self.alt_label, self.sats_label, self.clear_btn]:
            top.addWidget(w)
        top.addStretch()

        self.web = QWebEngineView()
        self.web.setHtml(MAP_HTML, QUrl("http://localhost"))

        layout.addLayout(top)
        layout.addWidget(self.web)

    def update_gps(self, lat, lon, alt, sats, fix):
        fix_str = "Fix" if fix else "No Fix"
        color = "#4caf50" if fix else "#f44336"
        self.status_label.setText(f"GPS: {fix_str}")
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.lat_label.setText(f"Lat: {lat:.6f}")
        self.lon_label.setText(f"Lon: {lon:.6f}")
        self.alt_label.setText(f"Alt: {alt} м")
        self.sats_label.setText(f"Спутники: {sats}")
        if fix and lat != 0 and lon != 0:
            self.web.page().runJavaScript(f"updatePosition({lat}, {lon});")

    def clear_track(self):
        self.web.page().runJavaScript("clearTrack();")