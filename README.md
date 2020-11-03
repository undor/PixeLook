# ReadHelper
Gaze detector Python Pkg API

<table>
  <tr><td>
<img src="https://i.postimg.cc/tRd9QxgS/readme-img.png" width="262" height="187">
<img src=".idea/video_screen.gif" width="190" height="190">
   </td></tr></table>

## Webcam requriements ##
1. at least 720p resolution
2. located in the top center of the screen

## Using The API ##
The api made simple as possible.
for example:

```python
from PixeLook import PixeLook

def __main__():
    my_px_gt = PixeLook(screen_size=13.3, camera_number=0) #Create PixelGetter
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
2. install requriements:
```
pip install -r requirements.txt
```
3. run demo.py
```
python main.py
```
4.Enter needed information

5.Enjoy!

## References ##
* [1] Zhang, Xucong, Yusuke Sugano, Mario Fritz, and Andreas Bulling. "It's Written All Over Your Face: Full-Face Appearance-Based Gaze Estimation." Proc. of the IEEE Conference on Computer Vision and Pattern Recognition Workshops(CVPRW), 2017. arXiv:1611.08860, Project Page
* [2] Zhang, Xucong, Yusuke Sugano, Mario Fritz, and Andreas Bulling. "MPIIGaze: Real-World Dataset and Deep Appearance-Based Gaze Estimation." IEEE transactions on pattern analysis and machine intelligence 41 (2017). arXiv:1711.09017
