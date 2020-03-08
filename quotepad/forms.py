from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from quotepad.models import Document, Profile, ProductPrice, ProductComponent
from django.forms import ModelMultipleChoiceField

# For Editing the template
from django.conf import settings
from pathlib import Path

''' Section to define the boiler quote form field dropdown values and choices '''
OWNER_OR_TENANT_DROPDOWN = (
	('Owner','Owner'),
	('Tenant','Tenant'),
)

PROPERTY_TYPE_DROPDOWN = (
	('Detached','Detached'),
	('Semi Detached','Semi Detached'),
	('Terraced','Terraced'),
	('End of Terrace','End of Terrace'),
	('Bungalow','Bungalow'),
	('Flat','Flat'),
)

CURRENT_FUEL_TYPE_DROPDOWN = (
	('Gas','Gas'),
	('LPG','LPG'),
	('Oil','Oil'),
	('Electric','Electric'),
	('N/A','N/A'),
)

CURRENT_BOILER_TYPE_DROPDOWN = (
	('Combi','Combi'),
	('Conventional Wall Hung','Conventional Wall Hung'),
	('Conventional Flor Standing','Conventional Flor Standing'),
	('System','System'),
	('Back Boiler','Back Boiler'),
	('Water Heater','Water Heater'),
	('No Existing System','No Existing System'),
	('N/A','N/A'),
)

CURRENT_BOILER_LOCATION_DROPDOWN = (
	('Kitchen','Kitchen'),
	('Bathroom','Bathroom'),
	('Bedroom','Bedroom'),
	('Utility','Utility'),
	('Airing Cupboard','Airing Cupboard'),
	('Lounge','Lounge'),
	('Utility Room','Utility Room'),
	('WC','WC'),
	('Pantry','Pantry'),
	('Basement','Basement'),
	('Loft','Loft'),
	('Garage','Garage'),
	('Outdoor Room','Outdoor Room'),
	('Other','Other'),
)

CURRENT_FLUE_SYSTEM_DROPDOWN = (
	('Horizontal Flue','Horizontal Flue'),
	('Vertical Flue','Vertical Flue'),
	('Rear Flue','Rear Flue'),
	('No Existing Flue','No Existing Flue'),
	('N/A','N/A'),
)

CURRENT_FLUE_LOCATION_DROPDOWN = (
	('Ground Floor','Ground Floor'),
	('First Floor','First Floor'),
	('Second Floor','Second Floor'),
	('Third Floor','Third Floor'),
	('Fourth Floor','Fourth Floor'),
	('Fifth Floor','Fifth Floor'),
	('Above Fifth Floor','Above Fifth Floor'),
	('N/A','N/A'),
)

CURRENT_CONTROLS_DROPDOWN = (
	('No Controls Installed','No Controls Installed'),
	('Wired Programmer','Wired Programmer'),
	('Wired Thermostat','Wired Thermostat'),
	('Wireless Programmer','Wireless Programmer'),
	('Wireless Thermostat','Wireless Thermostat'),
	('Internet Connected Thermostat','Internet Connected Thermostat'),
)

REMOVALS_CHOICES = (
	('Old Boiler','Old Boiler'),
	('Hot Water Cylinder','Hot Water Cylinder'),
	('Cold Water Tank','Cold Water Tank'),
	('Feed and Expansion Tank','Feed and Expansion Tank'),
	('Gas Back Boiler + Fire','Gas Back Boiler + Fire'),
	('Solid Fuel Back Boiler + Fire','Solid Fuel Back Boiler + Fire'),
	('Warm Air Unit','Warm Air Unit'),
	('Fireplace','Fireplace'),
	('Multipoint Water Heater','Multipoint Water Heater'),
	('Shower Pump','Shower Pump'),
)

NEW_FUEL_TYPE_DROPDOWN = (
	('Gas','Gas'),
	('LPG','LPG'),
	('Oil','Oil'),
)

NEW_BOILER_TYPE_DROPDOWN = (
	('Combi','Combi'),
	('Conventional','Conventional'),
	('System','System'),
)

NEW_BOILER_LOCATION_DROPDOWN = (
	('Kitchen','Kitchen'),
	('Bathroom','Bathroom'),
	('Bedroom','Bedroom'),
	('Utility','Utility'),
	('Airing Cupboard','Airing Cupboard'),
	('Lounge','Lounge'),
	('Utility Room','Utility Room'),
	('WC','WC'),
	('Pantry','Pantry'),
	('Basement','Basement'),
	('Loft','Loft'),
	('Garage','Garage'),
	('Outdoor Room','Outdoor Room'),
	('Other','Other'),
)

NEW_FLUE_SYSTEM_DROPDOWN = (
	('Horizontal','Horizontal'),
	('Vertical','Vertical'),
	('Rear Flue','Rear Flue'),
)

NEW_FLUE_LOCATION_DROPDOWN = (
	('Ground Floor','Ground Floor'),
	('First Floor','First Floor'),
	('Second Floor','Second Floor'),
	('Third Floor','Third Floor'),
	('Fourth Floor','Fourth Floor'),
	('Fifth Floor','Fifth Floor'),
	('Above Fifth Floor','Above Fifth Floor'),
	('N/A','N/A'),
)

NEW_FLUE_DIAMETER_DROPDOWN = (
	('100mm','100mm'),
	('125mm','125mm'),
)

PLUME_MANAGEMENT_KIT_DROPDOWN = (
	('Required','Required'),
	('Not Required','Not Required'),
)

CONDENSATE_TERMINATION_DROPDOWN = (
	('Drain','Drain'),
	('Sink','Sink'),
	('Soil Vent Pipe','Soil Vent Pipe'),
	('External Gully','External Gully'),
	('Pumped','Pumped'),
	('Soakaway Trap','Soakaway Trap'),
	('Internal Waste Point','Internal Waste Point'),
)
NEW_CONTROLS_DROPDOWN = (
	('Connect on to Existing','Connect on to Existing'),
	('New Programmer Only','New Programmer Only'),
	('New Thermostat Only','New Thermostat Only'),
	('New Programmer + Thermostat','New Programmer + Thermostat'),
)

CWS_FLOW_RATE_DROPDOWN = (
	('1','1'),
	('2','2'),
	('3','4'),
	('4','4'),
	('5','5'),
	('6','6'),
	('7','7'),
	('8','8'),
	('9','9'),
	('10','10'),
	('11','11'),
	('12','12'),
	('13','13'),
	('14','14'),
	('15','15'),
	('16','16'),
	('17','17'),
	('18+','18+'),
)

NEW_FLUE_METRES_DROPDOWN = (
	('1','1'),
	('2','2'),
	('3','3'),
	('4','4'),
	('5','5'),
	('6','6'),
	('7','7'),
	('8','8'),
	('9','9'),
	('10','10'),
	('11','11'),
	('12','12'),
)

SYSTEM_TREATMENT_DROPDOWN = (
	('Chemical Flush & Inhibitor','Chemical Flush & Inhibitor'),
	('Magna Pro Flush & Inhibitor','Magna Pro Flush & Inhibitor'),
	('Power Flush & Inhibitor','Power Flush & Inhibitor'),
)

GAS_SUPPLY_DROPDOWN = (
	('Current Gas supply deemed satisfactory','Current Gas supply deemed satisfactory'),
	('Adaptation to existing gas supply required','Adaptation to existing gas supply required'),
	('New external gas supply required','New external gas supply required'),
	('New internal gas supply required','New internal gas supply required'),
)

GAS_SUPPLY_LENGTH_DROPDOWN = (
	('N/A','N/A'),
	('3m','3m'),
	('6m','6m'),
	('9m','9m'),
	('12m','12m'),
	('15m','15m'),
	('18m','18m'),
	('21m','21m'),
	('24m','24m'),
	('27m','27m'),
	('30m','30m'),
)

