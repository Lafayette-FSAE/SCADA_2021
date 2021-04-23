package com.company;

import java.util.ArrayList;

//object used to collect data for a sensor for the given session. Many actions can act on one sensor's data, that's why this object exists, to
//reduce the number of queries to 1.
//The keyname is just the keyname that was used to instantiate the collector, again sensor data isn't necessarily unique
//to a keyname, so many keynames could reference the same sensor data, this stored keyname is just the one that created
//the collector.
public class Collector {

    String keyname;
    ArrayList<String> data;
    String SQL;
    //query data from the SQL database
    App app;
    String sensorName;
    String dataType;
    int sessionStartID;
    int sessionEndID;
    //read from the csv files
    TableReader tableReader;

    //Constructor. Creates SQL to get the data for the correct sensor corresponding to the keyname based on the selected session
    public Collector(String keyname, int sessionStartID, int sessionEndID, App app){
        this.keyname = keyname;
        this.tableReader = new TableReader();
        this.SQL = "SELECT * FROM data WHERE sensor_id = (SELECT redis_key FROM sensors WHERE id = " + tableReader.sensorActionsReader.getSensorIDFromKey(keyname) + ") AND id BETWEEN " + (sessionStartID) +
                   " AND " + (sessionEndID);
        this.app = app;
        this.sensorName = getSensorName();
        getAvailableData();
        this.sessionStartID = this.sessionStartID;
        this.sessionEndID = this.sessionEndID;
        this.dataType = app.getSensorDataType(keyname);
    }
    //gets the data for the sensor in the given sensor
    public ArrayList<String> getAvailableData(){
        this.data = app.getDataForSensor(SQL);
        return getData();
    }

    public ArrayList<String> getData(){
        return data;
    }
    //returns the sensor name - glvv, rpm, etc.
    public String getSensorName() {
        return this.app.getSensorNameForAction(this.keyname);
    }

}
