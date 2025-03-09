# Stop-Motion-VTuber-Thing
Allows for facetracking and such using pre-rendered videos and VBridger (Hoping to add VTS support perchance). Operates using OpenCV

HOW TO USE:

Config:
- IP set to local device IP or device where VBridger is running
- Port set to VBridger VMC port (on the bottom-right of VBridger, switch from VTS to VMC)
- Video folder set to the name of the folder where all the videos are (make sure it's in the SAME directory)
- File Ext set to the file extension of the videos

Thresholds:
- Activation trigger amount for each parameter
- Just play around with it tbh

Videos:
- 5 horizontal positions (far-left, left, centre, right, far-right)
- 3 vertical positions (down, centre, right)
- Mouth closed or open
- Eyes open or closed
- Each parameter has a respective number from 0-n (where n in the amount of positions - 1)
- Default facing forward would be 2100 (centre, cetre, mouth closed, eyes open)
- The faces folder has examples for each
- Make sure to name the videos according to the numbers!
- Add a green background when you render (i forgor sorry)
