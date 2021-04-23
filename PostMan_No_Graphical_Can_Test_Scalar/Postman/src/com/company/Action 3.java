package com.company;

import java.util.ArrayList;

//the structure for holding all the information pertinent to an action: namely its ID, the keyname associated with it,
// the identifier (action name in the actions table), the value associated with executing the action (either scalar or image filename),
// the app (connection to SQL database), and the selected sessions start and end IDs
public abstract class Action {
    int actionID;
    String keyname;
    String actionIdentifier;
    String actionName;
    String value;
    App app;
    int sessionStartID;
    int sessionEndID;

    public Action(String keyname, int sessionStartID,int sessionEndID, App app){
        this.app = app;
        this.keyname = keyname;
        this.actionID = this.app.getActionID(this.keyname);
        this.actionIdentifier = this.app.getActionIdentifier(this.keyname);
        this.actionName = getName();
        this.sessionEndID = sessionEndID;
        this.sessionStartID = sessionStartID;

    }

    //fill a key's value - be that scalar or chart filename
    public abstract void execute(ArrayList<String> data, String dataType);

    //get key's name - the name to be displayed in report headers/titles - the more legible action name
    public String getName(){
        return this.app.getActionName(this.keyname);
    }

    public String getActionIdentifier() {
        return actionIdentifier;
    }
}
