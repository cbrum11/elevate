# For detailed information visit:
# http://github.com/cbrum11/

import elevate_functions

# Enter your specific Google Elevation API Key
key = 'YOUR GOOGLE MAPS ELEVATION API KEY'
# Enter the name of your specific coordinates.txt file
coordinates_file = "Example_Coordinates.txt"
# Enter what you want to call the new .csv file that is
# about to be created
csvfile = "Example.csv"

# Clean up raw file data and get coordinate pairs
pairs = elevate_functions.get_pairs(coordinates_file)
# Get only Latitude values
lat = elevate_functions.get_lat(pairs)
# Get only Longitude values
long = elevate_functions.get_long(pairs)


# Calculate distance between each latitude and longitude pair
dist = elevate_functions.get_dist_pairs(lat,long)

# Sum distances in a way that creates a distances list that will
# become the x axis of a graph
total_dist = elevate_functions.get_total_dist(dist)

# Combines Latitude and Longitude lists into single list that
# pairs them together as coordinates
combined_latlong = elevate_functions.combine_latlong(lat,long)

# Formats Combined Latitude and Longitude list into form
# acceptable to Google Maps elevation API
combined = elevate_functions.format_latlong(combined_latlong)

# Requests Elevation from Google Maps Elevation API
# based on Latitude and Longitude coordinates

sample = str(len(lat)) # Necessary parameter for Google API call.
                       # Tells Google to give 1 elevation value
                       # per each latitude/longitude pair

elevation = elevate_functions.get_elevation(key,combined,sample)

# Combines Latitude, Longitude, Distance, and Elevation data
# and creates a "Graph_Data.csv" file to be
# opened in Excel
new_csv = elevate_functions.create_csv(csvfile,lat,long,total_dist,elevation)

##END##
