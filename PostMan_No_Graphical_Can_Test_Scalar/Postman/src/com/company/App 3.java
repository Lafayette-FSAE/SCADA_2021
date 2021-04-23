package com.company;

import java.sql.*;
import java.util.ArrayList;
import java.util.Date;

//used to hold the connection and information to the SQL database - so you don't have to keep reconnecting to the database
//every time you want to query data. Holds methods for querying data of interst, usually based on the given keyname
//NOTE: actionkey and keyname refer to the same thing, I just changed it arbitrarily
public class App {

    //address
    private final String url = "jdbc:postgresql://localhost/postgres";
    private final String user = "postgres";
    private final String password = "";
    //some methods are just calls to tableReader, this is because the app methods were initially all written to get data from
    //the SQL database, as all the tables were in the database. Then most of the tables, except data and sensors, were moved
    //to csv files, and to keep from rewriting a bunch of calls, I just made the app calls reference the tableReader calls
    private TableReader tableReader;

    /**
     * Connect to the PostgreSQL database
     *
     */

    //connect to the postgres database, only need to connect once and then can query.
    public Connection connect() {
        Connection conn = null;
        try {
            conn = DriverManager.getConnection(url, user, password);
        } catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        tableReader = new TableReader();
        return conn;
    }

    //gets the name from key_names table associated with the actionkey: input rpm_max, output Max RPM (rev/min)
    public String getActionName(String actionKey) {
        return tableReader.getActionName(actionKey);
    }

