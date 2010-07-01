// Copyright 2010 owners of the AI Challenge project
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may not
// use this file except in compliance with the License. You may obtain a copy
// of the License at http://www.apache.org/licenses/LICENSE-2.0 . Unless
// required by applicable law or agreed to in writing, software distributed
// under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.
//
// Author: Patrick Paskaris
//
// This class is for the viewer JFrame.

import javax.swing.*;

public class CLViewer extends JFrame {
	private ViewerPanel vp;
	
  // There are two ways of launching this viewer.
  //   1. Send command line arguments, sending a playback string over stdin.
  //   3. Just call the constructor with the stuff.
  //   Arguments are:
  //		player1name
  //		player2name
  //		[more_players]
  //   Separated by spaces.
  public static void main(String args[]) {
    if (args.length < 2) {
      System.err.println("ERROR: you must give at least 2 command line " +
        "arguments.");
      System.err.println("USAGE: player1name player2name [moreplayers]");
      System.exit(1);
    }
    String players[] = new String[args.length];
    for (int i = 0; i < args.length; i++) {
      players[i] = args[i];
    }
    String playbackString = "";
    int ch;
    try {
      while ((ch = System.in.read()) >= 0) {
        playbackString += (char)ch;
      }
    } catch (Exception e) {
      System.err.println("ERROR: game player failed while reading game " +
        "playback string.");
      System.exit(1);
    }
    CLViewer c = new CLViewer(players, playbackString.trim());
    c.show();
  }

	public CLViewer (String players[], String gameData) {
		try {
			// house keeping
			setTitle("Planet Wars Visualizer");
			setSize(640, 480);
			setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
			
			vp = new ViewerPanel(players, gameData);
			
			add(vp);
		} catch (Exception err) {
			// Add a text handler for VizPanel to display errors or something
			JLabel error = new JLabel("<HTML><STRONG>Error:  Visualizer was unable to correctly parse the game data!</STRONG><BR><BR>"
									  + err.getMessage());
			add(error);
		}
	}
}