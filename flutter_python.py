from dronekit import connect, VehicleMode, LocationGlobalRelative
from flask import Flask, request, jsonify
import threading
import time
from math import radians, sin, cos, sqrt, atan2

# Stockage des coordonnées
latest_coordinates = {"lat": None, "lon": None}

# Fonction pour calculer la distance entre deux points GPS
def get_distance_metres(location1, lat2, lon2):
    lat1 = radians(location1.lat)
    lon1 = radians(location1.lon)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    r = 6371000  # Rayon de la Terre en mètres
    return c * r

# Flask pour recevoir les coordonnées depuis Flutter
app = Flask(__name__)

@app.route('/destination', methods=['POST'])
def receive_coordinates():
    data = request.get_json()
    latest_coordinates["lat"] = data.get("latitude")
    latest_coordinates["lon"] = data.get("longitude")
    print(f"✅ Coordonnées reçues : {latest_coordinates}")
    return jsonify({"message": "Coordonnées reçues"}), 200

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Lancer Flask dans un thread séparé
threading.Thread(target=run_flask, daemon=True).start()

# Connexion au drone
print("🔗 Connexion au drone...")
vehicle = connect('tcp:127.0.0.1:5763', wait_ready=True)

# Attente du GPS
print("🛰️ En attente d’un signal GPS valide...")
while vehicle.gps_0.fix_type < 2:
    print("Recherche GPS...")
    time.sleep(1)

# Définir la position de départ
home_location = vehicle.location.global_frame
print(f"🏠 Position de base : lat={home_location.lat}, lon={home_location.lon}")

# Attente des coordonnées de destination
print("⏳ En attente des coordonnées de destination depuis Flutter...")
while latest_coordinates["lat"] is None or latest_coordinates["lon"] is None:
    time.sleep(1)

target_lat = latest_coordinates["lat"]
target_lon = latest_coordinates["lon"]
print(f"📍 Destination reçue : Latitude = {target_lat}, Longitude = {target_lon}")

# Passage en GUIDED
print("🧭 Passage en mode GUIDED...")
vehicle.mode = VehicleMode("GUIDED")
time.sleep(2)

# Armement
print("🔐 Armement...")
vehicle.armed = True
while not vehicle.armed:
    print("⏳ Attente de l’armement...")
    time.sleep(1)
print("✅ Drone armé.")

# Décollage
altitude_cible = 20
print(f"🚁 Décollage à {altitude_cible} m...")
vehicle.simple_takeoff(altitude_cible)

while True:
    altitude_actuelle = vehicle.location.global_relative_frame.alt
    print(f"Altitude : {altitude_actuelle:.2f} m")
    if altitude_actuelle >= altitude_cible * 0.95:
        print("✅ Altitude atteinte.")
        break
    time.sleep(1)

# Vol vers la destination
print("➡️ En route vers la destination...")
target_location = LocationGlobalRelative(target_lat, target_lon, altitude_cible)
vehicle.simple_goto(target_location)

while True:
    distance = get_distance_metres(vehicle.location.global_frame, target_lat, target_lon)
    print(f"📡 Distance à la cible : {distance:.2f} m")
    print(f"Position : lat={vehicle.location.global_frame.lat}, lon={vehicle.location.global_frame.lon}")
    print(f"Altitude : {vehicle.location.global_relative_frame.alt:.2f} m | Batterie : {vehicle.battery.level}% | Vitesse : {vehicle.groundspeed:.2f} m/s")
    if distance < 5:
        print("🎯 Destination atteinte.")
        break
    time.sleep(1)

# Retour à la base
print("↩️ Retour à la base...")
vehicle.simple_goto(LocationGlobalRelative(home_location.lat, home_location.lon, altitude_cible))

while True:
    distance_home = get_distance_metres(vehicle.location.global_frame, home_location.lat, home_location.lon)
    print(f"🏠 Distance au point de départ : {distance_home:.2f} m")
    if distance_home < 5:
        print("✅ Retour atteint.")
        break
    time.sleep(1)

# Atterrissage
print("🛬 Atterrissage...")
vehicle.mode = VehicleMode("LAND")
while vehicle.armed:
    print(f"Altitude en descente : {vehicle.location.global_relative_frame.alt:.2f} m")
    time.sleep(1)

# Fin de mission
print("✅ Mission terminée. Déconnexion.")
vehicle.close()