    //returns elapsed time since beginning of session in seconds, used for graph of that sensor vs time
    //used for scalar action and graph action to get the timestamps in terms of seconds since the session started
    //thats mostly used for graph action, for the x axis timestamps
    public ArrayList<String> getTimestampsForAction(String sensorAction, int sessionStartID, int sessionEndID) {
        String SQL = "SELECT * FROM data WHERE sensor_id = (SELECT redis_key FROM sensors WHERE id = " + tableReader.sensorActionsReader.getSensorIDFromKey(sensorAction) +
                ") AND id BETWEEN " + (sessionStartID ) + " AND " + (sessionEndID);

        ArrayList<Date> timestamps = new ArrayList<Date>();
        ArrayList<String> output = new ArrayList<String>();

        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            while (rs.next()) {
                timestamps.add(rs.getTimestamp(1));
            }

            long reference = timestamps.get(0).getTime();
            //("did i get his far?");
            for(int i =0;i<timestamps.size();i++){
                // /1000 used to change from ms to s
                output.add(Long.toString((timestamps.get(i).getTime() - reference)/1000) );
            }

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return output;
    }
    //returns the title for the sensor when used in a graph. Column in sensors table
    //which holds this name for display on the graph
    public String getSensorTitle(String sensorAction) {
        String SQL = "SELECT display_name FROM sensors WHERE id = " + tableReader.sensorActionsReader.getSensorIDFromKey(sensorAction);
        String sensorTitle = "";
        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            rs.next();
            sensorTitle = rs.getString(1);

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return sensorTitle;
    }
    //returns all the data in data table for given sensor for given session
    public ArrayList<String> getDataForSensor(String SQL){

        String output = "";
        ArrayList<String> data = new ArrayList<String>();

        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            while (rs.next()) {
                output = rs.getString(3);
                data.add(output);
            }

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return data;
    }
    //get action_id from actions table based on key
    public int getActionID(String keyname){
        return tableReader.getActionID(keyname);
    }
    //gets the action IDS for all scalar actions
    public ArrayList<Integer> getScalarActionIDS(){
        return tableReader.getScalarActionIDS();
    }
    //gets action_name from actions table - max, min, etc.
    public String getActionIdentifier(String keyname){
        return tableReader.getActionIdentifier(keyname);
    }
    //gets the action IDS for all graph actions
    public ArrayList<Integer> getGraphActionIDS(){
        return tableReader.getGraphActionIDS();
    }
    //get sensor_name from sensors table corresponding to key
    public String getSensorNameForAction(String keyname){
        String output = "";
        String SQL = "SELECT redis_key FROM sensors WHERE id = "+ tableReader.sensorActionsReader.getSensorIDFromKey(keyname);

        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            while (rs.next()) {
                output= rs.getString(1);
            }

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return output;
    }
    //gets the timestamps of every session
    public ArrayList<Date> getSessionTimestamps(){
        ArrayList<Date> output = new ArrayList<Date>();
        String SQL = "SELECT timestamp FROM data WHERE sensor_id = 'scada:session' ORDER BY timestamp";
        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            while (rs.next()) {
                output.add(rs.getTimestamp(1));
            }

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return output;
    }
    //get all data IDs for scada:session in the data table - the session starts
    public ArrayList<Integer> getDataIDForTimestamps(){
        ArrayList<Integer> output = new ArrayList<Integer>();
        String SQL = "SELECT id FROM data WHERE sensor_id = 'scada:session' ORDER BY timestamp";
        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            while (rs.next()) {
                output.add(rs.getInt(1));
            }

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return output;
    }
    //return the id of the last data entry in the data log
    public int getFinalDataID(){
        int output = 0;
        String SQL = "SELECT id FROM data ORDER BY id DESC";
        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            rs.next();
                output = rs.getInt(1);


        } catch (SQLException ex) {
            System.out.println("sss");
            System.out.println(ex.getMessage());
        }
        return output;
    }
    //return the data type for the sensor corresponding to the action keyname - double, string
    public String getSensorDataType(String keyname){
        String output = "";
        String SQL = "SELECT datatype FROM sensors WHERE id = "+ tableReader.sensorActionsReader.getSensorIDFromKey(keyname);
        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            rs.next();
            output = rs.getString(1);


        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return output;

    }
    //gets all the sensor data from the data table corresponding to the sensorID given between the session ids
    public ArrayList<String> getSensorDataForSensorID(int sensorID,int sessionStart,int sessionEnd){
        ArrayList<String> output = new ArrayList<String>();
        String SQL = "SELECT value FROM data WHERE sensor_id = (SELECT redis_key FROM sensors WHERE id = " + sensorID + ") AND id BETWEEN " + sessionStart + " AND " + sessionEnd;
        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            while(rs.next()) {
                output.add(rs.getString(1));
            }

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return output;
    }
    //test method
    public ArrayList<Date> getTimestampsForGLVV(){
        ArrayList<Date> output = new ArrayList<Date>();
        String SQL = "SELECT timestamp FROM data WHERE sensor = (SELECT sensor_name FROM sensors WHERE id = "+tableReader.sensorActionsReader.getSensorIDFromKey("glvv_max");
        int i =0;
        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            while(rs.next()){
            output.add(rs.getTimestamp(1));
            System.out.println(output.get(i).getTime());
            i++;
            }

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return output;

    }
    //gets the final timestamp in the data table, in Date
    public Date getFinalDataTimestamp(){
       Date output = new Date();
        String SQL = "SELECT timestamp FROM data ORDER BY timestamp DESC";
        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

                rs.next();
                output = rs.getTimestamp(1);


        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return output;

    }
    //gets all the timestamps in seconds since the start of the session that correspond to the sensorID provided
    //in this case sensor_id is the name of the sensor and sensorID is the id of the sensors table
    public ArrayList<String> getTimestampsForSensorID(int sensorID,int sessionStart,int sessionEnd){
        String SQL = "SELECT timestamp FROM data WHERE sensor_id = (SELECT redis_key FROM sensors WHERE id = " + sensorID + ") AND id BETWEEN " + (sessionStart ) + " AND " + (sessionEnd);

        ArrayList<Date> timestamps = new ArrayList<Date>();
        ArrayList<String> output = new ArrayList<String>();

        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            while (rs.next()) {
                timestamps.add(rs.getTimestamp(1));
            }
            long reference = timestamps.get(0).getTime();
           // System.out.println(reference);
            for(int i =0;i<timestamps.size();i++){
                output.add(Long.toString((timestamps.get(i).getTime() - reference)/1000) );
            }

        } catch (SQLException ex) {

            System.out.println(ex.getMessage());
        }
        return output;
    }
    //gets the more legible/display name from the sensors table that correspond to the given sensorID
    public String getSensorTitleForSensorID(int sensorID) {
        String SQL = "SELECT display_name FROM sensors WHERE id = " + sensorID;
        String sensorTitle = "";
        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            rs.next();
            sensorTitle = rs.getString(1);

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return sensorTitle;
    }
    //test method
    public int getNumberOfDataPointsInSession(int sessionStart, int sessionEnd){
        String SQL = "SELECT id FROM data WHERE id BETWEEN " + sessionStart + " AND " + sessionEnd;

        int counter = 0;

        try (Connection conn = connect();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(SQL)) {

            while (rs.next()) {
                counter++;
            }


        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return counter;

    }


}
