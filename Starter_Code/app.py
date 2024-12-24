# Import the dependencies.
import datetime as dt
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

engine = create_engine("sqlite:///Resources/Hawaii.sqlite")

# reflect the database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)

# Save references to each table

Station = Base.classes.station
Measurements = Base.classes.measurement

# Create our session (link) from Python to the DB

session = Session(engine)

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
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start  date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>")


@app.route("/api/v1.0/precipitation")

#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.

def precipitation():
    
#    
    last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date > last_year).\
        order_by(Measurements.date).all()

# Create a list of dicts with `date` and `prcp` as the keys and values
    precip_list = []
    for date, prcp in precip:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_list.append(precip_dict)

    # Return a list of jsonified precipitation data for the previous 12 months 
    return jsonify(precip_list)


@app.route("/api/v1.0/stations")
#Return a JSON list of stations from the dataset.

def station():
    
    session = Session(engine)
   
    station_data = session.query(Station.station).all()

    session.close()

    
    station_list = list(np.ravel(station_data))

    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
#Query the dates and temperature observations of the most-active station for the previous year of data.

def tobs():
    
    session = Session(engine)

    last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp_obs = session.query(Measurements.date, Measurements.tobs).\
        filter(Measurements.date > last_year).\
        order_by(Measurements.date).all()
    
    session.close()
    
     # Create a dictionary from the row data and append to a list of tobs_list
    tempobs_list = []
    for date, tobs in temp_obs:
        tempobs_dict = {}
        tempobs_dict["date"] = date
        tempobs_dict["tobs"] = tobs
        tempobs_list.append(tempobs_dict)

    # Return a list of jsonified tobs data for the previous 12 months
    return jsonify(tempobs_list)

# /api/v1.0/<start>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start=None, end=None):
    try:
        start = '2010-01-01'
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        #start_date = dt.datetime.strptime(start,'2010-01-01')
        #end_date = dt.datetime.strptime(end,'2010-01-20') if end else None
        end = '2010-01-20'
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    session = Session(engine)
    sel = [func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)]
    if not end:
        results = session.query(*sel).filter(Measurements.date >= start_date).all()
    else:
        results = session.query(*sel).filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).all()
    session.close()
    return jsonify(list(np.ravel(results)))
 

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
if __name__ == "__main__":

    app.run(debug = True)           

