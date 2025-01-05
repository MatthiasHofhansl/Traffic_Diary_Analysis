# Traffic_Diary_Analysis_Tool

## Descriptions
The **Traffic_Diary_Analysis_Tool** is a Python-based program designed to save and analyze travel routes taken by individuals. Users can input details about their journeys, such as:

- **Start Time** and **End Time**
- **Start Point** and **End Point** (using coordinates obtained from Mapbox Geocoder)
- **Mode of Transport** (selectable via a dropdown list)
- **Purpose of Travel** (selectable via a dropdown list)
- **Participant Name** (selectable via a dropdown list with the option to create a new name; every name has an own ID)

The collected data can be reviewed in simple charts.

## Features
- **Data Entry**: Input journey details with an intuitive user interface.
- **Dropdown Selection**: Choose transportation modes and purpose of travel from a predefined list.
- **Coordinate Integration**: Fetch geographical coordinates via the Mapbox Geocoder API.
- **Data Storage**: Save entered journeys for future analysis.
- **Visual Analysis**: Generate insightful charts using Matplotlib.

## Additional Features
- **Tooltips**: Helping users to choose from transportation modes and purpose of travel from a predefined list.
- **graphical map**: Giving users the possibility to type in a specific location or to choose from a map by placing a marker 

## Usage
1. Run the main program
2. Follow the prompts to input journey details:
   - Name (selectable via a dropdown list with the option to create a new name)
   - Start and end dates
   - Start and end times
   - Start and end points (Are turned into coordinates from Mapbox Geocoder)
   - Mode of transportation (selectable via a dropdown list)
   - Purpose of travel (selectable via a dropdown list)
3. Once all data is entered, click the **Evaluate now** button.
4. Visualizations and analysis results will be displayed as charts.

### Authors
**Paul Rösch** **Matthias Hofhansl**