"""
The template of the script for the machine learning process in game pingpong
"""
# Import the necessary modules and classes
import pickle
from os import path
import numpy as np
from mlgame.communication import ml as comm
filename = path.join(path.dirname(__file__), 'save', 'forest_reg.pickle')
with open(filename, 'rb') as file: # read binary
    clf = pickle.load(file)
def ml_loop(side: str):
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".
    """
    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    
    ball_prev = [93, 395] # ball's initial point 
    def get_dir(vector_x, vector_y):
        if(vector_x >= 0 and vector_y >= 0):
            return 0
        elif(vector_x > 0 and vector_y < 0):
            return 1
        elif(vector_x < 0 and vector_y > 0):
            return 2
        elif(vector_x < 0 and vector_y < 0):
            return 3 
    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':
            if scene_info["platform_1P"][0]+20  > (pred-1) and scene_info["platform_1P"][0]+20 < (pred+1): return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-1) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-1) and scene_info["platform_2P"][0]+20 < (pred+1): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-1) : return 1 # goes right
            else : return 2 # goes left
    # 2. Inform the game process that ml process is ready
    comm.ml_ready()
    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()
        if side == "1P":
            feature = []
            # feature.append(scene_info["platform_1P"][0])
            feature.append(scene_info["ball"][0])
            feature.append(scene_info["ball"][1])
            x =  get_dir(scene_info['ball_speed'][0], scene_info['ball_speed'][1])
            feature.append(1)
            for i in range(4):
                if i == x:
                    feature.append(1)
                else:
                    feature.append(0)
            feature = np.array(feature)
            feature = feature.reshape((-1,7)) # reshape array into 4 column
        else:
            feature = []
            # feature.append(scene_info["platform_1P"][0])
            feature.append(scene_info["ball"][0])
            feature.append(scene_info["ball"][1])
            x = get_dir(scene_info['ball_speed'][0], scene_info['ball_speed'][1])
            feature.append(2)
            for i in range(4):
                if i == x:
                    feature.append(1)
                else:
                    feature.append(0)
            # print(feature)
            feature = np.array(feature)
            feature = feature.reshape((-1,7)) # reshape array into 4 column
        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False
            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue
        # 3.3 Put the code here to handle the scene information
        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
#             comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
#             ball_served = True
        else:
            
            if side == "1P":
                command = move_to(player = "1P", pred = clf.predict(feature))
            else:
                command = move_to(player = "2P", pred = clf.predict(feature))

            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
