from flask import Flask, request, jsonify

app = Flask(__name__)

# Stockage temporaire des coordonnées
destination_coords = {}

@app.route('/destination', methods=['POST'])
def receive_coordinates():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is not None and longitude is not None:
        destination_coords['latitude'] = latitude
        destination_coords['longitude'] = longitude
        print(f"✅ Coordonnées reçues : lat={latitude}, lon={longitude}")
        return jsonify({"message": "Coordonnées enregistrées avec succès"}), 200
    else:
        return jsonify({"error": "Latitude ou longitude manquante"}), 400

@app.route('/destination', methods=['GET'])
def get_coordinates():
    if destination_coords:
        return jsonify(destination_coords), 200
    else:
        return jsonify({"error": "Aucune coordonnée disponible"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
# http://192.168.43.218:5000/destination pour l'appareil 
# http://127.0.0.1:5000/destination pour la raspberry par exemple 