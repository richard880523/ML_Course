"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True

            x_prev = scene_info.ball[0]
            y_prev = scene_info.ball[1]
            
            x_update = 80

        else:
            x_curr = scene_info.ball[0]
            y_curr = scene_info.ball[1]

            if(y_curr < 120 or y_curr - y_prev < 0): # do not move when ball is up there breaking bricks.
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            else:
                if(x_curr == 0):
                    y_hit_point = y_curr
                    if(y_hit_point < 200): # will hit again on the other side
                        y_hit_point += 200
                        x_update = 200 - (400 - y_hit_point) - (40 / 2)
                    else:    
                        x_update = (400 - y_hit_point) - (40 / 2)
                    # print(x_update)

                elif(x_curr >= 195 and x_curr < 200):
                    y_hit_point = y_curr
                    if(y_hit_point < 200):
                        y_hit_point += 200
                        x_update = (400 - y_hit_point) - (40 / 2)
                    else:    
                        x_update = 200 - (400 - y_hit_point) - (40 / 2) # bias
                    # print(x_update)

                if(x_update < 0):
                    x_update = abs(x_update)
                elif(x_update > 195):
                    x_update -= 195

                while(x_update % 5 != 0):
                    x_update += 1 # for movimg plateform smoothly 

                if(scene_info.platform[0] > x_update):
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                elif(scene_info.platform[0] < x_update):
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)  
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)

            x_prev = x_curr
            y_prev = y_curr        