ASBESTOS_CONTAINING_MATERIALS_IDENTIFIED_DROPDOWN = (
	('No Asbestos Identified','No Asbestos Identified'),
	('Potential Asbestos Containing Material Identified','Potential Asbestos Containing Material Identified'),
)

ASBESTOS_REMOVAL_PROCEDURE_DROPDOWN = (
	('N/A','N/A'),
	('Your Heat to remove during installation','Your Heat to remove during installation'),
	('Client to arrange removal prior to installation','Client to arrange removal prior to installation'),
	('No disruption necessary','No disruption necessary'),
)

POTENTIAL_CONTRACTOR_ATTENDANCE_REQUIRED_DROPDOWN = (
	('No','No'),
	('Yes','Yes'),
)

ELECTRICAL_WORK_REQUIRED_DROPDOWN = (
	('Connect to existing wiring','Connect to existing wiring'),
	('New wiring to fuse spur','New wiring to fuse spur'),
	('New wiring S plan','New wiring S plan'),
	('New wiring Y plan','New wiring Y plan'),
	('New boiler on plug','New boiler on plug'),
)

BOILER_MANUFACTURER_DROPDOWN = (
	('Worcester Bosch','Worcester Bosch'),
	('Viessmann','Viessmann'),
	('Vaillant','Vaillant'),
	('Glowworm','Glowworm'),
	('Ideal','Ideal'),
	('Baxi','Baxi'),
	('Potterton','Potterton'),
)

MANUFACTURER_GUARANTEE_DROPDOWN = (
	('5 Years','5 Years'),
	('6 Years','6 Years'),
	('7 Years','7 Years'),
	('8 Years','8 Years'),
	('9 Years','9 Years'),
	('10 Years','10 Years'),
)

FLUE_COMPONENTS_DROPDOWN = (
	('Horizontal Flue Kit','Horizontal Flue Kit'),
	('Vertical Flue Kit','Vertical Flue Kit'),
	('Flue Extension','Flue Extension'),
	('Pair 45 Degree Bends','Pair 45 Degree Bends'),
	('Single 90 Degree Bend','Single 90 Degree Bend'),
	('Roof Flashing','Roof Flashing'),
)

PROGRAMMER_THERMOSTAT_DROPDOWN = (
	('Drayton Twin Channel Programmer','Drayton Twin Channel Programmer'),
	('Drayton Single Channel Programmer','Drayton Single Channel Programmer'),
	('Drayton RTS1 Room Thermostat','Drayton RTS1 Room Thermostat'),
	('Siemens Wireless Thermostat','Siemens Wireless Thermostat'),
	('Nest Smart Thermostat','Nest Smart Thermostat'),
	('ESI Smart Thermostat','ESI Smart Thermostat'),
	('Drayton Y Plan Pack','Drayton Y Plan Pack'),
	('Drayton S Plan Pack','Drayton S Plan Pack'),
	('None Required','None Required'),
)

CENTRAL_HEATING_SYSTEM_FILTER_DROPDOWN = (
	("Unable to Install - None Required","Unable to Install - None Required"),
    ("Use Existing","Use Existing"),
    ("(1x) Magnaclean Atom (22mm)","(1x) Magnaclean Atom (22mm)"),
    ("(1x) Magnaclean Pro2 (22mm)","(1x) Magnaclean Pro2 (22mm)"),
    ("(1x) Magnaclean Pro2 (28mm)","(1x) Magnaclean Pro2 (28mm)"),
    ("(1x) Magnaclean Pro3 Sense (22mm)","(1x) Magnaclean Pro3 Sense (22mm)"),
    ("(1x) Greenstar System Filter 22mm 7733600236","(1x) Greenstar System Filter 22mm 7733600236"),
    ("(1x) Greenstar System Filter 28mm 7733600237","(1x) Greenstar System Filter 28mm 7733600237"),
)

SCALE_REDUCER_DROPDOWN = (
	('No Scale Reducer Required','No Scale Reducer Required'),
	('(1x) 22mm Inline Scale Reducer','(1x) 22mm Inline Scale Reducer'),
	('(1x) 15mm Inline Scale Reducer','(1x) 15mm Inline Scale Reducer'),
	('(1x) 28mm Inline Scale Reducer','(1x) 28mm Inline Scale Reducer'),
)

RADIATOR_REQUIREMENTS_DROPDOWN = (
	('N/A','N/A'),
	('Thermostatic Radiator Valves Only','Thermostatic Radiator Valves Only'),
	('Thermostatic Radiator Valves and Lock Shield','Thermostatic Radiator Valves and Lock Shield'),
	('New Panel Radiators and Valves','New Panel Radiators and Valves'),
)

ESTIMATED_DURATION_DROPDOWN = (
	('1 Day','1 Day'),
	('2 Days','2 Days'),
	('3 Days','3 Days'),
	('4 Days','4 Days'),
	('5 Days','5 Days'),
)

''' Dropdowns for Yourheat forms '''

CUSTOMER_TITLE_DROPDOWN = (
	('Mr','Mr'),
	('Mrs','Mrs'),
	('Miss','Miss'),
	('Ms','Ms'),
	('Dr','Dr'),
)

OWNER_TENANT_OR_LANDLORD_DROPDOWN = (
	('Owner','Owner'),
	('Tenant','Tenant'),
	('Landlord','Landlord'),
)

CURRENT_RADIATORS_WORKING_CORRECTLY_DROPDOWN = (
	('Yes', 'Yes'),
	('No', 'No'),
	('Boiler Non-Operational', 'Boiler Non-Operational'),
)

INCOMING_FLOW_RATE_DROPDOWN = (
	('1','1'),
	('2','2'),
	('3','3'),
	('4','4'),
	('5','5'),
	('6','6'),
	('7','7'),
	('8','8'),
	('9','9'),
	('10','10'),
	('11','11'),
	('12','12'),
	('13','13'),
	('14','14'),
	('15','15'),
	('16','16'),
	('17','17'),
	('18','18'),
	('19','19'),
	('20','20'),
	('21','21'),
	('22','22'),
	('23','23'),
	('24','24'),
	('25','25'),
	('26','26'),
	('27','27'),
	('28','28'),
	('29','29'),
	('30','30'),
)

WILL_BOILER_BE_HOUSED_IN_CUPBOARD_DROPDOWN = (
	('Yes', 'Yes'),
	('No', 'No'),	
)

CHEMICAL_SYSTEM_TREATMENT_DROPDOWN = (
	('Chemical Flush & Inhibitor','Chemical Flush & Inhibitor'),
	#('Magna Pro Flush & Inhibitor','Magna Pro Flush & Inhibitor'),
	('Chemical Powerflush & Inhibitor','Chemical Powerflush & Inhibitor'),
)

SCAFFOLDING_REQUIRED_DROPDOWN = (
	('No Scaffolding Required', 'No Scaffolding Required'),	
	('One Storey Scaffold Required', 'One Storey Scaffold Required'),
	('Two Storey Scaffold Required', 'Two Storey Scaffold Required'),
	('Three Storey Scaffold Required', 'Three Storey Scaffold Required'),
	('Four Storey Scaffold Required', 'Four Storey Scaffold Required'),
	('Five Storey Scaffold Required', 'Five Storey Scaffold Required'),
	('Five+ Storey Scaffold Required', 'Five+ Storey Scaffold Required'),
)

