# ReadHelper
Gaze detector from Webcam - Project for Technion , EE faculty.
Dor Arad & Tomer Keren

<table>
  <tr>
    <td>
<img src="https://i.postimg.cc/tRd9QxgS/readme-img.png" width="525" height="375">
<img src=".idea/video_screen.gif" width="388" height="388">
    </td>
  </tr>
  </table>

## Webcam requriements ##
1. at least 720p resolution
2. located in the top center of the screen

## Running the demo ##
1. Download repo
```
git clone https://github.com/araddor1/ReadHelper.git
```
2. install requriements:
```
pip install -r requirements.txt
```
3. run main.py
```
python main.py
```
4.Enter needed information

5.Enjoy!


## Structure
* `Calibration/` - all code regarding the calibration proccess
* `Tests/` - all code regarding the Testing proccess
* `FullFaceSolution/` - img to gaze solution based on [2]
* `HeadPoseBasedSolution/` - img to gaze solution based on [1]
* `Results/` - the accumulated result of the tested system (.csv files)
* `UtilsAndModels/` - collection of defines,models and utils methods needed across the system

## References ##
* [1] Zhang, Xucong, Yusuke Sugano, Mario Fritz, and Andreas Bulling. "Appearance-based Gaze Estimation in the Wild." Proc. of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2015. arXiv:1504.02863, Project Page
* [2] Zhang, Xucong, Yusuke Sugano, Mario Fritz, and Andreas Bulling. "It's Written All Over Your Face: Full-Face Appearance-Based Gaze Estimation." Proc. of the IEEE Conference on Computer Vision and Pattern Recognition Workshops(CVPRW), 2017. arXiv:1611.08860, Project Page
* [3] Zhang, Xucong, Yusuke Sugano, Mario Fritz, and Andreas Bulling. "MPIIGaze: Real-World Dataset and Deep Appearance-Based Gaze Estimation." IEEE transactions on pattern analysis and machine intelligence 41 (2017). arXiv:1711.09017
