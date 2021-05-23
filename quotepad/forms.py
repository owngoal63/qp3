from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from quotepad.models import Document, Profile, ProductPrice, ProductComponent, OptionalExtra
from django.forms import ModelMultipleChoiceField, ModelChoiceField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
import datetime

# For Editing the template
from django.conf import settings
from pathlib import Path

# To allow OR conditions on object filters
from django.db.models import Q

# Import YH personel data ( in the views folder ) required for forms
from .views.yh_personnel import SURVEYOR_DROPDOWN, ENGINEER_DROPDOWN, ENGINEER_POSTCODE_DROPDOWN

''' Section to define the boiler quote form field dropdown values and choices '''
OWNER_OR_TENANT_DROPDOWN = (
	('Owner','Owner'),
	('Tenant','Tenant'),
)

PROPERTY_TYPE_DROPDOWN = (
	('','Select One'),
	('Detached','Detached'),
	('Semi Detached','Semi Detached'),
	('Terraced','Terraced'),
	('End of Terrace','End of Terrace'),
	('Bungalow','Bungalow'),
	('Flat','Flat'),
)

ALTERNATIVE_BILLING_ADDRESS_DROPDOWN = (
	('No','No'),
	('Yes','Yes'),
)

CURRENT_FUEL_TYPE_DROPDOWN = (
	('','Select One'),
	('Gas','Gas'),
	('LPG','LPG'),
	('Oil','Oil'),
	('Electric','Electric'),
	('N/A','N/A'),
)

CURRENT_BOILER_TYPE_DROPDOWN = (
	('','Select One'),
	('Combi','Combi'),
	('Conventional Wall Hung','Conventional Wall Hung'),
	('Conventional Floor Standing','Conventional Floor Standing'),
	('System','System'),
	('Back Boiler','Back Boiler'),
	('Water Heater','Water Heater'),
	('No Existing System','No Existing System'),
	('N/A','N/A'),
)

CURRENT_BOILER_LOCATION_DROPDOWN = (
	('','Select One'),
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
	('N/A','N/A'),
)

CURRENT_FLUE_SYSTEM_DROPDOWN = (
	('','Select One'),
	('Horizontal Flue','Horizontal Flue'),
	('Vertical Flue','Vertical Flue'),
	('Rear Flue','Rear Flue'),
	('No Existing Flue','No Existing Flue'),
	('N/A','N/A'),
)

CURRENT_FLUE_LOCATION_DROPDOWN = (
	('','Select One'),
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
	('Radiators','Radiators'),
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
	('','Select One'),
	('Gas','Gas'),
	('LPG','LPG'),
	('Oil','Oil'),
	('Electric','Electric'),
)

NEW_BOILER_TYPE_DROPDOWN = (
	('','Select One'),
	('Combi','Combi'),
	('Conventional','Conventional'),
	('System','System'),
)

NEW_BOILER_LOCATION_DROPDOWN = (
	('','Select One'),
	('Existing Location','Existing Location'),
	('Open to options','Open to options'),
	('Relocate in current room','Relocate in current room'),
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
	('','Select One'),
	('Horizontal','Horizontal'),
	('Vertical','Vertical'),
	('Rear Flue','Rear Flue'),
)

NEW_FLUE_LOCATION_DROPDOWN = (
	('','Select One'),
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
	('','Select One'),
	('100mm','100mm'),
	('125mm','125mm'),
)

PLUME_MANAGEMENT_KIT_DROPDOWN = (
	('','Select One'),
	('Required','Required'),
	('Not Required','Not Required'),
)

CONDENSATE_TERMINATION_DROPDOWN = (
	('','Select One'),
	('Drain','Drain'),
	('Sink','Sink'),
	('Soil Vent Pipe','Soil Vent Pipe'),
	('External Gully','External Gully'),
	('Pumped','Pumped'),
	('Soakaway Trap','Soakaway Trap'),
	('Internal Waste Point','Internal Waste Point'),
)
NEW_CONTROLS_DROPDOWN = (
	('','Select One'),
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
	('','Select One'),
	('Current Gas supply deemed satisfactory','Current Gas supply deemed satisfactory'),
	('Adaptation to existing gas supply required','Adaptation to existing gas supply required'),
	('New external gas supply required','New external gas supply required'),
	('New internal gas supply required','New internal gas supply required'),
)

FUEL_SUPPLY_DROPDOWN = (
	('','Select One'),
	('Current Supply deemed satisfactory','Current Supply deemed satisfactory'),
	('Adaptation to existing supply required','Adaptation to existing supply required'),
	('New external supply required','New external supply required'),
	('New internal supply required','New internal supply required'),
)

GAS_SUPPLY_LENGTH_DROPDOWN = (
	('','Select One'),
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
	('','Select One'),
	('No Asbestos Identified','No Asbestos Identified'),
	('Potential Asbestos Containing Material Identified','Potential Asbestos Containing Material Identified'),
)

ASBESTOS_REMOVAL_PROCEDURE_DROPDOWN = (
	('','Select One'),
	('N/A','N/A'),
	('Your Heat to remove during installation','Your Heat to remove during installation'),
	('Client to arrange removal prior to installation','Client to arrange removal prior to installation'),
	('No disruption necessary','No disruption necessary'),
)

POTENTIAL_CONTRACTOR_ATTENDANCE_REQUIRED_DROPDOWN = (
	('','Select One'),
	('No','No'),
	('Yes','Yes'),
)

ELECTRICAL_WORK_REQUIRED_DROPDOWN = (
	('','Select One'),
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
	('','Select One'),
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
	('','Select One'),
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
	('1','1 day'),
	('2','2 days'),
	('3','3 days'),
	('4','4 days'),
	('5','5 days'),
	('6','6 days'),
	('7','7 days'),
	('8','8 days'),
	('9','9 days'),
	('10','10 days'),
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
	('','Select One'),
	('Owner','Owner'),
	('Tenant','Tenant'),
	('Landlord','Landlord'),
)

CURRENT_RADIATORS_WORKING_CORRECTLY_DROPDOWN = (
	('','Select One'),
	('Yes', 'Yes'),
	('No', 'No'),
	('Boiler Non-Operational', 'Boiler Non-Operational'),
)

INCOMING_FLOW_RATE_DROPDOWN = (
	('','Select One'),
	('N/A','N/A'),
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
	('Visually weak (remote quote)','Visually weak (remote quote)'),
	('Visually average (remote quote)','Visually average (remote quote)'),
	('Visually strong (remote quote)','Visually strong (remote quote)'),
)

WILL_BOILER_BE_HOUSED_IN_CUPBOARD_DROPDOWN = (
	('','Select One'),
	('No', 'No'),	
	('Yes', 'Yes'),
)

CHEMICAL_SYSTEM_TREATMENT_DROPDOWN = (
	('','Select One'),
	('Chemical Flush & Inhibitor','Chemical Flush & Inhibitor'),
	('Chemical Powerflush & Inhibitor','Chemical Powerflush & Inhibitor'),
	('Magnacleanse added (up to 10 rads)','Magnacleanse added (up to 10 rads)'),
	('Magnacleanse added (up to 15 rads)','Magnacleanse added (up to 15 rads)'),
	('Magnacleanse added (up to 20 rads)','Magnacleanse added (up to 20 rads)'),
	('Magnacleanse added (more than 20 rads)','Magnacleanse added (more than 20 rads)'),
	
)

SCAFFOLDING_REQUIRED_DROPDOWN = (
	('','Select One'),
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
	('','Select One'),
	("Electrical Pack A","Electrical Pack A"),
	("Electrical Pack B","Electrical Pack B"),
	("Electrical Pack C","Electrical Pack C"),
	("Electrical Pack D","Electrical Pack D"),
)

EARTH_SPIKE_REQUIRED_DROPDOWN = (
	('','Select One'),
	("Earth Spike Not Required","Earth Spike Not Required"),
	("Earth Spike Required","Earth Spike Required"),
)

FILLING_LINK_DROPDOWN = (
	('','Select One'),
	("No Filling Link","No Filling Link"),
	("15mm External Filling Loop","15mm External Filling Loop"),
	("Worcester Filling Link","Worcester Filling Link"),
	("Worcester Keyless Filling Link","Worcester Keyless Filling Link"),
	("Worcester Intelligent Automatic Filling System (Lifestyle Series ONLY)","Worcester Intelligent Automatic Filling System (Lifestyle Series ONLY)"),
)

SPECIAL_LIFT_REQUIREMENTS_DROPDOWN = (
	('','Select One'),
	('No', 'No'),	
	('Yes', 'Yes'),
)