PROGRAMMER_THERMOSTAT_DROPDOWN = (
	("(1x) Controller Included With Boiler (Worcester 2000)","(1x) Controller Included With Boiler (Worcester 2000)"),
    ("(1x) Worcester Comfort Plug In 7733600003","(1x) Worcester Comfort Plug In 7733600003"),
    ("(1x) Worcester Comfort 1 RF 7733600001","(1x) Worcester Comfort 1 RF 7733600001"),
    ("(1x) Worcester Comfort 2 RF 7733600002","(1x) Worcester Comfort 2 RF 7733600002"),
    ("(1x) NEST 3rd GEN Thermostat","(1x) NEST 3rd GEN Thermostat"),
    ("(1x) NEST Cradle Stand","(1x) NEST Cradle Stand"),
    ("(1x) Neomitis RT7RF Plus Wireless 7 Day Programmable Stat","(1x) Neomitis RT7RF Plus Wireless 7 Day Programmable Stat"),
    ("(1x) Honeywell DT92 Wireless stat","(1x) Honeywell DT92 Wireless stat"),
    ("(1x) Honeywell 7-day Single Channel ST9100C","(1x) Honeywell 7-day Single Channel ST9100C"),
    ("(1x) Honeywell ST9400C Two Channel Programmer","(1x) Honeywell ST9400C Two Channel Programmer"),
    ("(1x) Honeywell ST9500C Two Zone","(1x) Honeywell ST9500C Two Zone"),
    ("(1x) Honeywell DT90E Room Thermostat  [Wired]","(1x) Honeywell DT90E Room Thermostat [Wired]"),
    ("(1x) Honeywell T6360B1028 Room Thermostat Standard","(1x) Honeywell T6360B1028 Room Thermostat Standard"),
    ("(1x) Honeywell T4360 Frost Thermostat","(1x) Honeywell T4360 Frost Thermostat"),
    ("(1x) Honeywell ST9420C Wireless Programmer","(1x) Honeywell ST9420C Wireless Programmer"),
    ("(1x) Honeywell DT92E Wireless Room Thermostat","(1x) Honeywell DT92E Wireless Room Thermostat"),
    ("(1x) Hive Internet Connected Thermostat","(1x) Hive Internet Connected Thermostat"),
    ("(1x) See description of works for controls","(1x) See description of works for controls"),
)

ADDITIONAL_CENTRAL_HEATING_COMPONENTS_DROPDOWN = (
	("No Additional Central Heating Components","No Additional Central Heating Components"),
    ("(1x) Grundfos UPS2 15-50/60 22mm Complete Pump (With Valves)","(1x) Grundfos UPS2 15-50/60 22mm Complete Pump (With Valves)"),
    ("(1x) Grundfos UPS2 15-50/60 28mm Complete Pump (With Valves)","(1x) Grundfos UPS2 15-50/60 28mm Complete Pump (With Valves)"),
    ("(1x) Grundfos UPS2 25-80 Complete Pump","(1x) Grundfos UPS2 25-80 Complete Pump"),
    ("(1x) Honeywell 2 Port (22mm)","(1x) Honeywell 2 Port (22mm)"),
    ("(2x) Honeywell 2 Port (22mm)","(2x) Honeywell 2 Port (22mm)"),
    ("(1x) Honeywell 2 Port (28mm)","(1x) Honeywell 2 Port (28mm)"),
    ("(2x) Honeywell 2 Port (28mm)","(2x) Honeywell 2 Port (28mm)"),
    ("(1x) Honeywell 3 Port (22mm)","(1x) Honeywell 3 Port (22mm)"),
    ("(1x) Honeywell 3 Port (28mm)","(1x) Honeywell 3 Port (28mm)"),
    ("(1x) Cylinder Stat Wireless","(1x) Cylinder Stat Wireless"),
    ("(1x) Honeywell L641A Cylinder Thermostat","(1x) Honeywell L641A Cylinder Thermostat"),
    ("(1x) Honeywell CS92A Wireless Cylinder Thermostat","(1x) Honeywell CS92A Wireless Cylinder Thermostat"),
    ("(1x) Drayton 2 Port (22mm)","(1x) Drayton 2 Port (22mm)"),
    ("(2x) Drayton 2 Port (22mm)","(2x) Drayton 2 Port (22mm)"),
    ("(1x) Drayton 2 Port (28mm)","(1x) Drayton 2 Port (28mm)"),
    ("(2x) Drayton 2 Port (28mm)","(2x) Drayton 2 Port (28mm)"),
    ("(1x) Drayton 3 Port (22mm)","(1x) Drayton 3 Port (22mm)"),
    ("(1x) Drayton 3 Port (28mm)","(1x) Drayton 3 Port (28mm)"),
    ("(1) x Auto Bypass (15mm)","(1) x Auto Bypass (15mm)"),
    ("(1) x Auto Bypass (22mm)","(1) x Auto Bypass (22mm)"),
    ("(1x) x 11&quot; Immersion","(1x) x 11&quot Immersion"),
    ("(1x) x 14&quot; Immersion","(1x) x 14&quot Immersion"),
    ("(1x) x 27&quot; Immersion","(1x) x 27&quot Immersion"),
)

CONDENSATE_COMPONENTS_DROPDOWN = (	
    ("No Additional Condensate Components","No Additional Condensate Components"),
    ("(1x) Inline Condensate Neutraliser","(1x) Inline Condensate Neutraliser"),
    ("(1x) Grundfos Conlift 1 LS Pump","(1x) Grundfos Conlift 1 LS Pump"),
    ("(1x) Soakaway and Lime Stone Chippings","(1x) Soakaway and Lime Stone Chippings"),
    ("(1x) McAlpine Clamp 1GR","(1x) McAlpine Clamp 1GR"),
    ("(1x) McAlpine Mechanical Boss Connector 40mm","(1x) McAlpine Mechanical Boss Connector 40mm"),
    ("(1x) 110mm Strap Boss","(1x) 110mm Strap Boss"),
    ("(1x) HOTun","(1x) HOTun"),
    ("(1x) Length 32mm Waste pipe","(1x) Length 32mm Waste pipe"),
    ("(2x) Length 32mm Waste pipe","(2x) Length 32mm Waste pipe"),
    ("(3x) Length 32mm Waste pipe","(3x) Length 32mm Waste pipe"),
    ("(4x) Length 32mm Waste pipe","(4x) Length 32mm Waste pipe"),
    ("(3x) 32mm Waste Clips","(3x) 32mm Waste Clips"),
    ("(6x) 32mm Waste Clips","(6x) 32mm Waste Clips"),
    ("(9x) 32mm Waste Clips","(9x) 32mm Waste Clips"),
    ("(12x) 32mm Waste Clips","(12x) 32mm Waste Clips"),
    ("(2x) 32mm Waste Elbows","(2x) 32mm Waste Elbows"),
    ("(4x) 32mm Waste Elbows","(4x) 32mm Waste Elbows"),
    ("(6x) 32mm Waste Elbows","(6x) 32mm Waste Elbows"),
    ("(8x) 32mm Waste Elbows","(8x) 32mm Waste Elbows"),
    ("(1x) 32mm Waste Coupling","(1x) 32mm Waste Coupling"),
    ("(2x) 32mm Waste Coupling","(2x) 32mm Waste Coupling"),
    ("(3x) 32mm Waste Coupling","(3x) 32mm Waste Coupling"),
    ("(4x) 32mm Waste Coupling","(4x) 32mm Waste Coupling"),
)

