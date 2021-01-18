# PixelLook
Multy platform gaze detector based on It's Written All Over Your Face [1] article.

Includes:
1. Drawing app - draw dots with your eyes
2. Data Collection - saves all pixels looked in a csv file
3. Screen capture - creates video of your screen with mark on the gazed area.
4. Library API - a simple API to use this project to make you own gaze-based app

<table>
  <tr><td>
<img src=".idea/waldo_final.gif"  width="450" height="300">
    Mac
    </td><td>
<img src=".idea/netflixgif.gif"  width="450" height="300">
    Linux
    </td> </tr></table>

## Webcam requriements ##
1. at least 720p resolution
2. located in the top center of the screen

## Using The API ##
The api made simple as possible.
for example:

```python
from PixeLook import PixeLook

def __main__():
    
    ## Option 1: Create PixelGetter with arguments in code
    my_px_gt = PixeLook(screen_size=13.3, camera_number=0)  
    ## Option 2: Create PixelGetter from config file (see config.txt in this repo)
    my_px_gt = PixeLook.create_from_file() # "config.txt" is the default 
    
    my_px_gt.calibrate() # start the calibration process (GUI)
    cur_pixel = my_px_gt.get_pixel() #use this method to get the cur pixel from webcam.
    if cur_pixel[0]>my_px_gt.screen_width/2: # (x,y) = (cur_pixel[0],cur_pixel[1])
        print("you are looking in the right side of the screen!")

    my_px_gt.set_screen_shots(with_webcam=True) # set a screen shot video params
    my_px_gt.start_screen_shots(max_frames=100) # start the screen record session (new thread)
    wait(100)
    my_px_gt.stop_screen_shots()    # stop screen recording thread
```


## Running the demo ##
1. Download repo
```
git clone https://github.com/araddor1/ReadHelper.git
```
2. Install requriements:
```
pip install -r requirements.txt
```
3. Edit the config.txt file (explenation inside)

4. Run demo.py
```
python Demo.py
```
5.Enjoy!

## References ##
* [1] Zhang, Xucong, Yusuke Sugano, Mario Fritz, and Andreas Bulling. "It's Written All Over Your Face: Full-Face Appearance-Based Gaze Estimation." Proc. of the IEEE Conference on Computer Vision and Pattern Recognition Workshops(CVPRW), 2017. arXiv:1611.08860, Project Page
* [2] Zhang, Xucong, Yusuke Sugano, Mario Fritz, and Andreas Bulling. "MPIIGaze: Real-World Dataset and Deep Appearance-Based Gaze Estimation." IEEE transactions on pattern analysis and machine intelligence 41 (2017). arXiv:1711.09017
* [3] Full-Face net Implemention on with smaller net - https://github.com/glefundes/mobile-face-gaze
