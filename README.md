# data-preprocessing

This repo contains a script that finds, processes and psuedonymizes the data.

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