ADDITIONAL_COPPER_REQUIRED_DROPDOWN = (
	("No Additional Copper Required","No Additional Copper Required"),
    ("(1x) Length 15mm Copper Tube","(1x) Length 15mm Copper Tube"),
    ("(2x) Length 15mm Copper Tube","(2x) Length 15mm Copper Tube"),
    ("(3x) Length 15mm Copper Tube","(3x) Length 15mm Copper Tube"),
    ("(4x) Length 15mm Copper Tube","(4x) Length 15mm Copper Tube"),
    ("(5x) Length 15mm Copper Tube","(5x) Length 15mm Copper Tube"),
    ("(6x) Length 15mm Copper Tube","(6x) Length 15mm Copper Tube"),
    ("(7x) Length 15mm Copper Tube","(7x) Length 15mm Copper Tube"),
    ("(8x) Length 15mm Copper Tube","(8x) Length 15mm Copper Tube"),
    ("(9x) Length 15mm Copper Tube","(9x) Length 15mm Copper Tube"),
    ("(10x) Length 15mm Copper Tube","(10x) Length 15mm Copper Tube"),
    ("(1x) Length 22mm Copper Tube","(1x) Length 22mm Copper Tube"),
    ("(2x) Length 22mm Copper Tube","(2x) Length 22mm Copper Tube"),
    ("(3x) Length 22mm Copper Tube","(3x) Length 22mm Copper Tube"),
    ("(4x) Length 22mm Copper Tube","(4x) Length 22mm Copper Tube"),
    ("(5x) Length 22mm Copper Tube","(5x) Length 22mm Copper Tube"),
    ("(6x) Length 22mm Copper Tube","(6x) Length 22mm Copper Tube"),
    ("(7x) Length 22mm Copper Tube","(7x) Length 22mm Copper Tube"),
    ("(8x) Length 22mm Copper Tube","(8x) Length 22mm Copper Tube"),
    ("(9x) Length 22mm Copper Tube","(9x) Length 22mm Copper Tube"),
    ("(10x) Length 22mm Copper Tube","(10x) Length 22mm Copper Tube"),
    ("(1x) Length 28mm Copper Tube","(1x) Length 28mm Copper Tube"),
    ("(2x) Length 28mm Copper Tube","(2x) Length 28mm Copper Tube"),
    ("(3x) Length 28mm Copper Tube","(3x) Length 28mm Copper Tube"),
    ("(4x) Length 28mm Copper Tube","(4x) Length 28mm Copper Tube"),
    ("(5x) Length 28mm Copper Tube","(5x) Length 28mm Copper Tube"),
    ("(6x) Length 28mm Copper Tube","(6x) Length 28mm Copper Tube"),
    ("(7x) Length 28mm Copper Tube","(7x) Length 28mm Copper Tube"),
    ("(8x) Length 28mm Copper Tube","(8x) Length 28mm Copper Tube"),
    ("(9x) Length 28mm Copper Tube","(9x) Length 28mm Copper Tube"),
    ("(10x) Length 28mm Copper Tube","(10x) Length 28mm Copper Tube"),
    ("(1x) Small Roll 8mm Copper Tube","(1x) Small Roll 8mm Copper Tube"),
    ("(1x) Large Roll 8mm Copper Tube","(1x) Large Roll 8mm Copper Tube"),
    ("(1x) Small Roll 10mm Copper Tube","(1x) Small Roll 10mm Copper Tube"),
    ("(1x) Large Roll 10mm Copper Tube","(1x) Large Roll 10mm Copper Tube"),
)

FITTINGS_PACKS_DROPDOWN = (
	("No Pack Required","No Pack Required"),
    ("Pack 1 Conventional to Conventional (22mm)","Pack 1 Conventional to Conventional (22mm)"),
    ("Pack 1 Conventional to Conventional (28mm)","Pack 1 Conventional to Conventional (28mm)"),
    ("Pack 2 Combi to Combi","Pack 2 Combi to Combi"),
    ("Pack 3 Conventional to Combi","Pack 3 Conventional to Combi"),
    ("Pack 4 Cylinder Replace","Pack 4 Cylinder Replace"),
    ("Pack 5 Internal Condense","Pack 5 Internal Condense"),
    ("Pack 6W External Condense (White)","Pack 6W External Condense (White)"),
    ("Pack 6B External Condense (Black)","Pack 6B External Condense (Black)"),
    ("Pack 7 Fully Pumped Update (22mm)","Pack 7 Fully Pumped Update (22mm)"),
    ("Pack 8 Fully Pumped Update (28mm)","Pack 8 Fully Pumped Update (28mm)"),
    ("New Full System Pack","New Full System Pack"),
)

ELECTRICAL_PACK_DROPDOWN = (
	("Electrical Pack A","Electrical Pack A"),
	("Electrical Pack B","Electrical Pack B"),
	("Electrical Pack C","Electrical Pack C"),
	("Electrical Pack D","Electrical Pack D"),
)

EARTH_SPIKE_REQUIRED_DROPDOWN = (
	("Earth Spike Not Required","Earth Spike Not Required"),
	("Earth Spike Required","Earth Spike Required"),
)

FILLING_LINK_DROPDOWN = (
	("No Filling Link","No Filling Link"),
	("15mm External Filling Loop","15mm External Filling Loop"),
	("Worcester Filling Link","Worcester Filling Link"),
	("Worcester Keyless Filling Link","Worcester Keyless Filling Link"),
	("Worcester Intelligent Automatic Filling System (Lifestyle Series ONLY)","Worcester Intelligent Automatic Filling System (Lifestyle Series ONLY)"),
)

SPECIAL_LIFT_REQUIREMENTS_DROPDOWN = (
	('No', 'No'),	
	('Yes', 'Yes'),
)

DOUBLE_HANDED_LIFT_REQUIRED_DROPDOWN = (
	('No', 'No'),
	('Double Handed Lift Required', 'Double Handed Lift Required'),
)

RADIATOR_SPECIFICATION_CHOICES = (
	('No Radiators Required','No Radiators Required'),
	('Radiator(s) Required','Radiator(s) Required'),
	('Thermoststic Radiator Valves Only','Thermoststic Radiator Valves Only'),
	('Towel Rail(s) Required','Towel Rail(s) Required'),
	('Customer to Provide Radiators','Customer to Provide Radiators'),
)

''' Section for defining the multiple forms that will be used for the boiler quote (FormWizard library) '''

