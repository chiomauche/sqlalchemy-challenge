# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

import numpy as np
import pandas as pd
import datetime as dt


#################################################
# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#################################################


# reflect an existing database into a new model

Base = automap_base()


# reflect the tables
#Base.prepare(autoload_with=engine)
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup

app = Flask(__name__)
#################################################




#################################################
# Flask Routes

# 1. Start at the homepage and List all the available routes.

@app.route("/")
def welcome():

    return(
     
     f"Climate App Home Page<br/>"  
        
     f"<br/>Welcome To Honolulu, Hawaii Climate API!<br/><br/><br/>"
        
     f"The following routes are available:<br/>"
        
     f"/api/v1.0/precipitation - "
        
     f"One year of precipitation data<br/>"
        
     f"/api/v1.0/stations - "
        
     f"weather stations, ID and station<br/>"
        
     f"/api/v1.0/tobs - "
        
     f"temperature observations for most active station, USC00519281, for 12 months<br/>"
        
     f"/api/v1.0/start_date - "

     f"find minimum, average, and maximum temperatures for a specified start range(Date format:yyyy-mm-dd) <br/><br/>"
        
     f"/api/v1.0/start_date/end_date - "
        
     f"find minimum, average, and maximum temperatures for a specified start and end range(Date format:yyyy-mm-dd) <br/><br/>"
   )




# 2. Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date   as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation(): 

    # Assign the measurement class to a variable called `Measurement`
    Measurement= Base.classes.measurement
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Perform a query to retrieve the data and precipitation scores
    last_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    one_year_previous = dt.date(last_date.year -1, last_date.month, last_date.day)
    select = [Measurement.date, Measurement.prcp]
    date_prcp_scores= session.query(*select).filter(Measurement.date >= one_year_previous).all()
    
    # Create a dictionary and return JSON of dictionary
    prcp_data = []
    for date, prcp_scores in date_prcp_scores:
           prcp_dict = {}
           prcp_dict['date'] = date
           prcp_dict['prcp_scores'] = prcp_scores
           prcp_data.append(prcp_dict)
        
   # Close session    
    session.close()
    
    return jsonify(prcp_data)




# 3. Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def all_stations():

    # Design a query to retrieve the list of stations in dataset
    stations_list = session.query(stations_list.name , stations_list.station).all()

    # Create a dictionary
    dict_stations_list = dict(stations_list)
    
     # Close session    
    session.close() 

    return jsonify(dict_stations_list)



# 4.Query the dates and temperature observations of the most-active station for the previous year of data.
#   Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")

def tobs():

    
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Perform a query to retrieve the data and precipitation scores
    last_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d')
    one_year_previous = dt.date(last_date.year -1, last_date.month, last_date.day)
    select = [Measurement.date, Measurement.tobs]
    temperatures = session.query(*select).filter(func.strftime(Measurement.date) >= one_year_previous, Measurement.station == 'USC00519281').\
    group_by(Measurement.date).order_by(Measurement.date).all()
    
    
    # Create tobs dictionary
    tobs_data = []
    for date, temperature in temperatures:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['temperature'] = temperature
        tobs_data.append(tobs_dict)
        
    # Close session 
    session.close()

    return jsonify(tobs_data)



#5a. Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start range.
#   For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/<start>") 

def start(start):
    select = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    results = session.query(*select).\
            filter(Measurement.date >= start).all()
   
    # Close session
    session.close()

    temperatures = list(np.ravel(results))
    return jsonify(temperatures)



#5b. Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range.
#    For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>/<end>")

def start_end(start,end):
    select = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    start= dt.datetime.strptime(start, "%Y-%m-%d")
    results = session.query(*select).\
            filter(Measurement.date <= end).all()
   
    # Close session
    session.close()

    temperatures = list(np.ravel(results))
    return jsonify(temperatures)
    
    

 

if __name__ == "__main__":
    app.run(debug=True)
    
