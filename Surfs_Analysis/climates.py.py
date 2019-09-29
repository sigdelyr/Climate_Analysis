# import dependencies 
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
Base.classes.keys()

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)
engine.execute('SELECT * FROM Station LIMIT 5').fetchall()
engine.execute('SELECT * FROM Measurement LIMIT 5').fetchall()

# Flask Setup
#############
app = Flask(__name__)

##############
# Flask Routes
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation fall for last year"""

    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp_record = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > year_ago).\
    order_by(Measurement.date).all()
# Create a list of dicts with `date` and `prcp` as the keys and values
    precipitation_total = []
    for p in prcp_record:
        prcp_dict = {}
        prcp_dict["date"] = p.date
        prcp_dict["prcp"] = p.prcp
        precipitation_total.append(prcp_dict)

    return jsonify(precipitation_total)


######################
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
   
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    most_active_station = active_stations[0][0]
    temp_observations = session.query(Measurement.tobs).\
                                filter(Measurement.station==most_active_station).\
                                filter(Measurement.date >= year_ago).\
                                order_by(Measurement.date.desc()).all()
# Create a list of dicts with `date` and `tobs`
    temperature_totals = []
    for t in temp_observations:
        temp_dict = {}
        temp_dict["date"] = t.date[0]
        temp_dict["tobs"] = t.tobs[1]
        temperature_totals.append(temp_dict)

    return jsonify(temperature_totals)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    
    # Convert list of tuples into normal list
    temp_start = list(np.ravel(results))

    return jsonify(temp_start)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    """ Calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    
    # Convert list of tuples into normal list
    temp_start_end = list(np.ravel(results))

    return jsonify(temp_start_end)


if __name__ == "__main__":
    app.run(debug=True)