class FormStepOne(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.0.field_name e.g. form_data.0.customer_first_name
	def __init__(self, *args, **kwargs):
		super(FormStepOne, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	customer_first_name = forms.CharField(max_length=100)
	customer_last_name = forms.CharField(max_length=100)
	customer_home_phone = forms.CharField(max_length=100, required = False)
	customer_mobile_phone = forms.CharField(max_length=100, required = False)
	customer_email = forms.EmailField()
	owner_or_tenant = forms.ChoiceField(choices=OWNER_OR_TENANT_DROPDOWN)
	

class FormStepTwo(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.1.field_name e.g. form_data.1.installation_address
	def __init__(self, *args, **kwargs):
		super(FormStepTwo, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	house_name_or_number = forms.CharField(max_length=100)
	street_address = forms.CharField(max_length=100)
	city = forms.CharField(max_length=100)
	county = forms.CharField(max_length=100)
	postcode = forms.CharField(max_length=100)
	property_type = forms.ChoiceField(choices=PROPERTY_TYPE_DROPDOWN)

class FormStepThree(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.2.field_name e.g. form_data.2.current_fuel_type
	def __init__(self, *args, **kwargs):
		super(FormStepThree, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	current_fuel_type = forms.ChoiceField(choices=CURRENT_FUEL_TYPE_DROPDOWN)
	current_boiler_type = forms.ChoiceField(choices=CURRENT_BOILER_TYPE_DROPDOWN)
	current_boiler_location = forms.ChoiceField(choices=CURRENT_BOILER_LOCATION_DROPDOWN)
	current_flue_system = forms.ChoiceField(choices=CURRENT_FLUE_SYSTEM_DROPDOWN)
	current_flue_location = forms.ChoiceField(choices=CURRENT_FLUE_LOCATION_DROPDOWN)
	current_controls = forms.ChoiceField(choices=CURRENT_CONTROLS_DROPDOWN)
	
class FormStepFour(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.3.field_name e.g. form_data.3.removals
	removals = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
											 choices=REMOVALS_CHOICES)

class FormStepFive(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.4.field_name e.g. form_data.4.new_fuel_type
	def __init__(self, *args, **kwargs):
		super(FormStepFive, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	new_fuel_type = forms.ChoiceField(choices=NEW_FUEL_TYPE_DROPDOWN)
	new_boiler_type = forms.ChoiceField(choices=NEW_BOILER_TYPE_DROPDOWN)
	new_boiler_location = forms.ChoiceField(choices=NEW_BOILER_LOCATION_DROPDOWN)
	new_flue_system = forms.ChoiceField(choices=NEW_FLUE_SYSTEM_DROPDOWN)
	new_flue_location = forms.ChoiceField(choices=NEW_FLUE_LOCATION_DROPDOWN)
	new_flue_diameter = forms.ChoiceField(choices=NEW_FLUE_DIAMETER_DROPDOWN)
	plume_management_kit = forms.ChoiceField(choices=PLUME_MANAGEMENT_KIT_DROPDOWN)
	condensate_termination = forms.ChoiceField(choices=CONDENSATE_TERMINATION_DROPDOWN)
	new_controls = forms.ChoiceField(choices=NEW_CONTROLS_DROPDOWN)
	cws_flow_rate = forms.ChoiceField(choices=CWS_FLOW_RATE_DROPDOWN)
	new_flue_metres = forms.ChoiceField(choices=NEW_FLUE_METRES_DROPDOWN)
	
class FormStepSix(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.5.field_name e.g. form_data.5.new_fuel_type
	def __init__(self, *args, **kwargs):
		super(FormStepSix, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	system_treatment = forms.ChoiceField(choices=SYSTEM_TREATMENT_DROPDOWN)
	gas_supply = forms.ChoiceField(choices=GAS_SUPPLY_DROPDOWN)
	gas_supply_length = forms.ChoiceField(choices=GAS_SUPPLY_LENGTH_DROPDOWN)
	asbestos_containing_materials_identified = forms.ChoiceField(choices=ASBESTOS_CONTAINING_MATERIALS_IDENTIFIED_DROPDOWN)
	electrical_work_required = forms.ChoiceField(choices=ELECTRICAL_WORK_REQUIRED_DROPDOWN)

class FormStepSeven(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.6.field_name e.g. form_data.6.boiler_manufactureruel_type

	#boiler_manufacturer = forms.ChoiceField(choices=BOILER_MANUFACTURER_DROPDOWN)
	def __init__(self, *args, **kwargs):
		# Get the user to seed the filter on the boiler_manufacturer drop down.
		self.user = kwargs.pop('user')
		super(FormStepSeven, self).__init__(*args, **kwargs)
		self.fields['boiler_manufacturer'] = forms.ModelChoiceField(queryset=ProductPrice.objects.filter(user = self.user).order_by('brand').values_list('brand', flat=True).distinct(), to_field_name='brand',empty_label = 'Select Boiler Brand for quote')
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	manufacturer_guarantee = forms.ChoiceField(choices=MANUFACTURER_GUARANTEE_DROPDOWN)
	flue_components = forms.ChoiceField(choices=FLUE_COMPONENTS_DROPDOWN)
	programmer_thermostat = forms.ChoiceField(choices=PROGRAMMER_THERMOSTAT_DROPDOWN)
	central_heating_system_filter = forms.ChoiceField(choices=CENTRAL_HEATING_SYSTEM_FILTER_DROPDOWN)
	scale_reducer = forms.ChoiceField(choices=SCALE_REDUCER_DROPDOWN)
	
class FormStepEight(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.7.field_name e.g. form_data.7.radiator_requirements
	def __init__(self, *args, **kwargs):
		super(FormStepEight, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	radiator_requirements = forms.ChoiceField(choices=RADIATOR_REQUIREMENTS_DROPDOWN)
	thermostatic_radiator_valves_size = forms.CharField(max_length=100, required = False)
	thermostatic_radiator_valves_type = forms.CharField(max_length=100, required = False)
	thermostatic_radiator_valves_quantity = forms.CharField(max_length=100, required = False)
	
class FormStepNine(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.8.field_name e.g. form_data.8.estimated_duration
	def __init__(self, *args, **kwargs):
		# Get the user to seed the filter on the drop down.
		self.user = kwargs.pop('user')
		self.manuf = kwargs.pop('manufacturer')
		super(FormStepNine, self).__init__(*args, **kwargs)
		self.fields['product_choice'] = forms.ModelChoiceField(queryset=ProductPrice.objects.filter(user = self.user, brand = self.manuf), empty_label = 'Select Product for quote')
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'	
	estimated_duration = forms.ChoiceField(choices=ESTIMATED_DURATION_DROPDOWN)
	description_of_works = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'rows':5, 'cols':30}))

''' User Registration Form '''		
class UserRegistrationForm(forms.Form):
	username = forms.CharField(
			required = True,
			label = 'Username',
			max_length = 32
		)
	email = forms.EmailField(
			required = True,
			label = 'Email',
			max_length = 64,
		)
	password = forms.CharField(
			required = True,
			label = 'Password',
			max_length = 32,
			widget = forms.PasswordInput()
		)


''' File upload capability form '''
class DocumentForm(forms.ModelForm):
	class Meta:
		model = Document
		fields = ('document', 'description')

		widgets = {
			'document': forms.FileInput(attrs={'class': 'form-control'}),
			'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a description for the Image'}),
		}

		
		
''' User's extended details form - has a 1:1 relationship with the django user object '''
class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('first_name','last_name','email','company_name','telephone', 'daily_work_rate', 'quote_prefix', 'current_quote_number')

		widgets = {
			'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your First Name', 'autofocus': ''}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Last Name'}),
			'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
			'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Company Name'}),
			'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Telephone Number'}),
			'daily_work_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your daily work rate'}),
			'quote_prefix': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a three character prefix for your quote numbers'}),
			'current_quote_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Current Quote Number'}),
		}

''' Form extension used during the registration process to capture the company name '''		
class UserProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('company_name',)

''' Form for capturing the product and price information for the quote '''
class ProductPriceForm(forms.ModelForm):
	
	class Meta:
		model = ProductPrice
		fields = ['brand', 'model_name', 'product_code','price','product_image','guarantee']

		widgets = {
			'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter the Manufacturer's Brand Name",  'autofocus': ''}),
			'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Model Name'}),
			'product_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Product Code'}),
			'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Price of the product'}),
			'product_image': forms.Select(attrs={'class': 'form-control'}),
			'guarantee': forms.Select(attrs={'class': 'form-control'}),
		}


	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(ProductPriceForm, self).__init__(*args, **kwargs)
		self.fields['product_image'].queryset=Document.objects.filter(user = self.user)

''' Form for capturing the product components for the quote '''
class ProductComponentForm(forms.ModelForm):
	
	class Meta:
		model = ProductComponent
		fields = ['brand', 'component_type', 'component_name']

		widgets = {
			'brand': forms.Select(attrs={'class': 'form-control',  'autofocus': ''}),
			'component_type': forms.Select(attrs={'class': 'form-control'}),
			'component_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Component Name'}),
		}

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(ProductComponentForm, self).__init__(*args, **kwargs)
	#	self.fields['product_image'].queryset=Document.objects.filter(user = self.user)		


''' Form for creating the capability for users to edit their own pdf layout for quote (not implemented in this release) '''
class EditQuoteTemplateForm(forms.Form):

	pdf_template_code = forms.CharField(widget=forms.Textarea(attrs={'rows':24, 'cols':100}))

	def __init__(self, user, *args, **kwargs):
		#self.user = kwargs.pop('user')
		self.user = user
		super(EditQuoteTemplateForm, self).__init__(*args, **kwargs)
		usr_pdf_template_file = Path(settings.BASE_DIR + "/templates/pdf/user_{}/quote_for_pdf.html".format(self.user.username))
		#usr_pdf_template_file = Path(settings.BASE_DIR + "/templates/pdf/user_test/quote_for_pdf.html")
		#print(usr_pdf_template_file)
		template_file = open(usr_pdf_template_file,'r')
		self.fields['pdf_template_code'].initial = template_file.read
		alert = None



