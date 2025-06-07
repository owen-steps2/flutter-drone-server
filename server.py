from flask import Flask, request, jsonify

app = Flask(__name__)

# Stockage temporaire
destination_coords = {}
drone_coords = {}

# ======= Téléphone vers serveur =======
@app.route('/destination', methods=['POST'])
def receive_coordinates():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is not None and longitude is not None:
        destination_coords['latitude'] = latitude
        destination_coords['longitude'] = longitude
        print(f"✅ Coordonnées téléphone reçues : lat={latitude}, lon={longitude}")
        return jsonify({"message": "Coordonnées du téléphone enregistrées"}), 200
    else:
        return jsonify({"error": "Latitude ou longitude manquante"}), 400

@app.route('/destination', methods=['GET'])
def get_coordinates():
    if destination_coords:
        return jsonify(destination_coords), 200
    else:
        return jsonify({"error": "Aucune coordonnée disponible"}), 404

# ======= Drone vers serveur =======
@app.route('/drone_location', methods=['POST'])
def receive_drone_position():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is not None and longitude is not None:
        drone_coords['latitude'] = latitude
        drone_coords['longitude'] = longitude
        print(f"📡 Position du drone reçue : lat={latitude}, lon={longitude}")
        return jsonify({"message": "Position du drone enregistrée"}), 200
    else:
        return jsonify({"error": "Latitude ou longitude manquante"}), 400

@app.route('/drone_location', methods=['GET'])
def get_drone_position():
    if drone_coords:
        return jsonify(drone_coords), 200
    else:
        return jsonify({"error": "Aucune position drone disponible"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
