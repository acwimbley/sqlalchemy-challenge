# Import the dependencies.
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#from flask import Flask, jsonify
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
#engine = create_engine("sqlite:////Resources/hawaii.sqlite")
engine = create_engine('sqlite:///' + r'C:\Users\acwim\Desktop\DS-VIRT-DATA-PT-11-2023-U-LOLC\sqlalchemy-challenge\Resources\hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
#Base.prepare(autoload_with=engine)
Base.prepare(engine, reflect=True)

# Save references to each tables
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"api/v1.0/precipitation<br/>"
        f"api/v1.0/stations<br/>"
        f"api/v1.0/tobs"
        #f"api/v1.0/tobs/<start_date>"
    )

#PRECIPITATION ROUTE

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON representation of precipitation data for the past 12 months"""

    #Create a session - this is necessary because of a programming error encountering
    session = Session(engine)    
 
    try:
         # Starting from the most recent data point in the database.
         most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

         # Calculate the date one year from the last date in the data set.
         one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

         # Perform a query to retrieve the data and precipitation scores
         results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago, Measurement.date <= most_recent_date).all()


        # Create a dictionary from the row data and append to a list
         all_precipitation = []
         for date, prcp in results:
            precipitation_dict = {}
            precipitation_dict["date"] = date
            precipitation_dict["prcp"] = prcp
            all_precipitation.append(precipitation_dict)

         return jsonify(all_precipitation)

    finally:
        #Closing the session
        session.close()

if __name__ == "__main__":
    app.run(debug=True)

##STATIONS ROUTE

@app.route("/api/v1.0/stations")
def station():
    """Return a JSON list of stations from the data set."""

    #Create a session - this is necessary because of a programming error encountering
    session = Session(engine) 

    try:    
        # Perform the query to retrieve station data
        stations_data = session.query(Station.station, Station.name).all()

        # Create a list of dictionaries with station information
        all_stations = [{"station": station, "name": name} for station, name in stations_data]

        return jsonify(all_stations)

    finally:
        #Closing the session
        session.close()

if __name__ == "__main__":
    app.run(debug=True)



#TOBS ROUTE
 

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON representation of temperature observations for the last year."""

    #Creating a session
    session = Session(engine)    

    try:
        # Find the most active station
        most_active_station = (
            session.query(Measurement.station, func.count(Measurement.station))
            .group_by(Measurement.station)
            .order_by(func.count(Measurement.station).desc())
            .first()
    )

        if most_active_station:
            most_active_station_id = most_active_station[0]

            # Find the latest date in the dataset
            latest_date = session.query(func.max(Measurement.date)).scalar()

            # Calculate the date one year ago from the latest date
            one_year_ago = dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)

            # Perform the query to retrieve temperature observations for the most active station and the last year
            results = (
                session.query(Measurement.date, Measurement.tobs)
                .filter(Measurement.station == most_active_station_id)
                .filter(Measurement.date >= one_year_ago)
                .all()
            )

            # Create a list of dictionaries with temperature observations
            all_tobs = [{"date": date, "tobs": tobs} for date, tobs in results]

            return jsonify(all_tobs)
        else:
         return jsonify({"error": "No data available for temperature observations"}), 404

    finally:
        #Closing the session
        session.close() 
    
if __name__ == "__main__":
    app.run(debug=True)     
    
# #START DATE ROUTE

# @app.route("/api/v1.0/tobs/<start_date>")
# def tobs_start_date(start_date):
#     """Return a JSON representation of temperature observations from the specified start date."""
    
#     # Perform the query to retrieve temperature observations from the start date
#     results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start_date).all()

#     # Create a list of dictionaries with temperature observations
#     all_tobs = [{"date": date, "tobs": tobs} for date, tobs in results]

#     return jsonify(all_tobs)

# if __name__ == "__main__":
#     app.run(debug=True)    




# @app.route("/api/v1.0/tobs")
# def tobs():
#     """Return a JSON representation of temperature observations for the last year."""
    
#     # Perform the query to retrieve temperature observations
#     # Replace 'your_start_date' and 'your_end_date' with the appropriate date range
#     results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= 'your_start_date', Measurement.date <= 'your_end_date').all()

#     # Create a dictionary from the row data and append to a list
#     all_tobs = []
#     for date, tobs in results:
#         tobs_dict = {}
#         tobs_dict["date"] = date
#         tobs_dict["tobs"] = tobs
#         all_tobs.append(tobs_dict)

#     return jsonify(all_tobs)

# if __name__ == "__main__":
#     app.run(debug=True)


# @app.route("/api/v1.0/<start>")
# @app.route("/api/v1.0/<start>/<end>")
# def temperature_stats(start, end=None):
#     """Return a JSON list of the minimum, average, and maximum temperature for a specific start or start-end range."""
    
#     # Perform the query to retrieve temperature observations
#     if end:
#         results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
#             filter(Measurement.date >= start, Measurement.date <= end).all()
#     else:
#         results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
#             filter(Measurement.date >= start).all()

#     # Create a dictionary with temperature statistics
#     temperature_stats_dict = {
#         "start_date": start,
#         "end_date": end,
#         "tmin": results[0][0],
#         "tavg": results[0][1],
#         "tmax": results[0][2]
#     }

#     return jsonify(temperature_stats_dict)

#