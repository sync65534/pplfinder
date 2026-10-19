# pplfinder
Tool to find people in the US via property records 
#
# Usage
(in-line)
```python
import pplfinder
pplfinder.find(first_name="firstname", last_name="lastname", state_filter="Georgia", county_filter="Richmond")
```
(command)
```bash
# First name only
python main.py -f John

# Last name only
python main.py -l Johnson

# Both names
python main.py -b John Johnson

# Search just Georgia
python main.py -b John Johnson --state Georgia

# Search one county
python main.py -b John Johnson --state Georgia --county Richmond

# Use another configuration file
python main.py -f John --county-file /path/to/counties.json

# Disable the progress bar
python main.py -f John -n
```
#
# Workflow and conventions for development
The `county_list.json` file is used to load each `County` object into the program, and is in json formatting for readability in updating. If you or i am to update the file, it must be in the following form
```json
{
    "COUNTY NAME": {
        "state": "STATE ABBREVIATION",
        "data_type": "DATA TYPE",
        "links": [
            "LINKS TO BE INTERPRETED BY THE EXTRACTOR, COORESPONDING TO DATA TYPE"
        ],
        "notes": "ANY NOTES FOR DEVELOPMENT"
    }
}
```
This format ensures coherence and consistency throughout the development of this project.
note abbreviations are as follows
```
LN -> last name
FN -> first name
M -> mandatory
O -> optional
```
#
The `extractions.py` file contains the functions designated for each possible type of data case. Although there are 3200+ counties, they all seem to choose the same couple vendors for their mapping websites, which allows us to generalize the functions to be tailored to the vendor, as opposed to 3000 unqiue functions. In the case that a miscleanoeus or vendorless mapping website is to appear, it will be designated its unique function for extraction only then. All extractor functions are to return a python dict where the found name, if any, is the key, and an associative link to the address is the value. I have yet to find a service that does not provide a unique endpoint for each parcel, but it is possible and will be accounted for in the future.
#
