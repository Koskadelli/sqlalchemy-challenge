# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/><br/>"
        f"Dates should be in YYYY-M-D or YYYY-MM-DD format. Valid dates range from 2010-01-01 to 2017-08-23."
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation analysis results"""
    
    # Calculate the date one year from the last date in data set.
    one_year_prior = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation scores for the last year of data
    prcp_query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>=one_year_prior).\
        order_by(Measurement.date.asc()).all()

    # Close Session
    session.close()

    # Convert list of tuples into normal list
    # all_prcp = list(np.ravel(prcp_query))
    all_prcp = []
    for date, prcp in prcp_query:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_prcp.append(precipitation_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all passengers
    results = session.query(Measurement.station).distinct().all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return temperatures from most active station for the last year of data"""
    
    # Calculate the date one year from the last date in data set.
    one_year_prior = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Get the most active station id
    station_id = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Perform a query to retrieve the temps for the last year of data for the most active station
    tobs_query = session.query(Measurement.tobs).\
        filter(Measurement.station==station_id).\
        filter(Measurement.date>=one_year_prior).\
        order_by(Measurement.tobs.asc()).all()

    # Close Session
    session.close()

    # Convert list of tuples into normal list
    all_temps = list(np.ravel(tobs_query))

    return jsonify(all_temps)


@app.route("/api/v1.0/<start>")
def tobs_start(start):
    """Return temperature analysis results for a given start date."""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the temperature info from the given start date onwards
    tobs_start_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date>=start).all()

    # Close Session
    session.close()

    # Convert list of tuples into normal list
    defined_tobs = []
    for min, avg, max in tobs_start_query:
        tobs_dict = {}
        tobs_dict["min"] = min
        tobs_dict["avg"] = avg
        tobs_dict["max"] = max
        defined_tobs.append(tobs_dict)

    return jsonify(defined_tobs)


@app.route("/api/v1.0/<start>/<end>")
def tobs_range(start, end):
    """Return temperature analysis results for between a start and end date."""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the temperature info from the given start date onwards
    tobs_range_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date>=start).\
        filter(Measurement.date<=end).all()

    # Close Session
    session.close()

    # Convert list of tuples into normal list
    defined_tobs = []
    for min, avg, max in tobs_range_query:
        tobs_dict = {}
        tobs_dict["min"] = min
        tobs_dict["avg"] = avg
        tobs_dict["max"] = max
        defined_tobs.append(tobs_dict)

    return jsonify(defined_tobs)

if __name__ == '__main__':
    app.run(debug=True)

