import requests
import math
import numpy as np
import csv

def get_pairs(filename):
    """(filename.txt) --> list of str

    Returns a list of strings (coordinates) when given a properly formatted file from
    Google Earth route line.
    Note: the coordinates will be in order ['longitude1','latitude1','longitude2','latitude2']

    Precondition:  Original data format must be comma seperated text
    file of latitude and longitude pairs.

    Example:

    Path data copied from Google Earth to a text file usually takes the form:
    
     -110.87521,43.50059,0 -110.87514,43.50059,0 -110.87483,43.50059,
    0 -110.87454,43.50056,0 -110.87443,43.50055,0 etc...

    >>>get_pairs("filename.txt")

    '-110.87521','43.50059','-110.87514','43.50059','-110.87483','43.50059',
    '-110.87454,'43.50056','-110.87443','43.50055' etc...
    """

    #Open The File To Read
    file = open(filename, 'r')
    read = file.read()

    #Accumulators
    no_comma = ''
    no_comma_list = []
    final_string = ''
    combined=[]
    
    #Create List of Strings From All Values (removing extraneous commas)
    for char in read:
       if char != ',':
          no_comma = no_comma + char
       else:
          no_comma_list.append(no_comma)
          no_comma = ''

    #Remove garbage 0 and ' ' characters from pairs list
    for i in range(1,len(no_comma_list)):
        if i%2 == 0:
            no_comma_list[i] = no_comma_list[i][2:]
        else:
            no_comma_list[i] = no_comma_list[i]

    file.close()
    return no_comma_list

def get_long(no_comma_list):
    """(list of str) --> list of floats

    Takes list of coordinates created with get_pairs() and returns
    a list of only the LONGITUDE values as floats

    >>>get_long(['-110.87521','43.50059','-110.87514','43.50059'])
    
    [-110.87521,-110.87514]

    """
    long=[]

    for l in range(1,len(no_comma_list)):
        if l%2 == 0:
            long.append(float(no_comma_list[l]))
            
    #Don't forget to add the first longitude value back
    long.insert(0, float(no_comma_list[0]))

    return long

def get_lat(no_comma_list):
    """(list of str) --> list of floats

    Takes list of coordinates created with get_pairs() and returns
    a list of only the LATITUDE values as floats

    >>>get_lat(['-110.87521','43.50059','-110.87514','43.50059'])
    
    [43.50059,43.50059]

    """

    lat =[]
    
    for n in range(1,len(no_comma_list)):
        if n%2 != 0:
            lat.append(float(no_comma_list[n]))

    return lat

def combine_latlong(lat,long):
    """(list of floats, list of floats) --> list of str

    Returns a combined list of string pairs:
    ['latitude1,longitude1','latitude2,longitude2']
    when arguments are a list of latitude floats and
    a list of longitude floats

    >>>combine_latlong([43.50064,43.50059],[-110.87521,-110.87514])

    ['43.50064,-110.87521','43.50059,-110.87514']

    """
    combined=[]

    for m in range(0,len(long)):
        combined.append((str(lat[m]) + ',' + str(long[m])))
    
    return combined

def format_latlong(one_comma_list):
    """(list of str) --> string

    Creates properly formatted string for use with Google maps API.
    Argument must be a list of coordinate pair strings seperated by a comma.
    Basically just joins the list of string pairs to single a string
    and seperates latitude/longitude pairs with a '|' pipe character.

    >>>format_latlong(['43.50064,-110.87521','43.50059,-110.87514'])

    '43.50064,-110.87521|43.50059,-110.87514'
    """
    
    #Add Required '|' For Proper Google API Upload Format  
    for j in range(0,len(one_comma_list)):
        one_comma_list[j] = one_comma_list[j] + '|'

    #Convert list to string for Proper Google API Upload Format
    final_string = ''.join(one_comma_list)

    #Strip the last '|' pipe character from the string so Google
    #doesn't throw an error
    final_string = final_string[:-1]
    
    return final_string


