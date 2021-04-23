package com.company;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

//reader associated with the actions table csv file. Makes it easier to read from the csv file with function calls rather
//than using a bunch of try - catch blocks.
//contains a bunch of functions which retrieve specific types of information from the csv file, usually based on the action ID
public class ActionsTableReader {
    String csvFile = "actions_table.csv";
    BufferedReader br;

    int indexID = 0;
    int indexActionName = 1;
    int indexType = 2;
    int indexNumberOfGraphs = 3;
    //these below are used for graph3
    int indexGraphSensorID1 = 4;
    int indexGraphSensorID2 = 5;
    int indexGraphSensorID3 = 6;

    //constructor
    public ActionsTableReader(){
        try{
            br = new BufferedReader(new FileReader(csvFile));
        }catch (IOException ioe){
            ioe.printStackTrace();
        }

    }

    //gets the action identifier e.g max, min, etc. based on the action id
    public String getActionNameFromID(int id){
        String output = "";
        String line = "";
        try{
            br = new BufferedReader(new FileReader(csvFile));
            while((line = br.readLine()) !=null){
                String[] row = line.split(",");
                if(Integer.parseInt(row[indexID]) == id){
                    output = row[indexActionName];
                    br.close();
                    break;
                }
            }
        }catch (IOException ioe){
            ioe.printStackTrace();
        }
        return output;
    }

    //gets the action type e.g scalar, graph based on the action id
    public String getActionTypeFromID(int id){
        String output = "";
        String line = "";
        try{
            br = new BufferedReader(new FileReader(csvFile));
            while((line = br.readLine()) !=null){
                String[] row = line.split(",");
                if(Integer.parseInt(row[indexID]) == id){
                    output = row[indexType];
                    br.close();
                    break;
                }
            }
        }catch (IOException ioe){
            ioe.printStackTrace();
        }
        return output;
    }

    //gets all the action ids whose action type is scalar
    public ArrayList<Integer> getScalarActionIDS(){
        ArrayList<Integer> output = new ArrayList<Integer>();
        String line = "";
        try{
            br = new BufferedReader(new FileReader(csvFile));
            while((line = br.readLine()) !=null){
                String[] row = line.split(",");
                if(row[indexType].compareTo("scalar") == 0){
                    output.add(Integer.parseInt(row[indexID]));

                }
            }
            br.close();
        }catch (IOException ioe){
            ioe.printStackTrace();
        }
        return output;
    }

    //gets all the action ids whose action type is graph
    public ArrayList<Integer> getGraphActionIDS(){
        ArrayList<Integer> output = new ArrayList<Integer>();
        String line = "";
        try{
            br = new BufferedReader(new FileReader(csvFile));
            while((line = br.readLine()) !=null){
                String[] row = line.split(",");
                if(row[indexType].compareTo("graph") == 0){
                    output.add(Integer.parseInt(row[indexID]));

                }
            }
            br.close();
        }catch (IOException ioe){
            ioe.printStackTrace();
        }
        return output;
    }

    //gets the number of graph associated with an action id. This is the 4th column - notice scalars are 0 and regular graphs are 1
    public int getNumberOfGraphs(int actionID){
        int output = 1;
        String line = "";
        try{
            br = new BufferedReader(new FileReader(csvFile));
            while((line = br.readLine()) !=null){
                String[] row = line.split(",");
                if(row[indexID].compareTo(Integer.toString(actionID)) == 0){
                    output = (Integer.parseInt(row[indexNumberOfGraphs]));

                }
            }
            br.close();
        }catch (IOException ioe){
            ioe.printStackTrace();
        }
        return output;
    }

    //gets the first graph sensor ID - this is the 5th column and the number in the column is the sensor id for data to be collected
    //this is only used for graph3, every other case the 5th column is set to 0
    public int getGraphSensorID1(int actionID){
        int output = 0;
        String line = "";
        try{
            br = new BufferedReader(new FileReader(csvFile));
            while((line = br.readLine()) !=null){
                String[] row = line.split(",");
                if(row[indexID].compareTo(Integer.toString(actionID)) == 0){
                    output = (Integer.parseInt(row[indexGraphSensorID1]));

                }
            }
            br.close();
        }catch (IOException ioe){
            ioe.printStackTrace();
        }
        return output;
    }

    //gets the second graph sensor ID - this is the 6th column and the number in the column is the sensor id for data to be collected
    //this is only used for graph3, every other case the 6th column is set to 0
    public int getGraphSensorID2(int actionID){
        int output = 0;
        String line = "";
        try{
            br = new BufferedReader(new FileReader(csvFile));
            while((line = br.readLine()) !=null){
                String[] row = line.split(",");
                if(row[indexID].compareTo(Integer.toString(actionID)) == 0){
                    output = (Integer.parseInt(row[indexGraphSensorID2]));

                }
            }
            br.close();
        }catch (IOException ioe){
            ioe.printStackTrace();
        }
        return output;
    }

    //gets the third graph sensor ID - this is the 7th column and the number in the column is the sensor id for data to be collected
    //this is only used for graph3, every other case the 7th column is set to 0
    public int getGraphSensorID3(int actionID){
        int output = 0;
        String line = "";
        try{
            br = new BufferedReader(new FileReader(csvFile));
            while((line = br.readLine()) !=null){
                String[] row = line.split(",");
                if(row[indexID].compareTo(Integer.toString(actionID)) == 0){
                    output = (Integer.parseInt(row[indexGraphSensorID3]));

                }
            }
            br.close();
        }catch (IOException ioe){
            ioe.printStackTrace();
        }
        return output;
    }

}