DOUBLE_HANDED_LIFT_REQUIRED_DROPDOWN = (
	('','Select One'),
	('No', 'No'),
	('Double Handed Lift Required', 'Double Handed Lift Required'),
)

RADIATOR_SPECIFICATION_CHOICES = (
	('No Radiators Required','No Radiators Required'),
	('Radiator(s) Required','Radiator(s) Required'),
	('Thermostatic Radiator Valves Only','Thermostatic Radiator Valves Only'),
	('Towel Rail(s) Required','Towel Rail(s) Required'),
	# ('Customer to Provide Radiators','Customer to Provide Radiators'),
)

RADIATOR_LOCATION_DROPDOWN = (
	('','-----------'),
	("Bedroom 1","Bedroom 1"),
	("Bedroom 2","Bedroom 2"),
	("Bedroom 3","Bedroom 3"),
	("Bedroom 4","Bedroom 4"),
	("Bedroom 5","Bedroom 5"),
	("Dining Room","Dining Room"),
	("Lounge","Lounge"),
	("Downstairs Hallway","Downstairs Hallway"),
	("Downstairs WC","Downstairs WC"),
	("Kitchen","Kitchen"),
	("Conservatory","Conservatory"),
	("Landing","Landing"),
	("Bathroom 1","Bathroom 1"),
	("Bathroom 2","Bathroom 2"),
	("Ensuite 1","Ensuite 1"),
	("Ensuite 2","Ensuite 2"),
	("Ensuite 3","Ensuite 3"),
	("Wardrobe","Wardrobe"),
	("Study","Study"),
	("Utility Room","Utility Room"),
	("Games Room","Games Room"),
)

RADIATOR_HEIGHT_DROPDOWN = (
	('','-----'),
	('300','300'),
	('350','350'),
	('400','400'),
	('450','450'),
	('500','500'),
	('550','550'),
	('600','600'),
	('650','650'),
	('700','700'),	
)

RADIATOR_WIDTH_DROPDOWN = (
	('','----'),
	("400","400"),
	("500","500"),
	("600","600"),
	("700","700"),
	("800","800"),
	("900","900"),
	("1000","1000"),
	("1100","1100"),
	("1200","1200"),
	("1400","1400"),
	("1600","1600"),
	("1800","1800"),
	("2000","2000"),
	("2600","2600"),
	("2800","2800"),
)

RADIATOR_TYPE_DROPDOWN = (
	('','---'),
	("P+","P+"),
	("K1","K1"),
	("K2","K2"),
)

RADIATOR_VALVES_DROPDOWN = (
	('','-----'),
	("8mm","8mm"),
	("10mm","10mm"),
	("15mm","15mm"),
	("22mm","22mm"),
)

RADIATOR_VALVE_TYPE_DROPDOWN = (
	('','-----------'),
	("Straight TRV","Straight TRV"),
	("Angled TRV","Angled TRV"),
	("Straight TRV / Lockshield","Straight TRV / Lockshield"),
	("Angled TRV / Lockshield","Angled TRV / Lockshield"),
	("Straight Lockshield Only","Straight Lockshield Only"),
	("Angled Lockshield Only","Angled Lockshield Only"),
)

RADIATOR_VALVE_QTY_DROPDOWN = (
	('','----'),
	("1","1"),("2","2"),("3","3"),("4","4"),
	("5","5"),("6","6"),("7","7"),("8","8"),
	("9","9"),("10","10"),("11","11"),("12","12"),
	("13","13"),("14","14"),("15","15"),("16","16"),
	("17","17"),("18","18"),("19","19"),("20","20"),
	("21","21"),("22","22"),("23","23"),("24","24"),
	("25","25"),("26","26"),("27","27"),("28","28"),
	("29","29"),("30","30"),("31","31"),("32","32"),
	("33","33"),("34","34"),("35","35"),("36","36"),
	("37","37"),("38","38"),("39","39"),("40","40"),

)

TOWEL_RAIL_LOCATION_DROPDOWN = (
	('','-----------'),
	("Upstairs Bathroom","Upstairs Bathroom"),	
	("Downstairs Bathroom","Downstairs Bathroom"),	
)

# TOWEL_RAIL_HEIGHT = (
# 	('','-----'),
# 	("400","400"),
# 	("500","500"),
# 	("600","600"),
# 	("700","700"),
# 	("800","800"),
# 	("900","900"),
# 	("1000","1000"),
# 	("1100","1100"),
# 	("1200","1200"),
# 	("1300","1300"),
# 	("1400","1400"),
# 	("1500","1500"),
# 	("1600","1600"),
# 	("1700","1700"),
# 	("1800","1800"),
# 	("1900","1900"),
# 	("2000","2000"),

# )

# TOWEL_RAIL_WIDTH = (
# 	('','----'),
# 	("300","300"),
# 	("350","350"),
# 	("400","400"),
# 	("450","450"),
# 	("500","500"),
# 	("550","550"),
# 	("600","600"),
# 	("650","650"),
# 	("700","700"),
# )


TOWEL_RAIL_HEIGHT = (
	('','-----'),
	("900","900"),
	("1000","1000"),
	("1200","1200"),
	("1600","1600"),
	("1800","1800"),
)

TOWEL_RAIL_WIDTH = (
	('','----'),
	("450","450"),
	("600","600"),
)

TOWEL_RAIL_COLOUR = (
	('','-----'),
	("Chrome","Chrome"),
	("White","White"),
)

TOWEL_RAIL_TYPE = (
	('','-----'),
	("Straight","Straight"),
	("Curved","Curved"),
)

OPTIONAL_EXTRAS_QTY_DROPDOWN = (
	('','--'),
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
)

LOCATIONS_WHERE_RADIATORS_NOT_WORKING_CORRECTLY_DROPDOWN = (
	("Bedroom 1","Bedroom 1"),
	("Bedroom 2","Bedroom 2"),
	("Bedroom 3","Bedroom 3"),
	("Bedroom 4","Bedroom 4"),
	("Bedroom 5","Bedroom 5"),
	("Dining Room","Dining Room"),
	("Lounge","Lounge"),
	("Downstairs Hallway","Downstairs Hallway"),
	("Downstairs WC","Downstairs WC"),
	("Kitchen","Kitchen"),
	("Conservatory","Conservatory"),
	("Landing","Landing"),
	("Bathroom 1","Bathroom 1"),
	("Bathroom 2","Bathroom 2"),
	("Ensuite 1","Ensuite 1"),
	("Ensuite 2","Ensuite 2"),
	("Ensuite 3","Ensuite 3"),
	("Wardrobe","Wardrobe"),
	("Study","Study"),
	("Utility Room","Utility Room"),
	("Games Room","Games Room"),
)

BUILDING_PACK_REQUIRED_DROPDOWN = (
	("Same flue hole","Same flue hole"),
	("Minor building","Minor building"),
	("Engineer to collect bricks","Engineer to collect bricks"),
	("Customer to collect bricks","Customer to collect bricks"),
	("Boiler board required","Boiler board required"),
	("Block and render","Block and render"),
	("Custom building","Custom building"),
	("Red/Yellow brick standard","Red/Yellow brick standard"),
)

HEAT_LOSS_HOUSE_TYPE_DROPDOWN = (
	(0.04,"1985 onwards"),
	(0.05,"1950 - 1984"),
	(0.04,"Pre 1950"),
)

# Dropdowns for Survey Apointment Form

LEAD_BOOKER_DROPDOWN = (
	('','Select One'),
	('Sarah Dance', 'Sarah Dance'),	
	('Tom Hewitt', 'Tom Hewitt'),	
	('Tom Driscoll', 'Tom Driscoll'),	
	('Grace Barrett', 'Grace Barrett'),	
	('Anna Bishop-Apsey', 'Anna Bishop-Apsey'),	
	('Jeremy Tomkinson', 'Jeremy Tomkinson'),	
)

CUSTOMER_CONFIRMED_DROPDOWN = (
	('','Select One'),
	('Yes by phone', 'Yes by phone'),
	('Yes by email', 'Yes by email'),
	('Yes by text', 'Yes by text'),
	('Unable to contact', 'Unable to contact'),	
)

SURVEY_ATTENDEE_DROPDOWN = (
	('','Select One'),
	('Home Owner', 'Home Owner'),
	('Tenant', 'Tenant'),
	('Other', 'Other'),	
)

BRAND_PREFERENCE_DROPDOWN = (
	('','Select One'),
	('Open to options','Open to options'),
	('Worcester Bosch','Worcester Bosch'),
	('Worcester Bosch 2000','Worcester Bosch 2000'),
	('Worcester Bosch Lifestyle','Worcester Bosch Lifestyle'),
	('Vaillant','Vaillant'),
	('Ideal','Ideal'),
	('Glow Worm','Glow Worm'),
	('Baxi','Baxi'),	
)

