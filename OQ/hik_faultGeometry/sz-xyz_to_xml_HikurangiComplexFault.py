# -*- coding: utf-8 -*-
"""
Spyder Editor

"""

# -*- coding: utf-8 -*-
"""
Modified on 11 Sept

Must have unzipped file. .xyz files must contain contours (lon, lat, depth)

@author: abbott
"""
"""
Functions to read in specific xyz sz contour info to create xml complex geom for
the subduction zone in OpenQuake. Data must be in format: Lon, Lat, depth.

Only works for one source at a time right now
"""
#%%
import os
from lxml import etree
import pandas as pd
from shapely.geometry import Polygon, Point

# os.chdir('F:\Dropbox\Work\Repository\Hikurangi_mhzrd\OQ\hik_faultGeometry')
os.chdir('/Users/alex/Dropbox/Work/Repository/Hikurangi_mhzrd/OQ/hik_faultGeometry')

sz = 'hik'
in_directory = '../for_liz2'
out_directory = '.'
contour_differentiator = 'current' #'current'
out_file = sz + '-' + contour_differentiator + '-revised_geom_Alex' +'.xml'

#%%
#sz parameters by 2010 segment:
hik_attr = ['aValue', 'bValue', 'minMag', 'maxMag', 'topDep', 'bottomDep', 'cornerpoints']
# a_value, b_value, minMag, maxMag, mag, occur_rate, lon/lat/dep cornerpoints list (upper north, upper south, lower north, lower south)
hik_src = ['Interface']
hik_dict = {'Interface': [0.4, 0.7, 6.5, 9.0, 4, 50, [(179.735, -37.713), (175.388, -42.118), (178.657, -37.060), (174.240, -41.464)]]}


hik_df = pd.DataFrame(hik_dict, index=hik_attr)

#declare variables
depth_list = []
file_list = []
sorted_file_list = []

#%%
def splitFile(entry):

    return entry.split('_')

def readDirectory(in_directory, contour_differentiator):
    '''
    reads files in directory, uses differentiator (current, high, low) to
    search for appropriate contour files and record the depths that each file
    represents
    '''
    for entry in os.listdir(in_directory):
        split_file = splitFile(entry)
        if len(split_file) >= 3:
            if split_file[2] == 'contours.txt' and(split_file[1] == contour_differentiator):
                depth = -1*float(split_file[3])
                if depth not in depth_list: depth_list.append(depth)
                depth_list.sort() # sort from shallow to deep
                file_list.append(entry)
        else: pass


    return depth_list, file_list

def fileListByDepth(in_directory, depth_list, file_list):
    '''
    uses depth list and list of appropriate files to order the files from
    shallowest to deepest depth
    '''
    for val in depth_list:
        for entry in file_list:

            if float(splitFile(entry)[3]) == -1*val:
                sorted_file_list.append(entry)

    return sorted_file_list

def createSZdict(sorted_file_list, depth_list):
    """
	Function to read contour files from directory and write into
    dictionary with depth as the key, and lon, lat pairs as values.

	INPUT: location of files, filetype
	OUTPUT: lists of params
    """

    sz_conts_dict = {}
    for val in depth_list:
        sz_contour_locs = []
        for file in sorted_file_list:
            if float(splitFile(file)[3]) == -1*val:
                with open ((in_directory + '/' + file), newline='') as contfile:

                    for line in contfile:
                        row = line.split()

                        if val == -1*float(row[2]):
                            sz_contour_locs.append(createVal(row))
                            sz_contour_locs.sort(key=lambda x:x[1]) #order list by latitude
                        else: raise Exception("depth in file dne depth in filename")

        # convert list of tuples to list: https://www.geeksforgeeks.org/python-convert-list-of-tuples-into-list/
        sz_contour_locs_list = [item for t in sz_contour_locs for item in t]
        # make everything in list floats: https://stackoverflow.com/questions/1614236/in-python-how-do-i-convert-all-of-the-items-in-a-list-to-floats
        sz_contour_locs_list = [float(i) for i in sz_contour_locs_list]
        # add to dictionary under depth value key
        sz_conts_dict[val] = sz_contour_locs_list

    return sz_conts_dict

def createVal(row):
    lon = row[0]
    lat = row[1]
    row_loc = (lon,lat)
    return row_loc

def insertDepths(topCoords, depth):
    clipped_cont = []
    for item in topCoords:
        clipped_cont.append(item[0])
        clipped_cont.append(item[1])
        clipped_cont.append(depth)

    return clipped_cont

def hikSources(hik_df, sz_conts_dict, hik_src):
    '''
    Only works for 1 source at a time.
    '''

    hik_cont_dict = {}

    for key in sz_conts_dict:

        hik_cont_list=[0]* hik_df.shape[1]
        count = 0

        for col in hik_df:
            src_cont_list = []

            hik_poly = Polygon(hik_df.loc['cornerpoints', col])

            it = iter(sz_conts_dict[key])

            for x in it:
                point = (x, next(it))
                test_point = Point(point)
                if test_point.within(hik_poly): #.contains(test_point):
                    src_cont_list.append(point)
            hik_cont_list[count] = src_cont_list
            count += 1

        hik_cont_dict[key] = hik_cont_list

    hik_cont_df = pd.DataFrame(hik_cont_dict, index=hik_src)

    return hik_df.append(hik_cont_df.transpose(), sort=True)

