# Aurum (Meetstekker) custom component for Home Assistant Core

The main usage for this module is supporting [Home Assistant](https://www.home-assistant.io) / [home-assistant](http://github.com/home-assistant/core/)

There are in total 23 sensors available:
```
1)  Battery power            #power-flow on the AC-side of the inverter-charger
    unit_of_measurement: "W"
2)  Consumed from Battery    #total provided AC power from the batteries
    unit_of_measurement: "kWh"
3)  Stored in Battery `      #total stored AC power into the batteries
    unit_of_measurement: "kWh"
4)  uCHP power               #power-flow from any electricity-producing device, other than from solar energy
    unit_of_measurement: "W"
5)  uCHP production          #total uCHP production
    unit_of_measurement: "kWh"
6)  uCHP consumption         #total uCHP consumption
    unit_of_measurement: "kWh"
7)  PV power                 #power-flow of the solar-inverterconnection
    unit_of_measurement: "W"
8)  PV consumption           #total solar-inverter consumption
    unit_of_measurement: "kWh"
9)  PV production            #total solar-inverter production
    nit_of_measurement: "kWh"
10) EV power                 #power-flow of the Electrical Vehicle connection
    unit_of_measurement: "W"
11) EV consumption           #total EV consumption
    unit_of_measurement: "kWh"
12) EV production            #total EV production
    unit_of_measurement: "kWh"
13) Main power               #power-flow of the electrical connection connected to the main meter
    (When there is no Smart Meter with P1-port, a suitable electricity-meter can be read out instead)
    unit_of_measurement: "W"
14) Main consumption         #total Electricity consumption
    unit_of_measurement: "kWh"
15) Main production          #total Electricity production
    unit_of_measurement: "kWh"
16) DSMR timestamp           #When a Smart Meter with P1-port is present, this and the below data is coming from the Smart Meter
17) E net consumption        #power-flow of the electrical connection connected to the DSMR meter with p1-port
    unit_of_measurement: "W"
18) E low in totals          #total Electricity consumption - low tariff
    unit_of_measurement: "kWh"
19) E low out totals         #total Electricity export - low tariff
    unit_of_measurement: "kWh"
20) E high in totals         #total Electricity consumption - high tariff
    unit_of_measurement: "kWh"
21) E high out totals        #total Electricity export - high tariff
    unit_of_measurement: "kWh"
22) Gas rate                 #gas-flow, works only with an analog gas meter, needs a special add on
    unit_of_measurement: "m3/hr"
23) Gas totals               #total gas consumption
    unit_of_measurement: "m3"
```

# Installation

Install the custom_component manually or via HACS: add this repository as a custom repository.

After the files have been installed in HA Core, restart HA Core. After the restart, go to Configuration --> Integrations and press the "+" button.
Enter "Aurum" into the search-bar, select the found Aurum-beta-component. 
Next, enter in the pop-up windows the IP-address of the Meetstekker and the numbers of the sensors you want to add:

Look at http://'ip-address-of-the-Aurum-unit'/measurements/output.xml to find out which sensors show actual values. Then modify the numbers during configuration: enter for instance: 16,17,18,20,23

**NOTE: always use sensor 16.** 
Also, the numbers cannot be mixed, they must be entered in ascending order.

# Options

The Aurum integration has an OPTIONS-button. It can be used to change the default data-refresh-interval (= 10 secs).
