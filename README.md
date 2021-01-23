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
# step 1: get parameters from config file
    configuration()
# step 2: create PixeLook
    my_px_gt = PixeLook_from_config(config['settings'])
# step 3: calibrate 
    my_px_gt.calibrate()
# step 4: use the app as defined mode
    if mode == "dots":
        my_px_gt.draw_live()
    elif mode == "screenshots":
        my_px_gt.start_screen_shots(post=post, webcam=webcam)
    elif mode == "none":
        my_px_gt.run_in_background(post=post)
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
3. Install dlib:
if using conda:
```
conda install -c conda-forge dlib
```
else, install via visual studio c++

4. Edit the config.txt file (explenation inside)

5. Run demo.py
```
python Demo.py
```
5.Enjoy!

## References ##
* [1] Zhang, Xucong, Yusuke Sugano, Mario Fritz, and Andreas Bulling. "It's Written All Over Your Face: Full-Face Appearance-Based Gaze Estimation." Proc. of the IEEE Conference on Computer Vision and Pattern Recognition Workshops(CVPRW), 2017. arXiv:1611.08860, Project Page
* [2] Zhang, Xucong, Yusuke Sugano, Mario Fritz, and Andreas Bulling. "MPIIGaze: Real-World Dataset and Deep Appearance-Based Gaze Estimation." IEEE transactions on pattern analysis and machine intelligence 41 (2017). arXiv:1711.09017
* [3] Full-Face net Implemention on with smaller net - https://github.com/glefundes/mobile-face-gaze
