<p align="center">
    <img style="width: 35%; height: 35%" src="quimia4abc.svg">
</p>

# data-preprocessing

This repo contains a script that finds, processes and psuedonymizes the data for the QUMIA project.
The project as a whole uses ultrasound data from patients who may have various neurological diseases,
and explores computational models for diagnosis and classification.

As every hospital system will have multiple ways in which such data is stored, thus
programs in this particular repository are not meant to be generalizable. Work on machine learning models 
for diagnosis and classification based on patient data including ultrasounds
is held in a different repository. If you are interested in applying this kind of analysis or
collaborating with us please contact Candace Makeda Moore at c.moore@esciencecenter.nl . 

## Dependencies

```
dotenv
numpy
pandas
pyreadstat
pydicom
opencv-python
scipy
```

## Configure

The script will look for a number of environment variables (ideally put them in a .env file in the project root):

```
QU_SALT         # Secret for id pseudonymization
QU_INPUT        # Input SPSS file
QU_OUTPUT       # Where to put the resulting csv file
QU_IMG_IN_DIR   # Where to find the image directories
QU_IMG_OUT_DIR  # Where to put the converted images
```

## Run

Simply run `python main.py`
