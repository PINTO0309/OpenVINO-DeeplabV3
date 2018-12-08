# OpenVINO-DeeplabV3
[4-5 FPS / Core m3 CPU only] [11 FPS / Core i7 CPU only]  
OpenVINO+DeeplabV3+LattePandaAlpha. CPU / GPU / NCS. RealTime semantic-segmentaion.   Python3.5+OpenCV3.4.3+PIL  
  
**【Japanese article / English article】**  
**[（１） Introducing Ubuntu 16.04 + OpenVINO to Latte Panda Alpha 864 (without OS included) and enjoying Semantic Segmentation with Neural Compute Stick and Neural Compute Stick 2](https://qiita.com/PINTO/items/5ac8f4395e190d06cfab#introducing-ubuntu-1604--openvino-to-latte-panda-alpha-864-without-os-included-and-enjoying-semantic-segmentation-with-neural-compute-stick-and-neural-compute-stick-2)**  
  
**[（２） Real-time Semantic Segmentation with CPU alone [part2] [4-5 FPS / Core m3 CPU only] [11-12 FPS / Core i7 CPU only] DeeplabV3+MobilenetV2](https://qiita.com/PINTO/items/15d822c3d280c42e08c8)**
  
  
# Results
**【Result 1】 Click the image below to play Youtube video. (Core m3 + CPU only mode. 4.0FPS - 5.0FPS)**  
[<img src="media/sample01.jpg" width=60%>](https://youtu.be/CxxDwK7vBAo)  
  
**【Result 2】 Click the image below to play Youtube video. (Core m3 + CPU only mode. 4.0FPS - 5.0FPS)**  
[<img src="media/sample02.jpg" width=60%>](https://youtu.be/-pXB3dDj-rQ)  
  
**【Result 3】 Click the image below to play Youtube video. (Core m3 + CPU only mode. 4.0FPS - 5.0FPS)**  
[<img src="media/sample03.jpg" width=60%>](https://youtu.be/1NLCr5XnVX8)  

**【Result 4】 Click the image below to play Youtube video. (Core i7 + CPU only mode. 11.0FPS - 12.0FPS)**  
[<img src="media/sample04.jpg" width=60%>](https://youtu.be/TjiH2dMltl4)  
  
# Environment
- LattePanda Alpha (Intel 7th Core m3-7y30)
- Ubuntu 16.04 x86_64
- OpenVINO toolkit 2018 R4 (2018.4.420)
- Python 3.5
- OpenCV 3.4.3
- PIL
- Tensorflow v1.11.0
- DeeplabV3 + MobilenetV2 (Pascal VOC 2012)
- USB Camera (PlaystationEye)
- 【option】 Intel Neural Compute Stick / Intel Neural Compute Stick 2 or GPU

# Usage
### 1. Installation of OpenVINO main unit
#### 1.1 Download
```bash
$ cd ~/Downloads
$ curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=18-TeUzeN34CV-QqM0rO3wpdEGODTWrBc" > /dev/null
$ CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"
$ curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=18-TeUzeN34CV-QqM0rO3wpdEGODTWrBc" -o l_openvino_toolkit_p_2018.4.420.tgz
$ tar -zxf l_openvino_toolkit_p_2018.4.420.tgz
$ cd l_openvino_toolkit_p_2018.4.420
```
#### 1.2 Install basic functions
```bash
## GUI version installer
$ sudo ./install_GUI.sh
or
## CUI version installer
$ sudo ./install.sh
```
<img src="media/01.jpg" width=60%>
<img src="media/02.jpg" width=60%>
<img src="media/03.jpg" width=60%>

```bash
$ cd /opt/intel/computer_vision_sdk/install_dependencies
$ sudo -E ./install_cv_sdk_dependencies.sh
$ nano ~/.bashrc
source /opt/intel/computer_vision_sdk/bin/setupvars.sh

$ source ~/.bashrc
$ cd /opt/intel/computer_vision_sdk/deployment_tools/model_optimizer/install_prerequisites
$ sudo ./install_prerequisites.sh
```
#### 1.3 Install optional features
##### 1.3.1 Additional installation steps for the Intel® Movidius™ Neural Compute Stick and Intel® Neural Compute Stick 2
```bash
$ sudo usermod -a -G users "$(whoami)"
$ cat <<EOF > 97-usbboot.rules
SUBSYSTEM=="usb", ATTRS{idProduct}=="2150", ATTRS{idVendor}=="03e7", GROUP="users", MODE="0666", ENV{ID_MM_DEVICE_IGNORE}="1"
SUBSYSTEM=="usb", ATTRS{idProduct}=="2485", ATTRS{idVendor}=="03e7", GROUP="users", MODE="0666", ENV{ID_MM_DEVICE_IGNORE}="1"
SUBSYSTEM=="usb", ATTRS{idProduct}=="f63b", ATTRS{idVendor}=="03e7", GROUP="users", MODE="0666", ENV{ID_MM_DEVICE_IGNORE}="1"
EOF
$ sudo cp 97-usbboot.rules /etc/udev/rules.d/
$ sudo udevadm control --reload-rules
$ sudo udevadm trigger
$ cd /opt/intel/common/mdf/lib64
$ sudo mv igfxcmrt64.so igfxcmrt64.so.org
$ sudo ln -s libigfxcmrt64.so igfxcmrt64.so
$ cd /opt/intel/mediasdk/lib64
$ sudo mv libmfxhw64.so.1 libmfxhw64.so.1.org
$ sudo mv libmfx.so.1 libmfx.so.1.org
$ sudo mv libva-glx.so.2 libva-glx.so.2.org
$ sudo mv libva.so.2 libva.so.2.org
$ sudo mv libigdgmm.so.1 libigdgmm.so.1.org
$ sudo mv libva-drm.so.2 libva-drm.so.2.org
$ sudo mv libva-x11.so.2 libva-x11.so.2.org
$ sudo ln -s libmfxhw64.so.1.28 libmfxhw64.so.1
$ sudo ln -s libmfx.so.1.28 libmfx.so.1
$ sudo ln -s libva-glx.so.2.300.0 libva-glx.so.2
$ sudo ln -s libva.so.2.300.0 libva.so.2
$ sudo ln -s libigdgmm.so.1.0.0 libigdgmm.so.1
$ sudo ln -s libva-drm.so.2.300.0 libva-drm.so.2
$ sudo ln -s libva-x11.so.2.300.0 libva-x11.so.2
$ sudo ldconfig
$ rm 97-usbboot.rules
```
##### 1.3.2 Additional installation steps for processor graphics (GPU)


### 2. Additional installation for Intel Movidius Neural Compute Stick v1 / v2
### 3. Upgrade to Tensorflow v1.11.0
### 4. Settings for offloading custom layer behavior to Tensorflow
### 5. Conversion of Tensorflow-DeeplabV3 model to lr format

# Reference article, thanks
https://github.com/FionaZZ92/OpenVINO.git  
https://medium.com/@oleksandrsavsunenko/optimizing-neural-networks-for-production-with-intels-openvino-a7ee3a6883d  
