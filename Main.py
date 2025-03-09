import asyncio
import json
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
import cv2
import sys

import traceback


with open("config.json", "r") as file:
    config = json.load(file)

with open("thresholds.json", "r") as file:
    thresholds = json.load(file)
    
HOST = config["host"]
OSC_PORT = config["osc_port"]
FILE = config["video_folder"]
EXT = config["file_ext"]

faceStr = "2100"  # Default face (change dynamically in your OSC server)

### OpenCV ###
cap = None  # Global video capture object

def video_player():
    global faceStr
    path = f'{FILE}/{faceStr}.{EXT}'  # Default video path

    # Open first video
    cap = cv2.VideoCapture(path)
    cv2.namedWindow('Video Player', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Video Player', 1280, 720)

    if not cap.isOpened():
        print("Error opening video file")
        return

    print("Video player started")
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Video Player', frame)
        else:
            # Restart the same video if it reaches the end
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Quit condition (close the window properly)
        if (cv2.waitKey(36) & 0xFF == ord('q')) or cv2.getWindowProperty('Video Player', cv2.WND_PROP_VISIBLE) < 1:
            break

        elif path != f'{FILE}/{faceStr}.{EXT}':
            e1 = cv2.getTickCount()
            path = f'{FILE}/{faceStr}.{EXT}'
            cap.release()  # Release old video
            cap = cv2.VideoCapture(path)  # Load new video
            e2 = cv2.getTickCount()
            print((e2-e1)/cv2.getTickFrequency())

            if not cap.isOpened():
                print("Error opening video:", path)
                cap = cv2.VideoCapture('{FILE}/210.{EXT}')  # Fallback video

    cap.release()
    cv2.destroyAllWindows()
    sys.exit()

### OSC Server ###
values = {}

def val_handler(address, *args):
    #print(f"VALUE {address}: {args}")
    values[args[0]] = args[1]

def apply_handler(address, *args):
    global faceStr
    faceStr = calc_pose(values)


def default_handler(address, *args):
    return

def calc_pose(params):
    faceAngleY = params["FaceAngleY"]
    faceAngleX = params["FaceAngleX"]
    mouthOpen = params["MouthOpen"]
    eyeOpenLeft = params["EyeOpenLeft"]
    eyeOpenRight = params["EyeOpenRight"]

    updown = "2"
    leftright = "1"
    mouth = "0"
    eyes = "0"

    if faceAngleY > thresholds["up"]:
        updown = "2"
    elif faceAngleY < thresholds["down"]:
        updown = "0"
    else:
        updown = "1"

    if faceAngleX > thresholds["farright"]:
        leftright = "4"
    elif faceAngleX > thresholds["right"]:
        leftright = "3"
    elif faceAngleX < thresholds["farleft"]:
        leftright = "0"
    elif faceAngleX < thresholds["left"]:
        leftright = "1"
    else:
        leftright = "2"

    if mouthOpen > thresholds["mouthopen"]:
        mouth = "1"
    else:
        mouth = "0"

    if eyeOpenLeft > thresholds["eyeblink"] or eyeOpenRight > thresholds["eyeblink"]:
        eyes = "0"
    else:
        eyes = "1"

    return (leftright + updown + mouth + eyes)

async def osc_server_task():
    loop = asyncio.get_running_loop()
    dispatcher = Dispatcher()
    dispatcher.map("/VMC/Ext/Blend/Val", val_handler)
    dispatcher.map("/VMC/Ext/Blend/Apply", apply_handler)
    dispatcher.set_default_handler(default_handler)

    server = osc_server.AsyncIOOSCUDPServer((HOST, OSC_PORT), dispatcher, loop)
    transport, protocol = await server.create_serve_endpoint()
    print(f"OSC listening at {OSC_PORT}")
    try:
        await asyncio.Future()  # Keeps server running
    finally:
        transport.close()

### Main Async Function ###
async def main():
    _= asyncio.create_task(osc_server_task())
    thread = asyncio.to_thread(video_player)  # Run OpenCV loop
    await thread

if __name__ == "__main__":
    asyncio.run(main())