CURRENT_BOILER_LOCATION_DROPDOWN = (
	('','Select One'),
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
	('N/A','N/A'),
)

LOCATION_OF_NEW_BOILER_DROPDOWN = (
	('','Select One'),
	('Existing Location','Existing Location'),
	('Open To Options','Open To Options'),
	('Relocate in current room','Relocate in current room'),
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

PARKING_AND_ACCESS_DROPDOWN = (
	('','Select One'),
	('No restrictions', 'No restrictions'),
	('Customer Driveway ( Customer Agreed)', 'Customer Driveway ( Customer Agreed)'),
	('Paid Parking Required', 'Paid Parking Required'),
	('Customer Provided Permit', 'Customer Provided Permit'),
	('Difficult', 'Difficult'),
	('Other See Notes', 'Other See Notes'),	
)

BRING_FORWARD_DROPDOWN = (
	('','Select One'),
	('No', 'No'),	
	('Yes', 'Yes'),	
)


MERCHANT_DROPDOWN = (
	('', 'Select One'),
	('2336@cityplumbing.co.uk', '2336@cityplumbing.co.uk'),
	('dan.lombard@cityplumbing.co.uk', 'dan.lombard@cityplumbing.co.uk'),
	('ben.cooper3@cityplumbing.co.uk', 'ben.cooper3@cityplumbing.co.uk'),
	('jon@tdlonline.co.uk', 'jon@tdlonline.co.uk'),
	('sam@tdlonline.co.uk', 'sam@tdlonline.co.uk'),
	('purchasing@yourheat.co.uk', 'purchasing@yourheat.co.uk'),

)

TIME_OVERRIDE_DROPDOWN = (
	('No override','No override'),
	('Anytime', 'Anytime'),
	('Anytime AM', 'Anytime AM'),
	('Anytime PM', 'Anytime PM')
)

''' Dropdowns for QuoteAcceptedForm '''
SELECTED_OPTION_DROPDOWN = (
	('A','A'),
	('B', 'B'),
)

PAYMENT_METHOD_DROPDOWN = (
	('Card','Card'),
	('BACS', 'BACS'),
	('Finance', 'Finance'),
)

FINANCE_DROPDOWN = (
	('Pass','Pass'),
	('Referred', 'Referred'),
	('Cash', 'Cash'),
)

URGENCY_DROPDOWN = (
	('ASAP','ASAP'),
	('Within a week', 'Within a week'),
	('Within a month', 'Within a month'),
	('Within 3 months', 'Within 3 months'),
	('Flexible', 'Flexible'),
)

CURRENT_BOILER_STATUS_DROPDOWN = (
	('Not working','Not working'),
	('Intermittent', 'Intermittent'),
	('Working', 'Working'),
)

TIME_OVERRIDE_DROPDOWN = (
	('No override','No override'),
	('Anytime', 'Anytime'),
	('Anytime AM', 'Anytime AM'),
	('Anytime PM', 'Anytime PM')
)

''' Dropdown fields for Heat Plans '''

BOILER_FUEL_TYPE_DROPDOWN = (
	('Not Yet Determined', 'Not Yet Determined'),
	('Gas Boiler', 'Gas Boiler'),
	('LPG Boiler', 'LPG Boiler'),
	('Oil Boiler', 'Oil Boiler')
)

TYPE_OF_PLAN_DROPDOWN = (
	('Not Yet Determined', 'Not Yet Determined'),
	('Boiler Service Care Plan', 'Boiler Service Care Plan'),
	('Boiler & Controls Care Plan', 'Boiler & Controls Care Plan'),
	('Full System Care Plan', 'Full System Care Plan')
)

CUSTOMER_PLAN_TYPE_DROPDOWN = (
	('', 'Select One'),
	('Prospective Home Owner', 'Prospective Home Owner'),
	('Prospective Landlord', 'Prospective Landlord'),
	('Confirmed Home Owner', 'Confirmed Home Owner'),
	('Confirmed Landlord', 'Confirmed Landlord')
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
		fields = ('first_name','last_name','email','company_name','telephone', 'baseline_work_rate', 'additional_daily_work_rate', 'quote_prefix', 'current_quote_number')

		widgets = {
			'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your First Name', 'autofocus': ''}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Last Name'}),
			'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
			'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Company Name'}),
			'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Telephone Number'}),
			'baseline_work_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the baseline work rate'}),
			'additional_daily_work_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your daily work rate'}),
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
		fields = ['brand', 'fuel_type', 'boiler_type', 'model_name', 'product_code', 'price', 'cost', 'product_image','guarantee']

		widgets = {
			'brand': forms.Select(attrs={'class': 'form-control',  'autofocus': ''}),
			'fuel_type': forms.Select(attrs={'class': 'form-control'}),
			'boiler_type': forms.Select(attrs={'class': 'form-control'}),
			'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Model Name'}),
			'product_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Product Code'}),
			'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Price of the product'}),
			'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Cost of the product'}),
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
		fields = ['brand', 'component_type', 'component_name', 'price', 'cost', 'est_time_duration']

		widgets = {
			'brand': forms.Select(attrs={'class': 'form-control',  'autofocus': ''}),
			'component_type': forms.Select(attrs={'class': 'form-control'}),
			'component_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Component Name'}),
			'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Price of the Component'}),
			'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Cost of the Component'}),
			'est_time_duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the estimate time duration'}),
		}

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(ProductComponentForm, self).__init__(*args, **kwargs)

''' Form for capturing the product components for the quote '''
class OptionalExtraForm(forms.ModelForm):
	
	class Meta:
		model = OptionalExtra
		fields = ['product_name', 'price']

		widgets = {
			'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Optional Extra Product Name'}),
			'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the Price of the Optional Extra'}),
		}

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(OptionalExtraForm, self).__init__(*args, **kwargs)		
		


''' Form for creating the capability for users to edit their own pdf layout for quote (not implemented in this release) '''
class EditQuoteTemplateForm(forms.Form):

	pdf_template_code = forms.CharField(widget=forms.Textarea(attrs={'rows':24, 'cols':100}))

	def __init__(self, user, *args, **kwargs):
		self.user = user
		super(EditQuoteTemplateForm, self).__init__(*args, **kwargs)
		usr_pdf_template_file = Path(settings.BASE_DIR + "/templates/pdf/user_{}/quote_for_pdf.html".format(self.user.username))
		template_file = open(usr_pdf_template_file,'r')
		self.fields['pdf_template_code'].initial = template_file.read
		alert = None


''' form for editing current_quote.txt (json file) '''
class EditCurrentQuoteDataForm(forms.Form):

	#quote_data = JSONField2()
	quote_data = forms.CharField(widget=forms.Textarea(attrs={'rows':24, 'cols':100}))

	def __init__(self, user, *args, **kwargs):
		self.user = user
		super(EditCurrentQuoteDataForm, self).__init__(*args, **kwargs)
		usr_data_template_file = Path(settings.BASE_DIR + "/pdf_quote_archive/user_{}/current_quote.txt".format(self.user.username))
		template_file = open(usr_data_template_file,'r')
		self.fields['quote_data'].initial = template_file.read
		alert = None


''' ----------- Form pages for yourheat -------------'''

