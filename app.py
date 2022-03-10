import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement= Base.classes.measurement
Station= Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
   """List all available api routes."""
   return (
        f"Welcome to my Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
  # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the JSON representation of your dictionary"""
    prev_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    results=session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    
    session.close()

    all_precip=[]
    for date, prcp in results:
        if prcp != None:
            precip_dict={}
            precip_dict["date"]=date
            precip_dict["prcp"]=prcp
            all_precip.append(precip_dict)
    return jsonify(all_precip)
    
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    stations= session.query(Station.station, Station.name, Station.latitude,
                         Station.longitude, Station.elevation).all()
    session.close()

    all_stations=[]
    for station, name, latitude, longitude, elevation in stations:
        station_dict={}
        station_dict ["station"]=station
        station_dict ["name"]=name
        station_dict ["latitude"]=latitude
        station_dict ["longitude"]=longitude
        station_dict ["elevation"]=elevation
        all_stations.append(station_dict)
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
   
    """Query the dates and temperature observations of the most active station 
        for the last year of data."""
    prev_year=dt.date(2017,8,23)-dt.timedelta(days=365)
    most_active=session.query(Measurement.station).group_by(Measurement.station).\
                          order_by(func.count(Measurement.date).desc()).first()
    most_active_ID= most_active [0]

    print(f" The most active station is {most_active_ID}.")

    most_active_stats= session.query(Measurement.date, Measurement.tobs).filter(Measurement.station==most_active_ID).filter(Measurement.date>=prev_year).all()
    
    session.close()

    active_station=[]
    for date, tobs in most_active_stats:
        if tobs != None:
            active_dict={}
            active_dict["date"]=date
            active_dict["tobs"]=tobs
            active_station.append(active_dict)
    return jsonify(active_station)

@app.route("/api/v1.0/<start>",defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""

    """When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date."""

    """When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive."""

    session = Session(engine)

    if end != None:
        temp_data= session.query(func.min(Measurement.tobs), func.max(Measurement.tobs)\
                               ,func.avg(Measurement.tobs)).filter(Measurement.date>= start)\
                                .filter(Measurement.date<=end).all()
    else:
        temp_data=session.query(func.min(Measurement.tobs), func.max(Measurement.tobs)\
                               ,func.avg(Measurement.tobs)).filter(Measurement.date>= start).all()
                               
    session.close()

    temp_list=[]
    no_temp_found= False
    for TMIN, TMAX, TAVG, in temp_data:
        if TMIN== None or TMAX== None or TAVG== None:
            no_temp_found= True
        temp_list.append(TMIN)
        temp_list.append(TMAX)
        temp_list.append(TAVG)

    if no_temp_found == True:
        return f"No temperature data found for your start and end date range. Try another date range."
    else:
        return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)