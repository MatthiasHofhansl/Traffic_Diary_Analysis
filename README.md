# Traffic_Diary_Analysis_Tool




## Descriptionss
The **Traffic_Diary_Analysis_Tool** is a Python-based program designed to save and analyze travel routes taken by individuals. Users can input details about their journeys, such as:

- **Start Time** and **End Time**
- **Start Point** and **End Point** (using coordinates obtained from Mapbox Geocoder)
- **Mode of Transport** (selectable via a dropdown list)
- **Purpose of Travel** (selectable via a dropdown list)
- **Participant Name** (selectable via a dropdown list with the option to create a new name; every name has an own ID)

The data is stored and, upon completion, users can generate graphical analyses using **Matplotlib**.

## Features
- **Data Entry**: Input journey details with an intuitive user interface.
- **Dropdown Selection**: Choose transportation modes from a predefined list.
- **Coordinate Integration**: Fetch geographical coordinates via the Mapbox Geocoder API.
- **Data Storage**: Save entered journeys for future analysis.
- **Visual Analysis**: Generate insightful diagrams and visualizations using Matplotlib.

## Usage
1. Run the main program
2. Follow the prompts to input journey details:
   - Start and end times
   - Start and end points (Are turned into coordinates from Mapbox Geocoder)
   - Mode of transportation (selectable via a dropdown list)
   - Purpose of travel (selectable via a dropdown list)
   - Name (selectable via a dropdown list with the option to create a new name; every name has an own ID)
3. Once all data is entered, click the **Evaluate** button.
4. Visualizations and analysis results will be displayed as charts.

### Authors
**Paul Rösch** **Matthias Hofhansl**