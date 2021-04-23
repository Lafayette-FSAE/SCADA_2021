package com.company;

import java.util.ArrayList;
import java.util.List;

//structure that holds a collector for a sensor and the list of actions associated with the sensor data and a graph3
//the scalar actions and graph actions go to the actions list, graph 3 goes separate
public class CollectionList {

    private Collector parent;
    private List<Action> children;

    private String sensorName;
    //Graph3 graph3;
    boolean containsGraph3;

    public CollectionList(Collector parent){
        this.parent = parent;
        this.children = new ArrayList<Action>();
        this.sensorName = this.parent.getSensorName();
        this.containsGraph3 = false;
    }

    public CollectionList(){
        this.parent = null;
        this.children = null;
        this.sensorName = "";
        this.containsGraph3 = false;
    }

    //add an Action to the list of actions
    public void addChild(Action child){
        children.add(child);
    }
    //returns the list of actions
    public List<Action> getChildren(){
        return this.children;
    }
    //returns the parent
    public Collector getParent() {
        return parent;
    }
    //sets the parent to the specified
    public void setParent(Collector parent){
        this.parent = parent;
    }

    public void setTreeData(Collector parent){
        this.parent = parent;
        this.children = new ArrayList<Action>();
        this.sensorName = this.parent.getSensorName();
    }

    //returns sensorName - glvv, rpm, etc.
    public String getSensorName() {
        return sensorName;
    }

    //returns the data held by the collector for a given sensor
    public ArrayList<String> getCollectionListData(){
        return parent.getData();
    }

    //debugging
    public void print(){
        System.out.println("Parent Sensor: " + this.sensorName);
        for(int i = 0; i< children.size(); i++){
            System.out.println("Child:" + children.get(i).getActionIdentifier());
        }
    }

//    //sets the values of the graph3 so that it actually has sensor data to reference, doesn't reference the parent data directly
//    public void setGraph3(int sensorID1, int sensorID2, int sensorID3, int sessionStart, int sessionEnd,String imageName, String keyname,App app){
//        this.graph3 = new Graph3( sensorID1,  sensorID2,  sensorID3,  sessionStart,  sessionEnd, imageName,  keyname, app);
//        this.containsGraph3 = true;
//    }
}