class FormStepOne_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.0.field_name e.g. form_data.0.customer_first_name
	def __init__(self, *args, **kwargs):
		super(FormStepOne_yh, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	if settings.YH_SS_INTEGRATION:		
		customer_title = forms.CharField(max_length=20)		# Allow freeform populate from Smartsheet
	else:	
		customer_title = forms.ChoiceField(choices=CUSTOMER_TITLE_DROPDOWN)		# Provide Dropdown if not Smartsheet
	customer_first_name = forms.CharField(max_length=100)
	customer_last_name = forms.CharField(max_length=100)
	customer_primary_phone = forms.CharField(max_length=100)
	customer_secondary_phone = forms.CharField(max_length=100, required = False)
	customer_email = forms.EmailField()
	owner_tenant_or_landlord = forms.ChoiceField(choices=OWNER_TENANT_OR_LANDLORD_DROPDOWN)
	if settings.YH_SS_INTEGRATION:
		#smartsheet_id = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
		smartsheet_id = forms.CharField(max_length=100)
	
	
class FormStepTwo_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.1.field_name e.g. form_data.1.installation_address
	def __init__(self, *args, **kwargs):
		self.user_name = kwargs.pop('user_name')
		super(FormStepTwo_yh, self).__init__(*args, **kwargs)
		
		self.fields['house_name_or_number'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':60}))
		self.fields['street_address'] = forms.CharField(max_length=100)
		self.fields['city'] = forms.CharField(max_length=100)
		if settings.YH_SS_INTEGRATION:
			self.fields['county'] = forms.CharField(max_length=100, required=False)
		else:	
			self.fields['county'] = forms.CharField(max_length=100)
		self.fields['postcode'] = forms.CharField(max_length=100)
		self.fields['property_type'] = forms.ChoiceField(choices=PROPERTY_TYPE_DROPDOWN)	
		self.fields['alternative_billing_address'] = forms.ChoiceField(choices=ALTERNATIVE_BILLING_ADDRESS_DROPDOWN)
		if self.user_name == settings.YH_MASTER_PROFILE_USERNAME:		
			self.fields['billing_house_name_or_number'] = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={ 'placeholder': 'If different to installation address'}))
			self.fields['billing_street_address'] = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={ 'placeholder': 'If different to installation address'}))
			self.fields['billing_city'] = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={ 'placeholder': 'If different to installation address'}))
			self.fields['billing_county'] = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={ 'placeholder': 'If different to installation address'}))
			self.fields['billing_postcode'] = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={ 'placeholder': 'If different to installation address'}))
		else:
			self.fields['billing_house_name_or_number'] = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={ 'placeholder': 'If different to installation address', 'disabled': 'disabled'}))
			self.fields['billing_street_address'] = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={ 'placeholder': 'If different to installation address', 'disabled': 'disabled'}))
			self.fields['billing_city'] = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={ 'placeholder': 'If different to installation address', 'disabled': 'disabled'}))
			self.fields['billing_county'] = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={ 'placeholder': 'If different to installation address', 'disabled': 'disabled'}))
			self.fields['billing_postcode'] = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={ 'placeholder': 'If different to installation address', 'disabled': 'disabled'}))
		self.fields['heat_loss_house_type'] = forms.ChoiceField(choices=HEAT_LOSS_HOUSE_TYPE_DROPDOWN)
		self.fields['building_width'] = forms.FloatField( validators = [MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'placeholder': 'Metres'}))
		self.fields['building_length'] = forms.FloatField( validators = [MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'placeholder': 'Metres'}))
		self.fields['ceiling_height'] = forms.FloatField( validators = [MinValueValidator(0.0)],widget=forms.NumberInput(attrs={'placeholder': 'Metres'}))
		self.fields['floors'] = forms.IntegerField( validators = [MinValueValidator(0)], widget=forms.NumberInput(attrs={'placeholder': 'No. of floors'}))
		for field in self: 
				field.field.widget.attrs['class'] = 'form-control'


class FormStepThree_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.2.field_name e.g. form_data.2.current_fuel_type
	def __init__(self, *args, **kwargs):
		self.user_name = kwargs.pop('user_name')
		super(FormStepThree_yh, self).__init__(*args, **kwargs)
		self.fields['current_fuel_type'] = forms.ChoiceField(choices=CURRENT_FUEL_TYPE_DROPDOWN)
		self.fields['current_boiler_type'] = forms.ChoiceField(choices=CURRENT_BOILER_TYPE_DROPDOWN)
		self.fields['current_boiler_location'] = forms.ChoiceField(choices=CURRENT_BOILER_LOCATION_DROPDOWN)
		self.fields['current_flue_system'] = forms.ChoiceField(choices=CURRENT_FLUE_SYSTEM_DROPDOWN)
		self.fields['current_flue_location'] = forms.ChoiceField(choices=CURRENT_FLUE_LOCATION_DROPDOWN)
		self.fields['current_controls'] = forms.MultipleChoiceField(choices=CURRENT_CONTROLS_DROPDOWN)
		self.fields['current_radiators_working_correctly'] = forms.ChoiceField(choices=CURRENT_RADIATORS_WORKING_CORRECTLY_DROPDOWN)
		if self.user_name == settings.YH_MASTER_PROFILE_USERNAME:
			self.fields['locations_where_radiators_not_working_correctly'] = forms.MultipleChoiceField(required=False, choices=LOCATIONS_WHERE_RADIATORS_NOT_WORKING_CORRECTLY_DROPDOWN)
		else:
			self.fields['locations_where_radiators_not_working_correctly'] = forms.MultipleChoiceField(required=False, choices=LOCATIONS_WHERE_RADIATORS_NOT_WORKING_CORRECTLY_DROPDOWN, disabled=True)
		#locations_where_radiators_not_working_correctly = forms.MultipleChoiceField(required=False, choices=LOCATIONS_WHERE_RADIATORS_NOT_WORKING_CORRECTLY_DROPDOWN, widget=forms.SelectMultiple(attrs={'disabled': 'disabled'}))
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	
class FormStepFour_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.3.field_name e.g. form_data.3.removals
	def __init__(self, *args, **kwargs):
		self.user_name = kwargs.pop('user_name')
		super(FormStepFour_yh, self).__init__(*args, **kwargs)
		self.fields['removals'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
											 choices=REMOVALS_CHOICES)
		if self.user_name == settings.YH_MASTER_PROFILE_USERNAME:									 
			self.fields['radiator_quantity'] = forms.IntegerField(required=False, validators = [MinValueValidator(0)], widget=forms.NumberInput(attrs={ 'placeholder': 'If appropriate'}))
		else:
			self.fields['radiator_quantity'] = forms.IntegerField(required=False, validators = [MinValueValidator(0)], widget=forms.NumberInput(attrs={ 'placeholder': 'If appropriate', 'disabled': 'disabled'}))

class FormStepFive_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.4.field_name e.g. form_data.4.new_fuel_type
	def __init__(self, *args, **kwargs):
		# Get the user to seed the filter on the boiler_manufacturer drop down.
		self.user = kwargs.pop('user')
		self.user_name = kwargs.pop('user_name')
		super(FormStepFive_yh, self).__init__(*args, **kwargs)
		self.fields['new_fuel_type'] = forms.ChoiceField(choices=NEW_FUEL_TYPE_DROPDOWN)
		self.fields['new_boiler_type'] = forms.ChoiceField(choices=NEW_BOILER_TYPE_DROPDOWN)
		self.fields['new_boiler_location'] = forms.ChoiceField(choices=NEW_BOILER_LOCATION_DROPDOWN)
		self.fields['new_flue_system'] = forms.ChoiceField(choices=NEW_FLUE_SYSTEM_DROPDOWN)
		self.fields['new_flue_location'] = forms.ChoiceField(choices=NEW_FLUE_LOCATION_DROPDOWN)
		self.fields['new_flue_diameter'] = forms.ChoiceField(choices=NEW_FLUE_DIAMETER_DROPDOWN)
		self.fields['plume_management_kit'] = forms.ChoiceField(choices=PLUME_MANAGEMENT_KIT_DROPDOWN)
		self.fields['condensate_termination'] = forms.ChoiceField(choices=CONDENSATE_TERMINATION_DROPDOWN)
		#new_controls = forms.MultipleChoiceField(choices=NEW_CONTROLS_DROPDOWN)
		self.fields['new_controls'] = forms.ChoiceField(choices=NEW_CONTROLS_DROPDOWN)
		self.fields['incoming_flow_rate'] = forms.ChoiceField(choices=INCOMING_FLOW_RATE_DROPDOWN)
		self.fields['will_boiler_be_housed_in_cupboard'] = forms.ChoiceField(choices=WILL_BOILER_BE_HOUSED_IN_CUPBOARD_DROPDOWN)
		if self.user_name == settings.YH_MASTER_PROFILE_USERNAME:
			self.fields['cupboard_height'] = forms.IntegerField(required=False, validators = [MinValueValidator(0)],  widget=forms.NumberInput(attrs={ 'placeholder': 'If appropriate'}))
			self.fields['cupboard_width'] = forms.IntegerField(required=False, validators = [MinValueValidator(0)], widget=forms.NumberInput(attrs={ 'placeholder': 'If appropriate'}))
			self.fields['cupboard_depth'] = forms.IntegerField(required=False, validators = [MinValueValidator(0)], widget=forms.NumberInput(attrs={ 'placeholder': 'If appropriate'}))
		else:
			self.fields['cupboard_height'] = forms.IntegerField(required=False, validators = [MinValueValidator(0)],  widget=forms.NumberInput(attrs={ 'placeholder': 'If appropriate', 'disabled': 'disabled'}))
			self.fields['cupboard_width'] = forms.IntegerField(required=False, validators = [MinValueValidator(0)], widget=forms.NumberInput(attrs={ 'placeholder': 'If appropriate', 'disabled': 'disabled'}))
			self.fields['cupboard_depth'] = forms.IntegerField(required=False, validators = [MinValueValidator(0)], widget=forms.NumberInput(attrs={ 'placeholder': 'If appropriate', 'disabled': 'disabled'}))
		self.fields['boiler_manufacturer'] = forms.ModelChoiceField(queryset=ProductPrice.objects.filter(user = self.user).order_by('brand').values_list('brand', flat=True).distinct(), to_field_name='brand',empty_label = 'Select Boiler Brand for quote')
		self.fields['alt_boiler_manufacturer'] = forms.ModelChoiceField(required=False, queryset=ProductPrice.objects.filter(user = self.user).order_by('brand').values_list('brand', flat=True).distinct(), to_field_name='brand',empty_label = 'Select Alternative Boiler Brand if required')
		for field in self: 
				field.field.widget.attrs['class'] = 'form-control'

