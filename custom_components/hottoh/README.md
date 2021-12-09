# ha-hottoh-component
THIS IS A WIP project whit lots of regular changes, when it will have a correct level of features / quality it will be published to HACS


Custom Component for HottoH integration

Add the content of this repo in HA/config/custom_components

Restart HA and then add new HottoH integration

You will need IP Address of the HottoH stove and also port number (default: 5001)

This will add a climate to control the stove and also some sensors and switches.

Entities added to HA:

Climate with fan capability to control the stove

    - Support for preset eco, comfort, away
    - Support for fan speed (1, 2, 3, 4, 5, 6)
    
Sensor for: 

    - smoke temperature
    - Speed fan Smoke
    - Temperature Room 1 / 2 / 3 if available
    - Water temperature if available
    - Power Level
    - Speed Fan 1 / 2 / 3 if available

Binary Sensor for:

    - Water pump

Switch for:

    - Stove On / Off
    - Eco Mode On / Off
