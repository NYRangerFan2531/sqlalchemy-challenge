# Import the dependencies.
import sqlalchemy
from sqlalchemy import create_engine,func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from flask import Flask, jsonify

import numpy as np
#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session {Session will be created an closed in every route}

###session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
# Using "&lt;" so that HTML will convert to "<" and "&gt;" to ">"
def home():
    """List all the available routes"""
    return (
        f"Welcome to the Climate App API<br/>"
        f"===========================<br/>"
        f"Avaliable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Convert the query results from your precipitation analysis 
    (i.e. retrieve only the last 12 months of data) to a dictionary 
    using date as the key and prcp as the value."""

    # Create a session
    session = Session(engine)
    # Preform Query from SQLite Data Base
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()

    # Close the Session
    session.close()

    # Convert data to a list for output
    all_precipation=[]    

    for (date, prcp) in data:
        precipitation_dict={date:prcp}
        all_precipation.append(precipitation_dict)
    
    # Return Data as a JSON   
    return jsonify(all_precipation)

@app.route("/api/v1.0/stations")
def stations():

    """Return a JSON list of stations from the dataset"""

    # Create a session
    session = Session(engine)

    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).distinct().all()
    
    # Close the Session
    session.close()

    # Create a Dictonary of the row fata and append to station_list
    stations_list = []

    for (station,name,latitude,longitude,elevation) in results:
        station_dict={
            "ID" : station,
            "Name": name,
            "Latitude": latitude,
            "Longitude": longitude,
            "Elevation": elevation
        }
        stations_list.append(station_dict)
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():

    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    
    # Create a session
    session = Session(engine)

    # Find the most active station 
    station_query = [Measurement.station, func.count(Measurement.station)]
    
    station_active = session.query(*station_query).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc())\
        .all()
    
    #Isolate the ID of the most active station
    station_id_most_active = station_active[0][0]

    # Query to get the Date and the Tempature of the Most Active Station
    data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == station_id_most_active).filter(Measurement.date >= '2016-08-23').all()

    # Close the Session
    session.close()

    # Create a Dictonary of the row fata and append to tobs_mostactive
    tobs_mostactive=[]    

    for (date, tobs) in data:
        tobs_dict={}
        tobs_dict["Date"] = date
        tobs_dict["tobs"] = tobs
        tobs_mostactive.append(tobs_dict)
    
    # Return as a JSON
    return jsonify(tobs_mostactive)

@app.route('/api/v1.0/<start>')
def tempature_stats1(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start range."""
    # Create a session
    session = Session(engine)

    # Design Query for minimum temperature, the average temperature, and the maximum temperature
    query = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    
    # Query the data on or after the user-pasted in start date
    tobs_data = session.query(*query).filter(Measurement.date >= start)

    # Close the Session
    session.close()

    # Create a Dictonary of the row fata and append to tobs_all
    tobs_all =[]

    for min,max,avg in tobs_data:
        tobs_dict={}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Avg"] = avg

        tobs_all.append(tobs_dict)

    # Return as a JSON
    return jsonify(tobs_all)

@app.route('/api/v1.0/<start>/<stop>')
def tempature_stats2(start,stop):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range."""

    # Create a session
    session = Session(engine)

    # Design Query for minimum temperature, the average temperature, and the maximum temperature
    query = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    
    # Query the data on or after the user-pasted in start date and before or on the stop date
    tobs_data = session.query(*query).filter(Measurement.date >= start).filter(Measurement.date <= stop).all()

    # Close the Session
    session.close()

    # Create a Dictonary of the row fata and append to tobs_all
    tobs_all =[]

    for min,max,avg in tobs_data:
        tobs_dict={}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Avg"] = avg

        tobs_all.append(tobs_dict)


    return jsonify(tobs_all)

#################################################
# Flask Main
#################################################
if __name__ == "__main__":
    app.run(debug=True)
