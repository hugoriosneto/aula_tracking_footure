@echo off
ECHO Setting up virtual environment for Football Tracking Visualization...

REM Create virtual environment
python -m venv venv
ECHO Virtual environment created in .\venv\

REM Activate the virtual environment
CALL venv\Scripts\activate

ECHO Virtual environment activated

REM Install requirements
pip install --upgrade pip
ECHO Installing required packages...
pip install -r requirements.txt

REM Download sample data
ECHO Downloading sample data...
python download_sample_data.py

ECHO.
ECHO Setup completed successfully!
ECHO.
ECHO To activate the virtual environment again later:
ECHO   venv\Scripts\activate
ECHO.
ECHO To run the notebooks:
ECHO jupyter notebook
ECHO.

PAUSE 