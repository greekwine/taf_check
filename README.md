The Taf Check was created by the GreekWine-Groupe to collect, compare and check METAR-Data with TAF-Data. This project is still under development (for more information check "Targets"-section)

Installation Guide :

Requirements : 
 - numpy~=2.2.6
 - xarray~=2025.6.1
 - pandas~=2.3.0

Installation :
 - Get taf-check via github
 - use pip install -r requirements.txt to get all the packages
 - it its recommended to create a new venv in any case 

How to get started: 

You can use the program easy by running the "main.py".  

The default settings are generating a txt/nc-file for the airport in Bremen with the ICAO-Indicator 'EDDW' for a specific "default" time-range between the 7.6.2025 at 11 UTC to 8.6.2025 at 9:59 UTC. You can change these settings only in the main.py under "__name__". 

<img width="379" height="455" alt="greekwine" src="https://github.com/user-attachments/assets/21eadebe-cead-4421-a96f-4e6f6b2c56a3" />


Features: 
- Connect to ogimet.com and get METAR and TAF-Data for a specific time range via METAR/TAF-Queries
- Save these informations on your local computer as .txt-file
- Parse the METAR into different parts like visibilty, weather, wind or clouds and save these parts into a nc-file

Targets and Futher Development:
- Check with METAR-Data with the TAF
- Does the METAR fit to the TAF using DWD-Tresholds?
- Create a Tkinter-Window with the METAR/TAF as an overview 
  - Is-Taf correct/wrong?
  - Need the meteorologist change (AMD) or correct (COR) the TAF?

  -> yes/no
  -> why?
  -> per Parameter and oberservation
    
- Create an AUTO-TAF with DMO via https://github.com/earthobservations/wetterdienst 
  (More Info : https://wetterdienst.readthedocs.io/en/latest/data/overview/)

Contributing:
You can support our development by giving feedback, testing the code or by finding and reporting bugs to us. 
If you are interested you can also join our project directly by contacting our group. 
