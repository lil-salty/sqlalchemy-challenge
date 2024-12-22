# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import json
from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station =  Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

#Homepage route, list all available routes
@app.route("/")

def home():
    return (
        f"Climate Analysis Homepage<br/>"
        f"Available Routes:br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


#Precipitation route, last 12 months of precipitation data
@app.route("/api/v1.0/precipitation")

def precipitation():

    most_recent_date = (
        session.query(func.max(Measurement.date))
        .scalar()
    )
    prcp_results = (
        session.query(Measurement.date, Measurement.prcp)
        .all()
    )

    session.close()

    prcp_data = []

    for prcp in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = most_recent_date
        prcp_dict["precipitation"] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)



#Stations route, list of all stations
@app.route("/api/v1.0/stations")

def stations():
    
    stations_results = (
        session.query(stations.station, stations.name, stations.latitude, stations.longitude, stations.elevation)
        .all()
    )

    session.close()

    stations_data = []

    for id, name, lat, long, elev in stations_results:
        stations_dict = {
            id: { "Name": name, "Latitude": lat, "Longitude": long, "Elevation": elev}
        }
        stations_data.append(stations_dict)

    return jsonify(stations_data)


    


#tobs route, list of dates and temperature observations from the most active station for the last year
@app.route("/api/v1.0/tobs")

def tobs():

    active_station = (
        session.query(Measurement.station, func.count(Measurement.station))
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station)
                  .desc())
                  .first()
    )

    most_active = active_station[0]

    end_date = session.query(func.max(Measurement.date)).scalar()
    start_date = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days=365)

    session.close()

    tobs_results = (
        session.query(Measurement.tobs)
        .filter(Measurement.station == most_active)
        .filter(Measurement.date >= start_date)
        .order_by(Measurement.date.desc())
        .all()
    )

    tobs_list = [{"Date": tobs[0], "Temperature": tobs[1]} for tobs in tobs_results]

    return jsonify(tobs_list)



@app.route('/api/v1.0/<start>')

def temps_start(start):
    session = Session(engine)

    start_results = (
        session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))
        .filter(Measurement.date >= start)
        .all()
    )

    session.close()

    start_temps = []
    
    for min, max, avg in start_results:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = min
        temp_dict["Maximum Temperature"] = max
        temp_dict["Average Temperature"] = avg
        start_temps.append(temp_dict)

    return jsonify(start_temps)


@app.route('/api/v1.0/<start>/<end>')
def temp_start_end(start, end):
    session = Session(engine)

    start_end_results = (
        session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .all()
    )

    session.close()

    start_end_temps = []
    
    for min, max, avg in start_end_results:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = min
        temp_dict["Maximum Temperature"] = max
        temp_dict["Average Temperature"] = avg
        start_end_temps.append(temp_dict)

    return jsonify(start_end_temps)
    
    
if __name__ == '__main__':
    app.run(debug=True)