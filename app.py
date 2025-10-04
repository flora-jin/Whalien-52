import folium
from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Set up a simple SQLite database for whale sightings (optional)
DATABASE = './db/sightings.db'

# Create a database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

# Create the sightings table with the correct columns
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS sightings (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT,
                latitude REAL,
                longitude REAL,
                date TIMESTAMP
            )
        ''')
        db.commit()


# Home route - display the map
@app.route('/')
def home():
    # Set up the base map centered on a location (e.g., Vancouver, BC)
    m = folium.Map(location=[49.2827, -123.1207], zoom_start=12)

    # Add ship tracking markers
    ships = get_ships_nearby()
    for ship in ships:
        folium.Marker([ship['latitude'], ship['longitude']], popup=f"Ship: {ship['name']}").add_to(m)

    # Add whale sightings from the database
    sightings = get_whale_sightings()
    for sighting in sightings:
        folium.Marker([sighting['latitude'], sighting['longitude']],
                      popup=f"Whale spotted by {sighting['name']} on {sighting['date']}",
                      icon=folium.Icon(color='blue')).add_to(m)

    # Generate the map HTML representation
    map_html = m._repr_html_()
    return render_template('index.html', map_html=map_html)

# Route to report a whale sighting
@app.route('/report', methods=['POST'])
def report_sighting():
    name = request.form.get('name')
    location = request.form.get('location')
    latitude = float(request.form.get('latitude'))
    longitude = float(request.form.get('longitude'))
    
    # Store the whale sighting in the database
    db = get_db()
    db.execute('''INSERT INTO sightings (name, location, latitude, longitude, date) 
                  VALUES (?, ?, ?, ?, ?)''', 
               (name, location, latitude, longitude, datetime.now()))
    db.commit()

    return jsonify({"status": "success", "message": "Sighting reported successfully!"})

# Function to get live ship data using MarineTraffic API
def get_ships_nearby():
    # Replace with actual API call to MarineTraffic or any other ship tracking service
    # Here, we are just simulating with some dummy data
    ships = [
        {"name": "Ship 1", "latitude": 49.281, "longitude": -123.122},
        {"name": "Ship 2", "latitude": 49.283, "longitude": -123.121}
    ]
    return ships

# Function to get all whale sightings from the database
def get_whale_sightings():
    db = get_db()
    cursor = db.execute('SELECT name, location, latitude, longitude, date FROM sightings')
    sightings = cursor.fetchall()
    return [{"name": row[0], "location": row[1], "latitude": row[2], "longitude": row[3], "date": row[4]} for row in sightings]

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