''' Section for defining the multiple forms that will be used for the boiler quote (FormWizard library) '''

#class XWestChemFormStepOne(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.0.field_name e.g. form_data.0.customer_first_name
	#def __init__(self, *args, **kwargs):
		#super(WestChemFormStepOne, self).__init__(*args, **kwargs)
		#for field in self: 
			#field.field.widget.attrs['class'] = 'form-control'
	#customer_first_name = forms.CharField(max_length=100)
	#customer_last_name = forms.CharField(max_length=100)
	#customer_home_phone = forms.CharField(max_length=100, required = False)
	#customer_mobile_phone = forms.CharField(max_length=100, required = False)
	#customer_email = forms.EmailField()
	#owner_or_tenant = forms.ChoiceField(choices=OWNER_OR_TENANT_DROPDOWN)
	#choice = forms.ModelChoiceField(queryset=ProductPrice.objects.filter(user = self.user, brand = 'Worcester Bosch'), empty_label = 'Select Product for quote')
	

#class XWestChemFormStepTwo(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.1.field_name e.g. form_data.1.installation_address
	#def __init__(self, *args, **kwargs):
		#self.user = kwargs.pop('user')
		#super(WestChemFormStepTwo, self).__init__(*args, **kwargs)
		# Get the user to seed the filter on the drop down.
		#self.manuf = kwargs.pop('manufacturer')
		#self.fields['product_choice'] = forms.ModelMultipleChoiceField(queryset=ProductPrice.objects.filter(user = self.user))
		#self.fields['product_choice'] = ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=ProductPrice.objects.filter(user = self.user).values_list('id', flat=True))
		#removals = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
		#									 choices=REMOVALS_CHOICES)
		#self.fields['product_choice'] = forms.ModelChoiceField(queryset=ProductPrice.objects.all(), empty_label = 'Select Product for quote')
		#for field in self: 
			#field.field.widget.attrs['class'] = 'form-control'
	#house_name_or_number = forms.CharField(max_length=100)
	#street_address = forms.CharField(max_length=100)
	#city = forms.CharField(max_length=100)
	#county = forms.CharField(max_length=100)
	#postcode = forms.CharField(max_length=100)
	#property_type = forms.ChoiceField(choices=PROPERTY_TYPE_DROPDOWN)

# class CustomerProductForm(forms.Form):
# 	def __init__(self, *args, **kwargs):
# 		super(CustomerProductForm, self).__init__(*args, **kwargs)
# 		for field in self: 
# 			field.field.widget.attrs['class'] = 'form-control'
# 	customer = forms.CharField(max_length=100)
# 	contact = forms.CharField(max_length=100)
# 	customer_email = forms.EmailField()
# 	customer_phone= forms.CharField(max_length=100, required=False)
# 	machine = forms.CharField(max_length=100)
# 	make = forms.CharField(max_length=100)
# 	model = forms.CharField(max_length=100)
	

# class KitchenChecksForm(forms.Form):
# 	def __init__(self, *args, **kwargs):
# 		super(KitchenChecksForm, self).__init__(*args, **kwargs)
# 		for field in self: 
# 			field.field.widget.attrs['class'] = 'format_chkbox'
# 	results = forms.BooleanField(required=False)
# 	wash_temp_55C = forms.BooleanField(required=False)
# 	rinse_temp_82C = forms.BooleanField(required=False)
# 	is_a_descale_required = forms.BooleanField( required=False)
# 	rinse_jets_blocked = forms.BooleanField( required=False)
# 	rinse_jets_missing = forms.BooleanField(required=False)
# 	wash_jets_clean = forms.BooleanField( required=False)
# 	other_fault = forms.BooleanField(required=False)
# 	wall_racks = forms.BooleanField(required=False)
# 	auto_dosing_clean = forms.BooleanField(required=False)
# 	auto_dosing_pump_head = forms.BooleanField(required=False)
# 	auto_dosing_tube_stiffeners = forms.BooleanField(required=False)
# 	control_systems_clean = forms.BooleanField(required=False)
# 	control_system_damaged = forms.BooleanField(required=False)
# 	wall_charts = forms.BooleanField(required=False)

# class LaundryChecksForm(forms.Form):
# 	def __init__(self, *args, **kwargs):
# 		super(LaundryChecksForm, self).__init__(*args, **kwargs)
# 		for field in self: 
# 			field.field.widget.attrs['class'] = 'format_chkbox'
# 	results = forms.BooleanField(required=False)
# 	other_faults = forms.BooleanField(required=False)
# 	clean = forms.BooleanField(required=False)
# 	pump_heads = forms.BooleanField(required=False)
# 	tube_stiffener = forms.BooleanField(required=False)
# 	touch_pad_attached = forms.BooleanField(required=False)
# 	wall_charts = forms.BooleanField(required=False)

# class WaterSoftenerChecksForm(forms.Form):
# 	def __init__(self, *args, **kwargs):
# 		super(WaterSoftenerChecksForm, self).__init__(*args, **kwargs)
# 		for field in self: 
# 			field.field.widget.attrs['class'] = 'format_chkbox'
# 	is_water_hard = forms.BooleanField(required=False)
# 	is_water_softener_working = forms.BooleanField(required=False)

# class ProductsUsedForForm(forms.Form):
# 	def __init__(self, *args, **kwargs):
# 		super(ProductsUsedForForm, self).__init__(*args, **kwargs)
# 		for field in self: 
# 			field.field.widget.attrs['class'] = 'format_chkbox'
# 	pot_washing = forms.BooleanField(required=False)
# 	glass_washing = forms.BooleanField(required=False)
# 	food_prep_areas = forms.BooleanField(required=False)
# 	floors_and_surfaces = forms.BooleanField(required=False)
# 	ovens = forms.BooleanField(required=False)
# 	hand_soap = forms.BooleanField(required=False)
# 	hand_sanitiser = forms.BooleanField(required=False)
# 	drains = forms.BooleanField(required=False)
# 	laundry = forms.BooleanField(required=False)
# 	housekeeping = forms.BooleanField(required=False)

# class CommentsForm(forms.Form):
# 	def __init__(self, *args, **kwargs):
# 		super(CommentsForm, self).__init__(*args, **kwargs)
# 		for field in self: 
# 			field.field.widget.attrs['class'] = 'form-control'
# 	comments = forms.CharField(max_length=3000, required=False, widget=forms.Textarea(attrs={'rows':15, 'cols':30}))

# class ProductOrderForm(forms.Form):
# 	def __init__(self, *args, **kwargs):
# 		super(ProductOrderForm, self).__init__(*args, **kwargs)
# 		for field in self: 
# 			field.field.widget.attrs['class'] = 'form-control-products'
# 	hydroclean5L_s = forms.IntegerField(required=False, min_value=0, max_value=999)
# 	hydroclean5L_o = forms.IntegerField(required=False, min_value=0, max_value=999)
# 	hydroclean10L_s = forms.IntegerField(required=False, min_value=0, max_value=999)
# 	hydroclean10L_o = forms.IntegerField(required=False, min_value=0, max_value=999)
# 	soilmaster5L_s = forms.IntegerField(required=False, min_value=0, max_value=999)
# 	soilmaster5L_o = forms.IntegerField(required=False, min_value=0, max_value=999)
# 	soilmaster10L_s = forms.IntegerField(required=False, min_value=0, max_value=999)
# 	soilmaster10L_o = forms.IntegerField(required=False, min_value=0, max_value=999)


	# quadrant_s = forms.IntegerField(required=False, min_value=0, max_value=999)
	# quadrant_o = forms.IntegerField(required=False, min_value=0, max_value=999)
	# ace87_s = forms.IntegerField(required=False, min_value=0, max_value=999)
	# ace87_o = forms.IntegerField(required=False, min_value=0, max_value=999)
	# dp100_s = forms.IntegerField(required=False, min_value=0, max_value=999)
	# dp100_o = forms.IntegerField(required=False, min_value=0, max_value=999)

	# bravo_s = forms.IntegerField(required=False, min_value=0, max_value=999)
	# bravo_o = forms.IntegerField(required=False, min_value=0, max_value=999)
	# fabricare_s = forms.IntegerField(required=False, min_value=0, max_value=999)
	# fabricare_o = forms.IntegerField(required=False, min_value=0, max_value=999)
	# encore5L_s = forms.IntegerField(required=False, min_value=0, max_value=999)
	# encore5L_o = forms.IntegerField(required=False, min_value=0, max_value=999)