def get_elevation(YOURAPI,latlong,samples):
    """(str,str,str) --> list of floats
    
    Returns elevation data from Google API based on latitude and longitude values.
    Requires YOUR API KEY (YOURAPI), a properly formatted (latlong) string from the
    format_latlong() function, and an appropriate (samples) value.

    (samples) is a number (in str form) of the amount of elevation values you expect
    back from Google. Expecting 1 sample per latitude/longitude coordinate means Google
    won't do any major interpolating and that your data should be accurate. Google
    places a limit on the amount of samples you're allowed to ask for.  Using str(len(lat))
    for the (samples) argument should give you 1 elevation value per coordinate (a desireable
    result).

    >>>get_elevation('YOUR API KEY','43.50064,-110.87521|43.50059,-110.87514','2')

    [1876.989135742188, 1876.720825195312]
    
    """

    
    payload = {'path':latlong , 'samples': samples , 'key':YOURAPI}
    elev = []

    r = requests.get('https://maps.googleapis.com/maps/api/elevation/json?', params=payload)
    r = r.json()

    for i in r['results']:
        elev.append(i['elevation'])

    return elev



def get_dist_pairs(lat,long):
    """(list of floats, list of floats) --> list of floats

    Returns a list of straight line distances (in meters) between
    adjacent latitude/longitude pairs.  Uses spherical law
    of cosines[See: http://www.movable-type.co.uk/scripts/latlong.html].

    >>>lat = [43.50059,43.50064,45.66609,46.03204]
    >>>long = [-110.87521,-110.87514,-112.93488,114.76894]
    >>>get_dist_pairs(lat,long)

    [7.923543615836835, 290816.0889955098, 8800659.429102872]
    
    """
    R = 6371000 #Radius of the earth in meters

    d =[]
    lat_rad=[]
    long_rad=[]

    for i in range(len(lat)):  #Need to convert degrees to Radians
        lat_rad.append(math.radians(lat[i]))

    for i in range(len(long)): #Need to convert degrees to Radians
        long_rad.append(math.radians(long[i]))

    for i in range(0,len(long)-1): #Spherical Law of Cosines formula
        d.append(math.acos(math.sin(lat_rad[i])*math.sin(lat_rad[i+1]) + math.cos(lat_rad[i])*math.cos(lat_rad[i+1])*math.cos(long_rad[i+1]-long_rad[i]))*R)

    return d

def get_total_dist(dist_pairs):
    """(list of floats) --> list of floats

    Takes each value in dist_pairs and sums all the previous values.
    The result of the fucntion get_dist_pairs() should be used for
    dist_pairs argument.  Purpose is to create a list of distances
    to be used in the .csv file that can become the x axis of a graph.

    >>>get_total_dist([7,4,8])
    [0,7,11,19]
    
    """
    d=[]

    for i in range(0,len(dist_pairs)+1):
        d.append(sum(dist_pairs[:i]))

    return d

def create_csv(csvfile,lat,long,total_dist,elevation):
    """(str, list of floats, list of floats, list of floats, list of floats) --> filename.csv

    Creates a new .csv file in your python directory with 4 columns.
    The file will be named whatever you choose for (csvfile).  Columns
    from left to right will represent latitude, longitude, total_dist
    from first coordinate, and elevation.  Arguments are named for the functions
    that produce properly formatted inputs.

    """

    final_data = []

    final_data.append(lat)
    final_data.append(long)
    final_data.append(total_dist)
    final_data.append(elevation)

    final_data = np.array(final_data) # Using numpy to create an array
    final_data = final_data.T         # for transposing.  Must transpose
                                      # the matrix, otherwise we will get
                                      # 4 rows instead of 4 columns
                                


    with open(csvfile,'w',newline='') as fp:
        e = csv.writer(fp,delimiter=',')
        e.writerows(final_data)

    print('Success! Check for the new .csv file in your python directory.')

    ##END##