def src2nrml(sz, hik_df, depth_list, out_file):

    """
    Function to take params read into dict from csv and returns
    site model file in xml
    INPUT: site parameters lists
    OUTPUT: nrml site model file
    """

    # Some XML definitions
    NAMESPACE = 'http://openquake.org/xmlns/nrml/0.4'
    GML_NAMESPACE = 'http://www.opengis.net/gml'
    SERIALIZE_NS_MAP = {None: NAMESPACE, 'gml': GML_NAMESPACE}
    gml_ns = SERIALIZE_NS_MAP['gml']

    # Head matter
    root = etree.Element(_tag='nrml', nsmap={'gml': 'http://www.opengis.net/gml'})
    root.set('xmlns', 'http://openquake.org/xmlns/nrml/0.4')
    root.append(etree.Comment('%s' % sz + ' sz sources from contour files'))

    # Define Source Model Name
    sMod = etree.SubElement(root, "sourceModel")
    sMod.set('name', 'Seismic Source Model')
    j = 0 # source id counter
    i = 0 # will eventually need to iterate through cols in dataframe

    for col in hik_df:
        #create list that says whether contour is empty or not
        notempty = [True]*len(depth_list)
        for ix in range(0,len(depth_list)):
            if not hik_df.loc[depth_list[ix]][i]:
                notempty[ix] = False
                if ix != 0 and notempty[ix -1]:
                    bottom_ix = ix-1

        if True not in notempty:
            print("PROBLEM - need to skip & throw exception eventually")
        else:
            top_ix = notempty.index(True)
        if False not in notempty:
            bottom_ix = len(depth_list)

        if top_ix == bottom_ix: print(hik_df.columns.values[i])

        # Define Fault Source Type
        fS = etree.SubElement(sMod, "complexFaultSource")
        fS.set('id', '%s' % str(j))
        j+=1
        #fS.set('name', '%s' % faultData[i][0])
        fS.set('name', '%s' % sz + str(hik_df.columns.values[i]))
        #fS.set('tectonicRegion', '%s' % faultData[i][1])
        fS.set('tectonicRegion', '%s' % 'Subduction Interface')

        # fault geometry
        cfbe = etree.SubElement(fS, 'complexFaultGeometry')

        # top edge
        cfte = etree.SubElement(cfbe, 'faultTopEdge')
        gmlLS = etree.SubElement(cfte, '{%s}LineString' % gml_ns)
        gmlPos = etree.SubElement(gmlLS, '{%s}posList' % gml_ns)

        topCoords = hik_df.loc[depth_list[top_ix]][i]
        top_cont = insertDepths(topCoords, depth_list[top_ix])
        gmlPos.text = ' '.join([str("%.3f" % x) for x in top_cont])


        # intermediate edges
        for d in depth_list[top_ix+1:bottom_ix]:
            cfie = etree.SubElement(cfbe, 'intermediateEdge')
            gmlLS = etree.SubElement(cfie, '{%s}LineString' % gml_ns)
            gmlPos = etree.SubElement(gmlLS, '{%s}posList' % gml_ns)
            intCoords = hik_df.loc[d][i]
            int_cont = insertDepths(intCoords, d)
            gmlPos.text = ' '.join([str("%.3f" % x) for x in int_cont])

        # bottom edge
        cfbe = etree.SubElement(cfbe, 'faultBottomEdge')
        gmlLS = etree.SubElement(cfbe, '{%s}LineString' % gml_ns)
        gmlPos = etree.SubElement(gmlLS, '{%s}posList' % gml_ns)
        bottomCoords = hik_df.loc[depth_list[bottom_ix]][i]
        bot_cont = insertDepths(bottomCoords, depth_list[bottom_ix])
        gmlPos.text = ' '.join([str("%.3f" % x) for x in bot_cont])

        # complex fault parameters:
            # MSR mag scaleRel
            # RAR = rupture aspect ratio
            # TGR = truncated Guntenberg Richter parameters
            # rake
        MSR= etree.SubElement(fS, 'magScaleRel')
        MSR.text = 'WC1994'

        RAR= etree.SubElement(fS, 'ruptAspectRatio')
        RAR.text = '%s' % 1.5

        TGR = etree.SubElement(fS, 'truncGutenbergRichterMFD')
        TGR.set('aValue', '%s' % hik_df.loc['aValue'][i])
        TGR.set('bValue', '%s' % hik_df.loc['bValue'][i])
        TGR.set('minMag', '%s' % hik_df.loc['minMag'][i])
        TGR.set('maxMag', '%s' % hik_df.loc['maxMag'][i])
        rake = etree.SubElement(fS, 'rake')
        rake.text = '%s' % 30

        i += 1
    # Form Tree and Write to XML
    root_tree = etree.ElementTree(root)

    nrml_file = open(out_file, 'wb')
    root_tree.write(nrml_file, encoding="utf-8", xml_declaration=True, pretty_print=True)

#%%
if __name__ == "__main__":

    depth_list, file_list = readDirectory(in_directory, contour_differentiator)
    sorted_file_list = fileListByDepth(in_directory, depth_list, file_list)
    sz_conts_dict = createSZdict(sorted_file_list, depth_list)
    hik_df = hikSources(hik_df, sz_conts_dict, hik_src)

    src2nrml(sz, hik_df, depth_list, out_file)

    print("finished!")

# %%