# class ProductForm(forms.Form):
# 	product_id = forms.IntegerField(widget=forms.HiddenInput)
# 	model_name = forms.CharField(label=False, required=False,
# 	 widget=forms.TextInput(attrs={'readonly':'readonly','class': "input-disabled"})
# 	 )
# 	size = forms.CharField(label=False, required=False,
# 	 widget=forms.TextInput(attrs={'readonly':'readonly','class': "input-price"})
# 	 )
# 	price = forms.DecimalField(label=False, required=False,
# 	 widget=forms.TextInput(attrs={'readonly':'readonly','class': "input-price"})
# 	 )
# 	stock = forms.IntegerField(label=False, widget=forms.TextInput(attrs={'class': "input-int"}))
# 	quantity = forms.IntegerField(label=False, widget=forms.TextInput(attrs={'class': "input-int"}))

''' ----------- Form pages for yourheat -------------'''
class FormStepOne_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.0.field_name e.g. form_data.0.customer_first_name
	def __init__(self, *args, **kwargs):
		super(FormStepOne_yh, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	customer_title = forms.ChoiceField(choices=CUSTOMER_TITLE_DROPDOWN)
	customer_first_name = forms.CharField(max_length=100)
	customer_last_name = forms.CharField(max_length=100)
	customer_home_phone = forms.CharField(max_length=100, required = False)
	customer_mobile_phone = forms.CharField(max_length=100, required = False)
	customer_email = forms.EmailField()
	owner_tenant_or_landlord = forms.ChoiceField(choices=OWNER_TENANT_OR_LANDLORD_DROPDOWN)
	

# class FormStepTwo_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.1.field_name e.g. form_data.1.installation_address
	# def __init__(self, *args, **kwargs):
	# 	super(FormStepTwo_yh, self).__init__(*args, **kwargs)
	# 	for field in self: 
	# 		field.field.widget.attrs['class'] = 'form-control'
	# house_name_or_number = forms.CharField(max_length=100)
	# street_address = forms.CharField(max_length=100)
	# city = forms.CharField(max_length=100)
	# county = forms.CharField(max_length=100)
	# postcode = forms.CharField(max_length=100)
	# property_type = forms.ChoiceField(choices=PROPERTY_TYPE_DROPDOWN)

class FormStepTwo_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.1.field_name e.g. form_data.1.installation_address
	def __init__(self, *args, **kwargs):
		super(FormStepTwo_yh, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	installation_address = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'rows':5, 'cols':30}))
	billing_address = forms.CharField(max_length=2000, required = False,  widget=forms.Textarea(attrs={'rows':5, 'cols':30, 'placeholder': 'Leave blank for Billing address same as Installation address'},))
	property_type = forms.ChoiceField(choices=PROPERTY_TYPE_DROPDOWN)	

class FormStepThree_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.2.field_name e.g. form_data.2.current_fuel_type
	def __init__(self, *args, **kwargs):
		super(FormStepThree_yh, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	current_fuel_type = forms.ChoiceField(choices=CURRENT_FUEL_TYPE_DROPDOWN)
	current_boiler_type = forms.ChoiceField(choices=CURRENT_BOILER_TYPE_DROPDOWN)
	current_boiler_location = forms.ChoiceField(choices=CURRENT_BOILER_LOCATION_DROPDOWN)
	current_flue_system = forms.ChoiceField(choices=CURRENT_FLUE_SYSTEM_DROPDOWN)
	current_flue_location = forms.ChoiceField(choices=CURRENT_FLUE_LOCATION_DROPDOWN)
	current_controls = forms.MultipleChoiceField(choices=CURRENT_CONTROLS_DROPDOWN)
	current_radiators_working_correctly = forms.ChoiceField(choices=CURRENT_RADIATORS_WORKING_CORRECTLY_DROPDOWN)
	
class FormStepFour_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.3.field_name e.g. form_data.3.removals
	removals = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
											 choices=REMOVALS_CHOICES)

class FormStepFive_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.4.field_name e.g. form_data.4.new_fuel_type
	def __init__(self, *args, **kwargs):
		# Get the user to seed the filter on the boiler_manufacturer drop down.
		self.user = kwargs.pop('user')
		super(FormStepFive_yh, self).__init__(*args, **kwargs)
		self.fields['boiler_manufacturer'] = forms.ModelChoiceField(queryset=ProductPrice.objects.filter(user = self.user).order_by('brand').values_list('brand', flat=True).distinct(), to_field_name='brand',empty_label = 'Select Boiler Brand for quote')
		self.fields['alt_boiler_manufacturer'] = forms.ModelChoiceField(queryset=ProductPrice.objects.filter(user = self.user).order_by('brand').values_list('brand', flat=True).distinct(), to_field_name='brand',empty_label = 'Select Alternative Boiler Brand for quote')
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	new_fuel_type = forms.ChoiceField(choices=NEW_FUEL_TYPE_DROPDOWN)
	new_boiler_type = forms.ChoiceField(choices=NEW_BOILER_TYPE_DROPDOWN)
	new_boiler_location = forms.ChoiceField(choices=NEW_BOILER_LOCATION_DROPDOWN)
	new_flue_system = forms.ChoiceField(choices=NEW_FLUE_SYSTEM_DROPDOWN)
	new_flue_location = forms.ChoiceField(choices=NEW_FLUE_LOCATION_DROPDOWN)
	new_flue_diameter = forms.ChoiceField(choices=NEW_FLUE_DIAMETER_DROPDOWN)
	plume_management_kit = forms.ChoiceField(choices=PLUME_MANAGEMENT_KIT_DROPDOWN)
	condensate_termination = forms.ChoiceField(choices=CONDENSATE_TERMINATION_DROPDOWN)
	new_controls = forms.MultipleChoiceField(choices=NEW_CONTROLS_DROPDOWN)
	# cws_flow_rate = forms.ChoiceField(choices=CWS_FLOW_RATE_DROPDOWN)
	incoming_flow_rate = forms.ChoiceField(choices=INCOMING_FLOW_RATE_DROPDOWN)
	will_boiler_be_housed_in_cupboard = forms.ChoiceField(choices=WILL_BOILER_BE_HOUSED_IN_CUPBOARD_DROPDOWN)
	#new_flue_metres = forms.ChoiceField(choices=NEW_FLUE_METRES_DROPDOWN)
	cupboard_height = forms.IntegerField(required=False)
	cupboard_width = forms.IntegerField(required=False)
	cupboard_depth = forms.IntegerField(required=False)
	
