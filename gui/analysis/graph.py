import datetime
import math
import pandas as pd
import matplotlib.pyplot as plt

def get_dynamic(emote, messages, graph_type=True):
    sorted_messages = sorted(messages, key=lambda message: message.time)
    emote_sum = 0
    x = []
    y = []
    start_time = messages[0].time
    prev_count = 0
    i = 0
    print(start_time)
    interval = math.floor(len(messages)/300)
    for msg in sorted_messages:
        if emote == "viewers":
            if msg.nickname != "Viewer_counter":
                continue
            
            if len(x) == 0:
                time = 0
            else:
                print(msg.time)
                time = (msg.time - start_time)/datetime.timedelta(minutes=1)

            
            x.append(time)
            msg_num = int(msg.message.strip())
            if graph_type:
                delta = msg_num - prev_count
                prev_count = msg_num
                y.append(delta)   
            else:
                y.append(msg_num)

            
        else:
            emote_sum += msg.count_emote(emote)
            i += 1
            if i >= interval:
                if len(x) == 0:
                    time = 0
                else:
                    time = (msg.time - start_time)/datetime.timedelta(minutes=1)

                ###TEMPORARY###
                if len(x) > 1 and msg.time == x[-1]:
                    continue
                ###############
                
                else:
                    if graph_type:
                        delta = emote_sum - prev_count
                        prev_count = emote_sum
                        y.append(delta)   
                    else:
                        y.append(emote_sum)
                
                x.append(time)
                i = 0
    print(x)
    print(y)
    # data
    df=pd.DataFrame({'x': x, 'y': y})
    plt.title(emote)
    # plot
    plt.plot( 'x', 'y', data=df, linestyle='-')
    plt.show()