class FormStepSix_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.5.field_name e.g. form_data.5.new_fuel_type
	#heat_loss_value = forms.DecimalField(required=False)

	def __init__(self, *args, **kwargs):
		# Get the user to seed the filter on the drop down.
		self.user = kwargs.pop('user')
		self.manuf = kwargs.pop('manufacturer')
		self.alt_manuf = kwargs.pop('alt_manufacturer')
		self.fuel_type = kwargs.pop('fuel_type')
		self.boiler_type = kwargs.pop('boiler_type')
		self.user_name = kwargs.pop('user_name')
		#self.heat_loss_value = kwargs.pop('heat_loss_value')
		super(FormStepSix_yh, self).__init__(*args, **kwargs)
		self.fields['chemical_system_treatment'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Chemical System Treatment').order_by('brand').only('component_name')])
		self.fields['fuel_supply_requirements'] = forms.ChoiceField(choices=FUEL_SUPPLY_DROPDOWN)
		#self.fields['fuel_supply_length'] = forms.MultipleChoiceField(required = False, choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Fuel Supply Length').order_by('-component_name').only('component_name')], widget=forms.Select(attrs={'disabled': 'disabled'}))
		self.fields['fuel_supply_length'] = forms.MultipleChoiceField(required = False, choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Fuel Supply Length').order_by('-component_name').only('component_name')])
		self.fields['scaffolding_required'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Scaffolding').order_by('-component_name').only('component_name')])
		self.fields['asbestos_containing_materials_identified'] = forms.ChoiceField(choices=ASBESTOS_CONTAINING_MATERIALS_IDENTIFIED_DROPDOWN)
		if self.user_name == settings.YH_MASTER_PROFILE_USERNAME:
			self.fields['asbestos_removal_procedure'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Asbestos Removal Procedure').order_by('brand').only('component_name')])
		else:
			self.fields['asbestos_removal_procedure'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Asbestos Removal Procedure').order_by('brand').only('component_name')], widget=forms.Select(attrs={'disabled': 'disabled'}))
		#self.fields['electrical_work_required'] = forms.ChoiceField(choices=ELECTRICAL_WORK_REQUIRED_DROPDOWN)
		self.fields['electrical_work_required'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Electrical Work').order_by('brand').only('component_name')])
		self.fields['potential_contractor_attendance_required'] = forms.ChoiceField(choices=POTENTIAL_CONTRACTOR_ATTENDANCE_REQUIRED_DROPDOWN)
		if self.user_name == settings.YH_MASTER_PROFILE_USERNAME:
			self.fields['details_on_potential_contractor_requirements'] = forms.CharField(max_length=2000, required = False, widget=forms.Textarea(attrs={'rows':3, 'cols':30, 'placeholder': 'if applicable, please be detailed'}))
		else:
			self.fields['details_on_potential_contractor_requirements'] = forms.CharField(max_length=2000, required = False, widget=forms.Textarea(attrs={'rows':3, 'cols':30, 'placeholder': 'if applicable, please be detailed', 'disabled': 'disabled'}))
		#self.fields['parking_requirements'] = forms.CharField(max_length=2000, required = False, widget=forms.Textarea(attrs={'rows':3, 'cols':30, 'placeholder': 'if applicable, please be detailed'}))
		#self.fields['parking_requirements'] = forms.CharField(max_length=2000, required = False, widget=forms.Textarea(attrs={'rows':3, 'cols':30, 'placeholder': 'if applicable, please be detailed'}))
		self.fields['parking_requirements'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Parking').order_by('brand').only('component_name')])

		self.fields['product_choice'] = forms.ModelChoiceField(queryset=ProductPrice.objects.filter(user = self.user, brand = self.manuf, fuel_type = self.fuel_type, boiler_type = self.boiler_type ), empty_label = 'Select Product for quote')
		if self.alt_manuf:
			self.fields['alt_product_choice'] = forms.ModelChoiceField(required=True, queryset=ProductPrice.objects.filter(user = self.user, brand = self.alt_manuf, fuel_type = self.fuel_type, boiler_type = self.boiler_type), empty_label = 'Select Alternative Product for quote')
		else:
			self.fields['alt_product_choice'] = forms.ModelChoiceField(required=False, queryset=ProductPrice.objects.filter(user = self.user, brand = self.alt_manuf, fuel_type = self.fuel_type, boiler_type = self.boiler_type), empty_label = 'Select Alternative Product for quote')
		# Initialise the component_duration_total field
		#self.fields['heat_loss_value'].initial = self.heat_loss_value	
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'

class FormStepSeven_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.6.field_name e.g. form_data.6.boiler_manufactureruel_type
	alt_manufx = forms.BooleanField(required=False)	# Temp boolean field value to determine if alt_manuf has been selected 

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self.manuf = kwargs.pop('manufacturer')
		self.alt_manuf = kwargs.pop('alt_manufacturer')
		#print(self.alt_manuf)
		self.plume_management_kit = kwargs.pop('plume_management_kit')
		self.new_fuel_type = kwargs.pop('new_fuel_type')
		self.new_controls = kwargs.pop('new_controls')
		self.boiler_type = kwargs.pop('boiler_type')
		self.user_name = kwargs.pop('user_name')
		super(FormStepSeven_yh, self).__init__(*args, **kwargs)
		#self.fields['gas_flue_components'] = forms.ModelMultipleChoiceField(required=True, queryset=ProductComponent.objects.filter(user = self.user, brand = self.manuf, component_type = 'Gas Flue Component').only('component_name'))
		if self.new_fuel_type == 'Oil':
			self.fields['oil_flue_components'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Oil Flue Component').only('component_name')])
		else:	
			self.fields['gas_flue_components'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Gas Flue Component').only('component_name')])
		if self.plume_management_kit == "Required":
			#self.fields['plume_components'] = forms.ModelMultipleChoiceField(required=True, queryset=ProductComponent.objects.filter(user = self.user, brand = self.manuf, component_type = 'Plume Component').only('component_name'))
			self.fields['plume_components'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Plume Component').only('component_name')])
		else:
			self.fields['plume_components'] = forms.ChoiceField(required=False, choices = (('Not Required (from step 5)','Not Required (from step 5)'),('Required','Required')), widget=forms.Select(attrs={'disabled': 'disabled'}))
		if self.alt_manuf:
			self.fields['alt_manufx'].disabled = True
			self.fields['alt_manufx'].initial = True
			if self.new_fuel_type == 'Oil':
				self.fields['alt_oil_flue_components'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.alt_manuf), user = self.user, component_type = 'Oil Flue Component').only('component_name')])
			else:	
				self.fields['alt_gas_flue_components'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.alt_manuf), user = self.user, component_type = 'Gas Flue Component').only('component_name')])	
		else:
			self.fields['alt_manufx'].disabled = True
			self.fields['alt_manufx'].initial = False
			if self.new_fuel_type == 'Oil':
				self.fields['alt_oil_flue_components'] = forms.ChoiceField(required=False, choices = (('Not Required (no Alternative Boiler)','Not Required (no Alternative Boiler)'),('Required','Required')), widget=forms.Select(attrs={'disabled': 'disabled'}))
			else:
				self.fields['alt_gas_flue_components'] = forms.ChoiceField(required=False, choices = (('Not Required (no Alternative Boiler)','Not Required (no Alternative Boiler)'),('Required','Required')), widget=forms.Select(attrs={'disabled': 'disabled'}))				
		if self.new_controls != 'Connect on to Existing':		
			self.fields['programmer_thermostat'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Programmer Thermostat').order_by('brand').only('component_name')])
			if self.alt_manuf:
				self.fields['alt_programmer_thermostat'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.alt_manuf), user = self.user, component_type = 'Programmer Thermostat').order_by('brand').only('component_name')])
			else:
				self.fields['alt_programmer_thermostat'] = forms.ChoiceField(required=False, choices = (('Not Required (no Alternative Boiler)','Not Required (no Alternative Boiler)'),('Required','Required')), widget=forms.Select(attrs={'disabled': 'disabled'}))
		else:
			self.fields['programmer_thermostat'] = forms.ChoiceField(required=False, choices = (('Not Required-Connect on to Existing (from step 5)','Not Required-Connect on to Existing (from step 5)'),('Required','Required')), widget=forms.Select(attrs={'disabled': 'disabled'}))
			if self.alt_manuf:
				self.fields['alt_programmer_thermostat'] = forms.ChoiceField(required=False, choices = (('Not Required-Connect on to Existing (from step 5)','Not Required-Connect on to Existing (from step 5)'),('Required','Required')), widget=forms.Select(attrs={'disabled': 'disabled'}))

		self.fields['additional_central_heating_components'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Additional Central Heating Component').order_by('-component_name').only('component_name')])
		self.fields['central_heating_system_filter'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Central Heating System Filter').order_by('brand').only('component_name')])
		self.fields['scale_reducer'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Scale Reducer').order_by('brand').only('component_name')])
		self.fields['condensate_components'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Condenstate Component').order_by('brand').only('component_name')])
		self.fields['additional_copper_required'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Additional Copper').order_by('brand').only('component_name')])
		self.fields['fittings_packs'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Fitting Pack').order_by('brand').only('component_name')])
		self.fields['electrical_pack'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Electrical Pack').order_by('brand').only('component_name')])
		self.fields['earth_spike_required'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Earth Spike').order_by('brand').only('component_name')])
		self.fields['filling_link'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Filling Link').order_by('-component_name').only('component_name')])
		#self.fields['special_lift_requirements'] = forms.ChoiceField(choices=SPECIAL_LIFT_REQUIREMENTS_DROPDOWN)
		#self.fields['special_lift_requirements'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Special Lift').order_by('brand').only('component_name')])
		#self.fields['double_handed_lift_required'] = forms.ChoiceField(choices=DOUBLE_HANDED_LIFT_REQUIRED_DROPDOWN)
		self.fields['double_handed_lift_required'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Double Handed Lift').order_by('brand').only('component_name')])
		self.fields['building_pack_required'] = forms.MultipleChoiceField(choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Building Pack').order_by('brand').only('component_name')])
		if self.boiler_type == 'Combi':
			self.fields['cylinder'] = forms.ChoiceField(required=False, choices = (('Not Required (Combi Boiler)','Not Required (Combi Boiler)'),('Required','Required')), widget=forms.Select(attrs={'disabled': 'disabled'}))
		else:
			self.fields['cylinder'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(Q(brand='Applicable for All') | Q(brand=self.manuf), user = self.user, component_type = 'Cylinder').order_by('brand').only('component_name')])

		
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'

	special_part_1 = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={ 'placeholder': 'If required'}))
	special_part_2 = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={ 'placeholder': 'If required'}))
	special_part_3 = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={ 'placeholder': 'If required'}))
	special_part_qty_1 = forms.IntegerField(required=False, validators = [MinValueValidator(0)])
	special_part_qty_2 = forms.IntegerField(required=False, validators = [MinValueValidator(0)])
	special_part_qty_3 = forms.IntegerField(required=False, validators = [MinValueValidator(0)])
	special_part_price_1 = forms.DecimalField(required=False, max_digits=7, decimal_places=2, initial=0)
	special_part_price_2 = forms.DecimalField(required=False, max_digits=7, decimal_places=2, initial=0)
	special_part_price_3 = forms.DecimalField(required=False, max_digits=7, decimal_places=2, initial=0)
	special_part_duration_1 = forms.DecimalField(required=False, max_digits=7, decimal_places=2, initial=0)
	special_part_duration_2 = forms.DecimalField(required=False, max_digits=7, decimal_places=2, initial=0)
	special_part_duration_3 = forms.DecimalField(required=False, max_digits=7, decimal_places=2, initial=0)
	
class FormStepEight_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.7.field_name e.g. form_data.7.radiator_requirements
	
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(FormStepEight_yh, self).__init__(*args, **kwargs)
		self.fields['loc_1'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_2'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_3'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_4'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_5'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_6'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_7'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_8'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_9'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_10'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_11'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_12'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_13'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_14'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_15'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_16'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_17'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_18'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_19'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])
		self.fields['loc_20'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Location').order_by('brand').only('component_name')])

		self.fields['rad_1'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_2'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_3'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_4'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_5'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_6'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_7'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_8'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_9'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_10'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_11'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_12'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_13'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_14'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_15'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_16'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_17'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_18'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_19'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])
		self.fields['rad_20'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator').order_by('brand').only('component_name')])

		self.fields['sty_1'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_2'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_3'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_4'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_5'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_6'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_7'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_8'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_9'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_10'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_11'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_12'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_13'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_14'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_15'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_16'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_17'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_18'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_19'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])
		self.fields['sty_20'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Radiator Style').order_by('brand').only('component_name')])


		self.fields['val_1'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])
		self.fields['val_2'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])
		self.fields['val_3'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])
		self.fields['val_4'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])
		self.fields['val_5'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])
		self.fields['val_6'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])
		self.fields['val_7'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])
		self.fields['val_8'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])
		self.fields['val_9'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])
		self.fields['val_10'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])
		self.fields['val_11'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])
		self.fields['val_12'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Thermostatic Radiator Valve').order_by('brand').only('component_name')])

		self.fields['vaq_1'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		self.fields['vaq_2'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		self.fields['vaq_3'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		self.fields['vaq_4'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		self.fields['vaq_5'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		self.fields['vaq_6'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		self.fields['vaq_7'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		self.fields['vaq_8'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		self.fields['vaq_9'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		self.fields['vaq_10'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		self.fields['vaq_11'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		self.fields['vaq_12'] = forms.ChoiceField(required=False, choices=RADIATOR_VALVE_QTY_DROPDOWN)
		
		self.fields['tow_1'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Towel Rail').order_by('brand').only('component_name')])
		self.fields['tow_2'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Towel Rail').order_by('brand').only('component_name')])
		self.fields['tow_3'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Towel Rail').order_by('brand').only('component_name')])
		self.fields['tow_4'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Towel Rail').order_by('brand').only('component_name')])

		self.fields['trl_1'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Towel Rail Location').order_by('brand').only('component_name')])
		self.fields['trl_2'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Towel Rail Location').order_by('brand').only('component_name')])
		self.fields['trl_3'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Towel Rail Location').order_by('brand').only('component_name')])
		self.fields['trl_4'] = forms.ChoiceField(required = False, choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Towel Rail Location').order_by('brand').only('component_name')])

		#self.fields['cust_supply_radiator_quantity'] = forms.IntegerField(required=False, validators = [MinValueValidator(0)])

	radiator_specification = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs = {'onchange' : "radiator_handler();"}),
											 choices=RADIATOR_SPECIFICATION_CHOICES)	

class ExtrasModelChoiceField(ModelChoiceField):
	def label_from_instance(self, obj):
		#return obj.name
		return "%s - £%s" % (obj.product_name,  obj.price)	
		#return obj.price

	
class FormStepNine_yh(forms.Form):
	# Fields in this class are rendered in the quote_for_pdf.html file with the following notation
	# within double curly braces...
	# form_data.8.field_name e.g. form_data.8.estimated_duration
	#estimated_duration = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=ESTIMATED_DURATION_DROPDOWN)	
	description_of_works = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':12, 'cols':60}))
	surveyors_notes = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':5, 'cols':60}))
	optional_extras = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs = {'class': 'form-check-input', 'onchange' : "extras_handler();"}))
	component_duration_total = forms.DecimalField(required=False)
	disruption_and_pipework_routes = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':5, 'cols':60, 'placeholder': 'Please record any pipe runs discussed in detail and any disruption the installation will cause to the property'}))
	addition_comments_for_requote = forms.CharField(required=False, max_length=2000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':8, 'cols':60}))

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self.component_duration_total = kwargs.pop('component_duration_total')
		super(FormStepNine_yh, self).__init__(*args, **kwargs)
		self.fields['estimated_duration'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(user = self.user, component_type = 'Estimated Duration').order_by('brand').only('component_name')])

		self.fields['extra_1'] = ExtrasModelChoiceField(required=False, queryset=OptionalExtra.objects.filter(user = self.user))
		self.fields['extra_2'] = ExtrasModelChoiceField(required=False, queryset=OptionalExtra.objects.filter(user = self.user))
		self.fields['extra_3'] = ExtrasModelChoiceField(required=False, queryset=OptionalExtra.objects.filter(user = self.user))
		self.fields['extra_4'] = ExtrasModelChoiceField(required=False, queryset=OptionalExtra.objects.filter(user = self.user))
		self.fields['extra_5'] = ExtrasModelChoiceField(required=False, queryset=OptionalExtra.objects.filter(user = self.user))
		self.fields['extra_6'] = ExtrasModelChoiceField(required=False, queryset=OptionalExtra.objects.filter(user = self.user))
		self.fields['extra_7'] = ExtrasModelChoiceField(required=False, queryset=OptionalExtra.objects.filter(user = self.user))
		self.fields['extra_8'] = ExtrasModelChoiceField(required=False, queryset=OptionalExtra.objects.filter(user = self.user))
		self.fields['extra_9'] = ExtrasModelChoiceField(required=False, queryset=OptionalExtra.objects.filter(user = self.user))
		self.fields['extra_10'] = ExtrasModelChoiceField(required=False, queryset=OptionalExtra.objects.filter(user = self.user))

		self.fields['extra_qty_1'] = forms.ChoiceField(required=False, choices=OPTIONAL_EXTRAS_QTY_DROPDOWN)
		self.fields['extra_qty_2'] = forms.ChoiceField(required=False, choices=OPTIONAL_EXTRAS_QTY_DROPDOWN)
		self.fields['extra_qty_3'] = forms.ChoiceField(required=False, choices=OPTIONAL_EXTRAS_QTY_DROPDOWN)
		self.fields['extra_qty_4'] = forms.ChoiceField(required=False, choices=OPTIONAL_EXTRAS_QTY_DROPDOWN)
		self.fields['extra_qty_5'] = forms.ChoiceField(required=False, choices=OPTIONAL_EXTRAS_QTY_DROPDOWN)
		self.fields['extra_qty_6'] = forms.ChoiceField(required=False, choices=OPTIONAL_EXTRAS_QTY_DROPDOWN)
		self.fields['extra_qty_7'] = forms.ChoiceField(required=False, choices=OPTIONAL_EXTRAS_QTY_DROPDOWN)
		self.fields['extra_qty_8'] = forms.ChoiceField(required=False, choices=OPTIONAL_EXTRAS_QTY_DROPDOWN)
		self.fields['extra_qty_9'] = forms.ChoiceField(required=False, choices=OPTIONAL_EXTRAS_QTY_DROPDOWN)
		self.fields['extra_qty_10'] = forms.ChoiceField(required=False, choices=OPTIONAL_EXTRAS_QTY_DROPDOWN)

		# Initialise the description of works field
		text = "Our engineer(s) will install your new boiler and equipment safely and efficiently with minimal disruption to your home.  To protect the boiler, system and radiators from sludge and corrosion, a Magnetic System Filter will be installed. The system will also be chemically flushed as a minimum, along with the required dose of inhibitor added to protect the system.\n\n"
		text = text + "The engineer(s) will arrive each day between 08:00 and 09:30 and before they leave, your new system will be fully tested and commissioned. The necessary safety certificates will be registered on completion and all paperwork will be sent you direct from the manufacturer and building control. We promise they will take good care of your home, using dust sheets to protect all surfaces.\n\n"
		text = text + "All waste will be disposed of in accordance with current Waste Disposal Regulation. While we always endeavour to keep the installation to the estimated duration, we may use additional labour to achieve completion in a shorter time-frame, or we may require additional days on site."
		self.fields['description_of_works'].initial = text

		# Initialise the component_duration_total field
		self.fields['component_duration_total'].initial = self.component_duration_total



class FinanceForm_yh(forms.Form):
	total_cost = forms.FloatField()
	alt_total_cost = forms.FloatField()
	deposit_amount = forms.FloatField()
	deposit_amount_thirty_percent = forms.DecimalField()
	ib36_loan_amount = forms.CharField(max_length=30)
	ib36_monthly_payment = forms.CharField(max_length=30)
	ib36_total_payable = forms.CharField(max_length=30)
	ib48_loan_amount = forms.CharField(max_length=30)
	ib48_monthly_payment = forms.CharField(max_length=30)
	ib48_total_payable = forms.CharField(max_length=30)
	ib60_loan_amount = forms.CharField(max_length=30)
	ib60_monthly_payment = forms.CharField(max_length=30)
	ib60_total_payable = forms.CharField(max_length=30)
	ib96_loan_amount = forms.CharField(max_length=30)
	ib96_monthly_payment = forms.CharField(max_length=30)
	ib96_total_payable = forms.CharField(max_length=30)
	ib120_loan_amount = forms.CharField(max_length=30)
	ib120_monthly_payment = forms.CharField(max_length=30)
	ib120_total_payable = forms.CharField(max_length=30)

	product_price = forms.DecimalField()
	component_price_total = forms.DecimalField()
	parts_price_total = forms.DecimalField()
	estimated_duration_cost = forms.DecimalField()
	component_duration_total = forms.DecimalField()

	interest_free_12m_deposit_amount = forms.CharField(max_length=30)
	interest_free_12m_monthly_payment = forms.CharField(max_length=30)
	interest_free_12m_loan_amount = forms.CharField(max_length=30)
	interest_free_12m_total_payable = forms.CharField(max_length=30)

	def __init__(self, *args, **kwargs):
		self.product_price = kwargs.pop('product_price')
		self.component_price_total = kwargs.pop('component_price_total')
		self.parts_price_total = kwargs.pop('parts_price_total')
		#print(self.parts_price_total)
		self.estimated_duration_cost = kwargs.pop('estimated_duration_cost')
		self.component_duration_total = kwargs.pop('component_duration_total')
		self.total_quote_price = kwargs.pop('total_quote_price')
		self.alt_total_quote_price = kwargs.pop('alt_total_quote_price')
		self.user_name = kwargs.pop('user_name')
		super(FinanceForm_yh, self).__init__(*args, **kwargs)
		if self.user_name == settings.YH_MASTER_PROFILE_USERNAME:
			self.fields['total_cost'].disabled = False
		else:	
			self.fields['total_cost'].disabled = True
		self.fields['total_cost'].initial = self.total_quote_price
		self.fields['deposit_amount'].initial = round((float(self.total_quote_price) * 30) / 100, 2)
		self.fields['deposit_amount'].decimal_places = 2
		self.fields['deposit_amount_thirty_percent'].initial = (float(self.total_quote_price) * 30) / 100
		self.fields['interest_free_12m_deposit_amount'].initial = (float(self.total_quote_price) * 30) / 100
		self.fields['product_price'].initial = self.product_price
		self.fields['component_price_total'].initial = self.component_price_total
		self.fields['parts_price_total'].initial = self.parts_price_total
		self.fields['estimated_duration_cost'].initial = self.estimated_duration_cost
		self.fields['component_duration_total'].initial = self.component_duration_total
		self.fields['alt_total_cost'].initial = self.alt_total_quote_price
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
		self.fields['include_interest_free_option'] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs = {'class': 'form-check-input'}))	
		self.fields['include_interest_free_option'].initial = True

class ssCustomerSelectForm(forms.Form):
	customers_for_quote = forms.ChoiceField(required = False, choices=[])

	def __init__(self, *args, **kwargs):
		customer_choices = kwargs.pop('customer_choices')
		super().__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
		self.fields['customers_for_quote'].choices = customer_choices

class ssPostSurveyQuestionsForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ssPostSurveyQuestionsForm, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	smartsheet_id = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_first_name = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_last_name = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	postcode = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	reason_for_quote = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':5, 'cols':60}))
	why_you_quoted_what_you_quoted = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':5, 'cols':60}))
	why_customer_did_not_go_ahead_on_day = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':5, 'cols':60}))
	important_to_customer = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':5, 'cols':60, 'placeholder': 'Useful info, finance, servicing etc'}))

class ssSurveyAppointmentForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ssSurveyAppointmentForm, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'

	surveyor = forms.ChoiceField(choices=SURVEYOR_DROPDOWN)
	#survey_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
	survey_date_and_time = forms.DateTimeField(initial=datetime.datetime.now().strftime('%d/%m/%Y %H:00'), input_formats=['%d/%m/%Y %H:%M'])
	time_override = forms.ChoiceField(required=False, choices=TIME_OVERRIDE_DROPDOWN)

	smartsheet_id = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_title = forms.CharField(max_length=20)		
	customer_first_name = forms.CharField(max_length=100)
	customer_last_name = forms.CharField(max_length=100)
	customer_primary_phone = forms.CharField(max_length=100)
	#customer_secondary_phone = forms.CharField(max_length=100, required = False)
	customer_email = forms.EmailField()
	house_name_or_number = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':60}))
	street_address = forms.CharField(max_length=100)
	city = forms.CharField(max_length=100)
	county = forms.CharField(max_length=100, required=False)
	postcode = forms.CharField(max_length=100)
	current_boiler_status = forms.CharField(max_length=100)
	fuel_type = forms.CharField(max_length=100)
	current_system = forms.CharField(max_length=100)
	system_wanted = forms.CharField(max_length=100)
	property_type = forms.CharField(max_length=100)
	number_of_bedrooms = forms.CharField(max_length=100)
	number_of_bathrooms = forms.CharField(max_length=100)
	hot_water_cylinder = forms.CharField(max_length=100)
	website_premium_package_quote = forms.CharField(max_length=20, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	website_standard_package_quote = forms.CharField(max_length=20, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	website_economy_package_quote = forms.CharField(max_length=20, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	additional_information = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':3, 'cols':60}))
	#-------- Above fields are populated from Smartsheet - Below by user -------------
	lead_booker = forms.ChoiceField(choices=LEAD_BOOKER_DROPDOWN)
	customer_confirmed = forms.ChoiceField(choices=CUSTOMER_CONFIRMED_DROPDOWN)
	survey_attendee = forms.ChoiceField(choices=SURVEY_ATTENDEE_DROPDOWN, widget=forms.Select(attrs = {'onchange' : "attendee_handler();"}))
	survey_other_attendee = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={ 'placeholder': 'Details on [Other] if selected above'}))
	brand_preference = forms.ChoiceField(choices=BRAND_PREFERENCE_DROPDOWN)
	current_boiler_location = forms.ChoiceField(choices=CURRENT_BOILER_LOCATION_DROPDOWN)
	location_of_new_boiler = forms.ChoiceField(choices=LOCATION_OF_NEW_BOILER_DROPDOWN)
	parking_and_access = forms.ChoiceField(choices=PARKING_AND_ACCESS_DROPDOWN)
	customer_interested_in_bring_forward = forms.ChoiceField(choices=BRING_FORWARD_DROPDOWN)

class ssInstallationAppointmentForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ssInstallationAppointmentForm, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'

	engineer = forms.ChoiceField(choices=ENGINEER_DROPDOWN)
	#installation_date = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS,widget=forms.TextInput(attrs={ 'placeholder': 'DD-MM-YYYY'}))
	installation_date = forms.DateField(initial=datetime.datetime.now().strftime('%d/%m/%Y'), input_formats=['%d/%m/%Y'])
	#widget=forms.TextInput(attrs={ 'placeholder': 'If different to installation address', 'disabled': 'disabled'})
	surveyor = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	#installation_date_and_time = forms.DateTimeField(initial=datetime.datetime.now().strftime('%d/%m/%Y %H:00'), input_formats=['%d/%m/%Y %H:%M'])
	installation_days_required = forms.FloatField()
	smartsheet_id = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_title = forms.CharField(max_length=20, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))		
	customer_first_name = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_last_name = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_primary_phone = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	#customer_secondary_phone = forms.CharField(max_length=100, required = False)
	customer_email = forms.EmailField(required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	house_name_or_number = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'size':60, 'readonly':'readonly'}))
	street_address = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	city = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	county = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	postcode = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	#current_boiler_status = forms.CharField(max_length=100)
	agreed_boiler_option = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	boiler_brand = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	additional_information = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':3, 'cols':60}))
	PO_number = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	PO_supplier = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	PO_supplier_address = forms.CharField(max_length=200, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	surveyor_notes	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':3, 'cols':60, 'readonly':'readonly'}))
	parts_list = forms.CharField(max_length=3000, required=False, widget=forms.HiddenInput())

class ssGetPhotosForUploadForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ssGetPhotosForUploadForm, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	smartsheet_id = forms.CharField(max_length=100, required=True)
	#customer_first_name = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	#customer_last_name = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))

class QuoteAcceptedForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(QuoteAcceptedForm, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	smartsheet_id = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_first_name = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_last_name = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	postcode = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	selected_option = forms.ChoiceField(choices=SELECTED_OPTION_DROPDOWN)
	payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_DROPDOWN)
	finance = forms.ChoiceField(choices=FINANCE_DROPDOWN)
	urgency = forms.ChoiceField(choices=URGENCY_DROPDOWN)
	current_boiler_status = forms.ChoiceField(choices=CURRENT_BOILER_STATUS_DROPDOWN)
	days_required_for_installation = forms.CharField(max_length=20, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	optional_extras = forms.CharField(max_length=2000, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':5, 'cols':60}))
	primary_product_choice = forms.CharField(max_length=200, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	alternative_product_choice = forms.CharField(max_length=200, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))

class JobPartsForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(JobPartsForm, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	PO = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	house_name_or_number = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	street_address = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	city = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	county = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	postcode = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	#job_date = forms.DateField(initial=datetime.datetime.now().strftime('%d/%m/%Y'), input_formats=['%d/%m/%Y'])
	installation_date = forms.DateField(input_formats=['%d/%m/%Y'])
	engineer = forms.ChoiceField(choices=ENGINEER_POSTCODE_DROPDOWN)
	merchant = forms.ChoiceField(choices=MERCHANT_DROPDOWN)
	delivery_or_collection = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':3, 'cols':60}))
	agreed_boiler_option = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	parts = forms.CharField(max_length=4000, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':5, 'cols':60}))
	optional_extras_taken = forms.CharField(max_length=4000, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':5, 'cols':60}))
	additional_information = forms.CharField(max_length=2000, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':3, 'cols':60}))

class SpecialOfferForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(SpecialOfferForm, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	smartsheet_id = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_title = forms.CharField(max_length=20, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))		
	customer_first_name = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_last_name = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_email = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	survey_date = forms.CharField(max_length=30, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	#quote_date = forms.DateField(input_formats=['%d/%m/%Y'], required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	primary_boiler = forms.CharField(max_length=300, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	alternative_boiler = forms.CharField(max_length=300, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	primary_boiler_price = forms.CharField(max_length=20, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	alternative_boiler_price = forms.CharField(max_length=20, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	agreed_boiler_option = forms.CharField(max_length=100, required=False, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	special_offer_details = forms.CharField(max_length=4000, required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':5, 'cols':60}))

class HeatPlanForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(HeatPlanForm, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	smartsheet_id = forms.CharField(max_length=100, widget = forms.TextInput(attrs={'readonly':'readonly'}))
	customer_title = forms.CharField(max_length=20)		
	customer_first_name = forms.CharField(max_length=100)
	customer_last_name = forms.CharField(max_length=100)
	customer_email = forms.EmailField(max_length=100)
	fuel_type = forms.ChoiceField(choices=BOILER_FUEL_TYPE_DROPDOWN)
	type_of_plan = forms.ChoiceField(choices=TYPE_OF_PLAN_DROPDOWN)
	customer_plan_type = forms.ChoiceField(choices=CUSTOMER_PLAN_TYPE_DROPDOWN)

class CustomerEnquiryForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(CustomerEnquiryForm, self).__init__(*args, **kwargs)
		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'
	questions_about_the_quote = forms.CharField(max_length=4000, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':40}))
	questions_about_finance = forms.CharField(max_length=4000, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':40}))
	changes_customer_would_like = forms.CharField(max_length=4000, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':40}))
	feedback_on_the_visit = forms.CharField(max_length=4000, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':40}))
	request_a_call_back = forms.DateTimeField(required=False, input_formats=['%d/%m/%Y %H:%M'])

	
class TestForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(TestForm, self).__init__(*args, **kwargs)
		self.fields['chemical_system_treatment'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(brand='Applicable for All', user = 6, component_type = 'Chemical System Treatment').order_by('brand').only('component_name')] + [('Other','Other')])
		# self.fields['fuel_supply_length'] = forms.MultipleChoiceField(required = False, choices=[(component.component_name,component.component_name) for component in ProductComponent.objects.filter(brand='Applicable for All', user = 6, component_type = 'Fuel Supply Length').order_by('-component_name').only('component_name')])
		self.fields['scaffolding_required'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(brand='Applicable for All', user = 6, component_type = 'Scaffolding').order_by('-component_name').only('component_name')] + [('Other','Other')])
		self.fields['parking_requirements'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(brand='Applicable for All', user = 6, component_type = 'Parking').order_by('brand').only('component_name')] + [('Other','Other')])
		self.fields['central_heating_system_filter'] = forms.ChoiceField(choices=[('','Select One')] + [(component.component_name,component.component_name) for component in ProductComponent.objects.filter(brand='Applicable for All', user = 6, component_type = 'Central Heating System Filter').order_by('brand').only('component_name')] + [('Other','Other')])

		for field in self: 
			field.field.widget.attrs['class'] = 'form-control'

class EngineerPhotoForm(forms.Form):
    engineer_photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))











	
	





