//package com.company;
//
//import org.knowm.xchart.BitmapEncoder;
//import org.knowm.xchart.CategoryChart;
//import org.knowm.xchart.CategoryChartBuilder;
//import org.knowm.xchart.CategorySeries;
//import org.knowm.xchart.style.Styler;
//import java.io.IOException;
//import java.util.ArrayList;
//import java.util.List;
//
///* IMPORTANT NOTE:
//    THIS OBJECT IS VERY FLAWED. I WOULDN'T REALLY CONSIDER THIS WORKING, ITS MOSTLY JUST HELD TOGETHER AND WAS MEANT MORE
//    AS A PROOF OF CONCEPT FOR THE DEMO. THERE IS A LIST OF FLAWS IN THE INCLUDED DOCUMENTATION, BUT MANY OF THE FLAWS CAN
//    BE SEEN FROM THE OUTPUT GRAPHS
// */
//public class Graph3 {
//    //similar to an action in that there is a value and name which will be overwritten by the png filename and given name
//    ArrayList<Double> data1;
//    ArrayList<Double> data2;
//    ArrayList<Double> data3;
//    ArrayList<String> timestamps1;
//    ArrayList<String> timestamps2;
//    ArrayList<String> timestamps3;
//    App app;
//    String actionName;
//    String value = "";
//    String imageName;
//    String yAxisTitle;
//    String yLabel2;
//    String yLabel3;
//    int actionID;
//    String keyname;
//
//    //allows for the creation of graphs with 3 inputs. Has 3 sensor ids for the 3 inputs to collect data all based on the same session
//    public Graph3(int sensorID1, int sensorID2, int sensorID3, int sessionStart, int sessionEnd,String imageName, String keyname, App app){
//        this.app = app;
//        this.data1 = convertToDouble(app.getSensorDataForSensorID(sensorID1,sessionStart,sessionEnd));
//        this.data2 = convertToDouble(app.getSensorDataForSensorID(sensorID2,sessionStart,sessionEnd));
//        this.data3 = convertToDouble(app.getSensorDataForSensorID(sensorID3,sessionStart,sessionEnd));
//        this.timestamps1 = app.getTimestampsForSensorID(sensorID1,sessionStart,sessionEnd);
//        this.timestamps2 = app.getTimestampsForSensorID(sensorID2,sessionStart,sessionEnd);
//        this.timestamps3 = app.getTimestampsForSensorID(sensorID3,sessionStart,sessionEnd);
//        this.imageName = imageName;
//        this.yAxisTitle = app.getSensorTitleForSensorID(sensorID1);
//        this.yLabel2 = app.getSensorTitleForSensorID(sensorID2);
//        this.yLabel3 = app.getSensorTitleForSensorID(sensorID3);
//        this.keyname = keyname;
//        this.actionID = app.getActionID(keyname);
//        this.actionName = this.app.getActionName(this.keyname);
//    }
//
//
//    //generates the chart, sets the value to the chart filename
//    public void execute(){
//            generateChart(timestamps1,timestamps2,timestamps3,data1,data2,data3,yAxisTitle + "vs Time(s)","Elapsed Time Since Session Start (seconds)",yAxisTitle, yLabel2,yLabel3,
//                    imageName);
//
//            //catches case user puts filename.png or filename
//            //just a catch so output filename is always right
//            if (this.imageName.contains(".png")) {
//                this.value = this.imageName;
//            } else {
//                this.value = this.imageName + ".png";
//            }
//
//    }
//
//    //creates a .png image of the graph given the parameters, so that the filename can be embedded into the report html
//    //to understand how this works better look up examples online/documentation of xchart
//    public void generateChart(ArrayList<String> timestamps1, ArrayList<String> timestamps2,ArrayList<String> timestamps3,
//                              ArrayList<Double> actionData1,ArrayList<Double> actionData2,ArrayList<Double> actionData3,
//                              String chartTitle, String xLabel, String yLabel1,String yLabel2,String yLabel3, String imageFilename){
//
//
//        // Create Chart
//        CategoryChart chart =
//                new CategoryChartBuilder()
//                        .width(1200)
//                        .height(600)
//                        .theme(Styler.ChartTheme.GGPlot2)
//                        .title(chartTitle)
//                        .xAxisTitle(xLabel)
//                        .yAxisTitle(yLabel1)
//                        .build();
//
//        // Customize Chart
//        chart.getStyler().setDefaultSeriesRenderStyle(CategorySeries.CategorySeriesRenderStyle.Line);
//        //chart.getStyler().setXAxisLabelRotation(-75);
//        chart.getStyler().setLegendPosition(Styler.LegendPosition.OutsideE);
//        chart.getStyler().setAvailableSpaceFill(0);
//        chart.getStyler().setOverlapped(true);
//
//
//        // Declare data
//        java.util.List<String> xAxisKeys1 = timestamps1;
//        List<Double> yAxisKeys1 = actionData1;
//
//        CategorySeries series1 =
//                chart.addSeries(yLabel1, xAxisKeys1, yAxisKeys1);
//
//        // Declare data
//        java.util.List<String> xAxisKeys2 = timestamps2;
//        List<Double> yAxisKeys2 = actionData2;
//
//        CategorySeries series2 =
//                chart.addSeries(yLabel2, xAxisKeys2, yAxisKeys2);
//
//        // Declare data
//        java.util.List<String> xAxisKeys3 = timestamps3;
//        List<Double> yAxisKeys3 = actionData3;
//
//        CategorySeries series3 =
//                chart.addSeries(yLabel3, xAxisKeys3, yAxisKeys3);
//
//
//        try {
//            BitmapEncoder.saveBitmap(chart, imageFilename, BitmapEncoder.BitmapFormat.PNG);
//        }catch(IOException ioe){
//            ioe.printStackTrace();
//        }
//    }
//
//    //converts arraylist of strings to arraylist of doubles
//    private ArrayList<Double> convertToDouble(ArrayList<String> strings){
//        ArrayList<Double> doubles = new ArrayList<Double>();
//        for(int i =0;i<strings.size();i++){
//            doubles.add(Double.parseDouble(strings.get(i)));
//        }
//        return doubles;
//    }
//}
