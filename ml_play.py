"""
The template of the script for the machine learning process in game pingpong
"""
import pickle
from os import path
import numpy as np
from mlgame.communication import ml as comm

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
    ball_served = False
    
    filename = path.join(path.dirname(__file__), 'ranf_mid.pickle')
    with open(filename, 'rb') as file: # read binary
        clf = pickle.load(file)
    
    ball_prev = [80, 415] # ball's initial point 
    
    def get_dir(vector_x, vector_y):
        if(vector_x >= 0 and vector_y >= 0):
            return [0, 0, 0, 1]
        elif(vector_x > 0 and vector_y < 0):
            return [0, 0, 1, 0]
        elif(vector_x < 0 and vector_y > 0):
            return [0, 1, 0, 0]
        else :
            return [1, 0, 0, 0]
        # elif(vector_x < 0 and vector_y < 0):
        #     return [1, 0, 0, 0]

    def move_to(player, pred) : # move platform to predicted position to catch ball 
        if player == '1P':
            if scene_info["platform_1P"][0]+20 > (pred-1) and scene_info["platform_1P"][0]+20 < (pred+1): return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-1) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20 > (pred-2) and scene_info["platform_2P"][0]+20 < (pred+2): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-2) : return 1 # goes right
            else : return 2 # goes left

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        scene_info = comm.recv_from_game()
        
        feature = []
        feature.append(scene_info["ball"][0])
        feature.append(scene_info["ball"][1])
        # feature.append(scene_info["blocker"][0])
        
        arr = get_dir(scene_info["ball"][0] - ball_prev[0], scene_info["ball"][1] - ball_prev[1])
        feature.append(arr[0])
        feature.append(arr[1])
        feature.append(arr[2])
        feature.append(arr[3])
        if side == "1P":
            feature.append(1)
        else: 
            feature.append(2)    

        ball_prev = [scene_info["ball"][0], scene_info["ball"][1]]
        feature = np.array(feature)
        feature = feature.reshape((-1, 7)) # reshape array into 7 column
        # print(feature)
            
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            comm.ml_ready()
            continue

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
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