class FormStepSix_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.5.field_name e.g. form_data.5.new_fuel_type
	def __init__(self, *args, **kwargs):
		# Get the user to seed the filter on the drop down.
		self.user = kwargs.pop('user')
		self.manuf = kwargs.pop('manufacturer')
		self.alt_manuf = kwargs.pop('alt_manufacturer')
		super(FormStepSix_yh, self).__init__(*args, **kwargs)
		self.fields['product_choice'] = forms.ModelChoiceField(queryset=ProductPrice.objects.filter(user = self.user, brand = self.manuf), empty_label = 'Select Product for quote')
		self.fields['alt_product_choice'] = forms.ModelChoiceField(queryset=ProductPrice.objects.filter(user = self.user, brand = self.alt_manuf), empty_label = 'Select Alternative Product for quote')
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	chemical_system_treatment = forms.ChoiceField(choices=CHEMICAL_SYSTEM_TREATMENT_DROPDOWN)
	gas_supply_requirements = forms.ChoiceField(choices=GAS_SUPPLY_DROPDOWN)
	gas_supply_length = forms.ChoiceField(choices=GAS_SUPPLY_LENGTH_DROPDOWN)
	scaffolding_required = forms.ChoiceField(choices=SCAFFOLDING_REQUIRED_DROPDOWN)
	asbestos_containing_materials_identified = forms.ChoiceField(choices=ASBESTOS_CONTAINING_MATERIALS_IDENTIFIED_DROPDOWN)
	asbestos_removal_procedure = forms.ChoiceField(choices=ASBESTOS_REMOVAL_PROCEDURE_DROPDOWN)
	electrical_work_required = forms.ChoiceField(choices=ELECTRICAL_WORK_REQUIRED_DROPDOWN)
	potential_contractor_attendance_required = forms.ChoiceField(choices=POTENTIAL_CONTRACTOR_ATTENDANCE_REQUIRED_DROPDOWN)
	details_on_potential_contractor_requirements = forms.CharField(max_length=2000, required = False, widget=forms.Textarea(attrs={'rows':3, 'cols':30, 'placeholder': 'if applicable, please be detailed'}))
	parking_requirements = forms.CharField(max_length=2000, required = False, widget=forms.Textarea(attrs={'rows':3, 'cols':30, 'placeholder': 'if applicable, please be detailed'}))

class FormStepSeven_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.6.field_name e.g. form_data.6.boiler_manufactureruel_type

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self.manuf = kwargs.pop('manufacturer')
		super(FormStepSeven_yh, self).__init__(*args, **kwargs)
		self.fields['gas_flue_components'] = forms.ModelMultipleChoiceField(queryset=ProductComponent.objects.filter(user = self.user, brand = self.manuf, component_type = 'Gas Flue Component').only('component_name'))
		self.fields['plume_components'] = forms.ModelMultipleChoiceField(queryset=ProductComponent.objects.filter(user = self.user, brand = self.manuf, component_type = 'Plume Component').only('component_name'))
		self.fields['programmer_thermostat'] = forms.MultipleChoiceField(choices=PROGRAMMER_THERMOSTAT_DROPDOWN)
		self.fields['additional_central_heating_components'] = forms.MultipleChoiceField(choices=ADDITIONAL_CENTRAL_HEATING_COMPONENTS_DROPDOWN)
		self.fields['central_heating_system_filter'] = forms.ChoiceField(choices=CENTRAL_HEATING_SYSTEM_FILTER_DROPDOWN)
		self.fields['scale_reducer'] = forms.ChoiceField(choices=SCALE_REDUCER_DROPDOWN)
		self.fields['condensate_components'] = forms.MultipleChoiceField(choices=CONDENSATE_COMPONENTS_DROPDOWN)
		self.fields['additional_copper_required'] = forms.MultipleChoiceField(choices=ADDITIONAL_COPPER_REQUIRED_DROPDOWN)
		self.fields['fittings_packs'] = forms.MultipleChoiceField(choices=FITTINGS_PACKS_DROPDOWN)
		self.fields['any_special_parts'] = forms.CharField(max_length=2000, required=False, widget=forms.Textarea(attrs={'rows':4, 'cols':30, 'placeholder': 'Input if necessary'}))
		self.fields['electrical_pack'] = forms.ChoiceField(choices=ELECTRICAL_PACK_DROPDOWN)
		self.fields['earth_spike_required'] = forms.ChoiceField(choices=EARTH_SPIKE_REQUIRED_DROPDOWN)
		self.fields['filling_link'] = forms.ChoiceField(choices=FILLING_LINK_DROPDOWN)
		self.fields['special_lift_requirements'] = forms.ChoiceField(choices=SPECIAL_LIFT_REQUIREMENTS_DROPDOWN)
		self.fields['double_handed_lift_required'] = forms.ChoiceField(choices=DOUBLE_HANDED_LIFT_REQUIRED_DROPDOWN)

		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	#manufacturer_guarantee = forms.ChoiceField(choices=MANUFACTURER_GUARANTEE_DROPDOWN)
	#flue_components = forms.ChoiceField(choices=FLUE_COMPONENTS_DROPDOWN)
	#programmer_thermostat = forms.ChoiceField(choices=PROGRAMMER_THERMOSTAT_DROPDOWN)
	#central_heating_system_filter = forms.ChoiceField(choices=CENTRAL_HEATING_SYSTEM_FILTER_DROPDOWN)
	#scale_reducer = forms.ChoiceField(choices=SCALE_REDUCER_DROPDOWN)
	
class FormStepEight_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.7.field_name e.g. form_data.7.radiator_requirements
	#def __init__(self, *args, **kwargs):
	#	super(FormStepEight_yh, self).__init__(*args, **kwargs)
	#	for field in self: 
	#		field.field.widget.attrs['class'] = 'form-control'
	radiator_specification = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
											 choices=RADIATOR_SPECIFICATION_CHOICES)		
	#radiator_requirements = forms.ChoiceField(choices=RADIATOR_REQUIREMENTS_DROPDOWN)
	#thermostatic_radiator_valves_size = forms.CharField(max_length=100, required = False)
	#thermostatic_radiator_valves_type = forms.CharField(max_length=100, required = False)
	#thermostatic_radiator_valves_quantity = forms.CharField(max_length=100, required = False)
	#programmer_thermostat = forms.MultipleChoiceField(choices=PROGRAMMER_THERMOSTAT_DROPDOWN)
	
class FormStepNine_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.8.field_name e.g. form_data.8.estimated_duration
	def __init__(self, *args, **kwargs):
		# Get the user to seed the filter on the drop down.
		#self.user = kwargs.pop('user')
		#self.manuf = kwargs.pop('manufacturer')
		#self.alt_manuf = kwargs.pop('alt_manufacturer')
		super(FormStepNine_yh, self).__init__(*args, **kwargs)
		#self.fields['product_choice'] = forms.ModelChoiceField(queryset=ProductPrice.objects.filter(user = self.user, brand = self.manuf), empty_label = 'Select Product for quote')
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
		#self.fields['alt_product_choice'] = forms.ModelChoiceField(queryset=ProductPrice.objects.filter(user = self.user, brand = self.alt_manuf), empty_label = 'Select Alternative Product for quote')
		# for field in self: 
		# 	field.field.widget.attrs['class'] = 'form-control'	
	estimated_duration = forms.ChoiceField(choices=ESTIMATED_DURATION_DROPDOWN)
	description_of_works = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'rows':5, 'cols':30}))

class FinanceForm_yh(forms.Form):
	total_cost = forms.FloatField()
	deposit_amount = forms.FloatField()
	ib60_loan_amount = forms.CharField(max_length=30)
	ib60_monthly_payment = forms.CharField(max_length=30)
	ib60_total_payable = forms.CharField(max_length=30)
	ib120_loan_amount = forms.CharField(max_length=30)
	ib120_monthly_payment = forms.CharField(max_length=30)
	ib120_total_payable = forms.CharField(max_length=30)

	interest_free_12m_monthly_payment = forms.CharField(max_length=30)
	interest_free_12m_loan_amount = forms.CharField(max_length=30)

	def __init__(self, *args, **kwargs):
		self.product_price = kwargs.pop('product_price')
		super(FinanceForm_yh, self).__init__(*args, **kwargs)
		self.fields['total_cost'].disabled = True
		self.fields['total_cost'].initial = self.product_price
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'

	


	
	

