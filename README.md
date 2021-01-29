# digit_detector_easyocr

System for detection and recognition of train plate numbers based on EasyOCR




## Anaconda [https://docs.anaconda.com/anaconda/install/linux/]

### To install:

* Install dependencies:

```
$ apt-get install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6
```

* Download the Anaconda installer for Linux available at https://www.anaconda.com/products/individual#linux.

* Run Anaconda installer:

```
$ bash $HOME/Downloads/Anaconda3-2020.02-Linux-x86_64.sh
```

### To run:

* Create an Anaconda environment: 

```
$ conda create -n easyocr python=3.6
$ activate easyocr # in linux "source activate easyocr"
(easyocr) $ pip install -r requirements.txt
(easyocr) $ pip install -e .
```

* In order not to run Anaconda every time a terminal is opened, comment out the last lines added to .bashrc by the Anaconda installer.




## Digit Detector Based on EasyOCR [https://github.com/JaidedAI/EasyOCR]

### To install:

```
$ pip install python-bidi
$ pip3 install scikit-build
$ pip3 install easyocr
```

### To run:

* Activate Anaconda environment:

```
$ . "$HOME/anaconda3/etc/profile.d/conda.sh"
$ conda activate easyocr
```

* Run the digit detector:

```
$ cd digit_detector_easyocr
$ python pred_easyocr_win.py -g ground_truths/ground_truth.txt  -n train_numbers/train_numbers.txt
```




