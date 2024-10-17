#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SYNOPSIS
    forest_condition_variable_bounds_extraction.py -i <file_path> -u <file_path> -l <file_path> -o <folder_path>
    -n <variable_name> -e <file_path> -d -x [-v,--verbose] [-h,--help] [--version]

DESCRIPTION
    This script extracts the forest condition variable values for the references areas representing the lower and
    upper bounds for the rescaling of the forest condition variable to an indicator.
    The script directly outputs the LUT of the bounds of the variable for all forest ecosystem types.
    NOTE: since not all forest ecosystem types have enough reference areas - a manual editing is needed!!!!!
          see Maes et al. (2023) article for more info which forest ecosystem types have to inherit the bounds of
          another ecosystem type.
    NOTE2: with the parameter d you can dump all the raw data per ecosystem type to do own calculations.
    NOTE3: use the -x parameter if you want to overrule some LUT results as described in Maes et al. (2023)

PREREQUISITES
    Python => 3.10.12

EXAMPLES
    python3 forest_condition_variable_bounds_extraction.py -i 'Copernicus_FCOVER_annual-mean_year2000.tif'
    -u 'forest-condition_upper-bounds-reference-areas_year2000_EPSG3035.tif'
    -l 'forest-condition_lower-bounds-reference-areas_year2000_EPSG3035.tif'
    -e 'forest_ecosystem_types_maes-article_LUT.csv' -o 'c:/TEMP' -n 'FCOVER'

EXIT STATUS
    Ctrl-C  =  cancel the script at any time

AUTHOR
    Dr. Marcel Buchhorn <marcel.buchhorn@vito.be>

VERSION
    1.2 (2023-12-13)
"""


##### IMPORT
import os
import rasterio
import numpy as np
from tqdm import tqdm
from datetime import datetime
import time
import math
import optparse
import pandas as pd
import csv

##### CONSTANT
block_shape = (1024, 1024)


##### FUNCTIONS
def parse_args():
    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()['__doc__'],
                                   version="%prog v1.2")
    parser.add_option('-v', '--verbose', action='store_true', default=False, help='verbose output')
    parser.add_option('-i', '--path_var', help='Path to raster data of forest condition variable.',
                      dest='path_var')
    parser.add_option('-o', '--path_out', help='Path to output folder.', dest='path_out')
    parser.add_option('-l', '--path_lower', help='Path to raster file with lower ref areas.', dest='path_lower')
    parser.add_option('-u', '--path_upper', help='Path to raster file with upper ref areas.', dest='path_upper')
    parser.add_option('-n', '--name', help='Path to output folder.', dest='var_name')
    parser.add_option('-e', '--eco_lut', help='Path to LUT of forest ecosystem types.', dest='path_eco_lut')
    parser.add_option('-d', '--dump', action='store_true', default=False, help='dump the variable data per eco')
    parser.add_option('-x', '--overrule', action='store_true', default=False, help='overrule LUT results as '
                                                                                   'described in Maes article for '
                                                                                   'three biogeographic regions')

    # parse the given system arguments
    (options, args) = parser.parse_args()
    # do checks on the parsed options
    if (not options.path_var) or (not os.path.isfile(os.path.normpath(options.path_var))):
        parser.error("the -i argument for input data is missing or the given path doesn't exist!!!")
    if (not options.path_lower) or (not os.path.isfile(os.path.normpath(options.path_lower))):
        parser.error("the -l argument for lower ref areas is missing or the given path doesn't exist!!!")
    if (not options.path_upper) or (not os.path.isfile(os.path.normpath(options.path_upper))):
        parser.error("the -u argument for upper ref areas is missing or the given path doesn't exist!!!")
    if (not options.path_eco_lut) or (not os.path.isfile(os.path.normpath(options.path_eco_lut))):
        parser.error("the -e argument for LUT ecosystem types is missing or the given path doesn't exist!!!")
    if not options.var_name:
        parser.error("the -n argument for naming the forest condition variable is missing!!!")

    if len(args) != 0:
        parser.error('too many arguments')

    return options


def block_window_generator(block_shapes, img_height, img_width):
    """Return an iterator over a band's block windows and their indexes.

    Block windows are tuples::

        ((row_start, row_stop), (col_start, col_stop))

    For example, ``((0, 2), (0, 2))`` defines a 2 x 2 block at the upper
    left corner of the raster dataset.
    This iterator yields blocks "left to right" and "top to bottom"
    and is similar to Python's ``enumerate()`` in that it also returns
    indexes.
    Main change to default rasterio function is that you can define
    your own block_shape!!!
    """
    # get block_height and block_width separately
    block_h, block_w = block_shapes
    # calculate number of block in row and column to process
    d, m = divmod(img_height, block_h)
    nrows = d + int(m > 0)
    d, m = divmod(img_width, block_w)
    ncols = d + int(m > 0)
    # start generation of windows
    for j in range(nrows):
        # get row_start
        row_start = j * block_h
        # correct block_height if we at end of image
        block_h_corr = min(block_h, img_height - row_start)
        for i in range(ncols):
            # get col_start
            col_start = i * block_w
            # correct block_width if we at end of image
            block_width_corr = min(block_w, img_width - col_start)
            # generate final window and yield result
            yield (j, i), ((row_start, row_start + block_h_corr), (col_start, col_start + block_width_corr))


def pre_checks(options):
    """ check if all input raster match in extent, resolution and EPSG

    :param options: parsed sys arguments
    """
    with rasterio.open(options.path_var) as src:
        var_profile = src.profile
    with rasterio.open(options.path_upper) as src:
        upper_profile = src.profile
    with rasterio.open(options.path_lower) as src:
        lower_profile = src.profile

    if not (var_profile['crs'] == upper_profile['crs'] == lower_profile['crs']):
        raise AssertionError(
            'the forest condition variable and ref areas for lower and upper bounds have not the same EPSG.')

    if not (var_profile['transform'] == upper_profile['transform'] == lower_profile['transform']):
        raise AssertionError('the resolution and/or starting coordinate of the rasters is not the same.')

    if not (var_profile['height'] == upper_profile['height'] == lower_profile['height']):
        raise AssertionError('the dataset height of the rasters is not the same.')

    if not (var_profile['width'] == upper_profile['width'] == lower_profile['width']):
        raise AssertionError('the dataset width of the rasters is not the same.')
    return var_profile['dtype']


def data_extraction(options, var_dtype, eco_list):
    """ data extractor

    :param options: phased system arguments
    :param var_dtype: dtype of the input variable dataset
    :param eco_list: list of the forest ecosystem types to process (list of raster values representation)
    :return: dictionaries with extracted data (key: eco id, value: numpy array with all values of ref areas)
    """
    # create the dict entries to store the arrays
    dict_statistics_upper = {key: np.empty(shape=(0,), dtype=var_dtype) for key in eco_list}
    dict_statistics_lower = {key: np.empty(shape=(0,), dtype=var_dtype) for key in eco_list}

    # open the needed input files
    with rasterio.open(os.path.normpath(options.path_var)) as src_var, \
            rasterio.open(os.path.normpath(options.path_lower)) as src_lower,\
            rasterio.open(os.path.normpath(options.path_upper)) as src_upper:

        ##some stuff for progress bar
        max_counter = math.ceil(src_var.height * 1.0 / block_shape[0]) * math.ceil(
            src_var.width * 1.0 / block_shape[1])
        # ini tqdm
        t_inner = tqdm(total=int(max_counter), desc='data extraction', colour='GREEN')

        # now iterate over the blocks of src files and process
        for index, window in block_window_generator(block_shape, src_var.height, src_var.width):
            var_nodata = src_var.nodata

            # load the needed data of block
            # need a fix due to issues with nan as nodata value - not the most elegant way but fast
            if np.isnan(var_nodata):
                aData = src_var.read(1, window=window, masked=True)
                aData = aData.filled(fill_value=-99999)
                var_nodata = -99999
            else:
                aData = src_var.read(1, window=window)
            aUpper = src_upper.read(1, window=window)
            aLower = src_lower.read(1, window=window)

            # shortcut
            if (aData == var_nodata).all():
                t_inner.update()
                continue

            # get a list of which eco we have to handle in this block... speeds it up a little bit
            pList = list(set(np.unique(aLower).tolist() + np.unique(aUpper).tolist()))
            if 0 in pList:
                pList.remove(0)

            # shortcut 2
            if len(pList) == 0:
                t_inner.update()
                continue

            # loop over the ecosystems to extract data in block
            for element in pList:
                dict_statistics_lower[element] = np.append(dict_statistics_lower[element],
                                                           aData[(aLower == element) & (aData != var_nodata)])
                dict_statistics_upper[element] = np.append(dict_statistics_upper[element],
                                                           aData[(aUpper == element) & (aData != var_nodata)])

            # free space
            aData = None
            aLower = None
            aUpper = None

            # update inner progressbar
            t_inner.update()
        # close the inner progressbar
        t_inner.close()
    return dict_statistics_upper, dict_statistics_lower


def dump_it(options, eco_list, dict_eco, dict_statistics_upper, dict_statistics_lower, df_LUT):
    """ dump results to disk

    :param options: phased sys arguments
    :param eco_list: list of the forest ecosystem types to process (list of raster values representation)
    :param dict_eco: dict ecosystem clear name to raster value (two-way-dict)
    :param dict_statistics_upper: dictionaries with extracted data (key: eco id, value: numpy array with all values of
                                   upper ref areas)
    :param dict_statistics_lower: dictionaries with extracted data (key: eco id, value: numpy array with all values of
                                   lower ref areas)
    """
    path_output = os.path.join(os.path.normpath(options.path_out),
                               f'LUT_forest-condition_variable-{options.var_name}_scaling-bounds.csv')
    # create sub-folder structure
    os.makedirs(os.path.dirname(path_output), exist_ok=True)
    # dump
    df_LUT.to_csv(path_or_buf=path_output, index=True)
    print(f'** LUT for forest condition variable {options.var_name} is saved here: {path_output}')

    # as wished by BC3 also dump all raw data
    path_out_upper = os.path.join(os.path.normpath(options.path_out),
                                  f'data-dump_condition-variable-{options.var_name}_upper-bounds.csv')

    if options.dump:
        print('* dump for BC3 also all variable values to CSV per forest ecosystem type (needs some time)')
        t_dump1 = tqdm(total=int(df_LUT.shape[0]), desc='dump upper', colour='YELLOW')

        with open(path_out_upper, 'w', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_NONNUMERIC)

            for eco in eco_list:
                wr.writerow([dict_eco[eco]] + dict_statistics_upper[eco].tolist())
                t_dump1.update()
        t_dump1.close()

        t_dump2 = tqdm(total=int(df_LUT.shape[0]), desc='dump lower', colour='BLUE')
        path_out_lower = os.path.join(os.path.normpath(options.path_out),
                                      f'data-dump_condition-variable-{options.var_name}_lower-bounds.csv')

        with open(path_out_lower, 'w', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_NONNUMERIC)

            for eco in eco_list:
                wr.writerow([dict_eco[eco]] + dict_statistics_lower[eco].tolist())
                t_dump2.update()
        t_dump2.close()


############## MAIN ###################################
def main():
    start_time = time.time()
    # parse the system arguments
    options = parse_args()

    # change umask driver to make sure we have the correct disk rights
    try:
        old_umask = os.umask(0o000)
    except Exception:
        print('Could not change UMASK setting')
        pass

    ##### MAIN
    print(f'Welcome to forest condition {options.var_name} variable data extractor for given reference areas')

    # run some checks
    var_dtype = pre_checks(options)

    # load LUT
    df_LUT = pd.read_csv(os.path.normpath(options.path_eco_lut))
    # list of ecosystem types to process
    eco_list = df_LUT.id.to_list()

    print('* start extraction of variable values for upper and lower ref areas')
    dict_statistics_upper, dict_statistics_lower = data_extraction(options, var_dtype, eco_list)

    # now we consolitate the results
    print(f'* calculate the percentiles to define the {options.var_name} upper & lower bounds per ecosystem type')
    df_LUT.set_index('forest_eco', inplace=True)
    df_LUT[f'{options.var_name}_upper'] = np.nan
    df_LUT[f'{options.var_name}_lower'] = np.nan

    # create a dict of eco clear name to raster value
    dict_eco = df_LUT['id'].to_dict()
    dict_eco.update({item[1]: item[0] for item in dict_eco.items()})

    # loop over the ecoststemtypes
    t_outer = tqdm(total=int(df_LUT.shape[0]), desc='bounds calc', colour='RED')
    for eco in eco_list:
        # 98 percentile for upper
        if not dict_statistics_upper[eco].size == 0:
            df_LUT.loc[dict_eco[eco], f'{options.var_name}_upper'] = np.percentile(dict_statistics_upper[eco], 98)

        # 2 percentile for lower
        if not dict_statistics_lower[eco].size == 0:
            df_LUT.loc[dict_eco[eco], f'{options.var_name}_lower'] = np.percentile(dict_statistics_lower[eco], 2)
        t_outer.update()
    t_outer.close()

    # some overruling
    if options.overrule:
        df_LUT.loc['BLF_ARC', f'{options.var_name}_upper'] = df_LUT.loc['BLF_ALS', f'{options.var_name}_upper']
        df_LUT.loc['CFF_ARC', f'{options.var_name}_upper'] = df_LUT.loc['CFF_ALS', f'{options.var_name}_upper']
        df_LUT.loc['MXF_ARC', f'{options.var_name}_upper'] = df_LUT.loc['MXF_ALS', f'{options.var_name}_upper']
        df_LUT.loc['TWS_ARC', f'{options.var_name}_upper'] = df_LUT.loc['TWS_ALS', f'{options.var_name}_upper']

        #df_LUT.loc['BLF_BLS', f'{options.var_name}_upper'] = df_LUT.loc['BLF_PAN', f'{options.var_name}_upper']
        df_LUT.loc['CFF_BLS', f'{options.var_name}_upper'] = df_LUT.loc['CFF_PAN', f'{options.var_name}_upper']
        df_LUT.loc['MXF_BLS', f'{options.var_name}_upper'] = df_LUT.loc['MXF_PAN', f'{options.var_name}_upper']
        df_LUT.loc['TWS_BLS', f'{options.var_name}_upper'] = df_LUT.loc['TWS_PAN', f'{options.var_name}_upper']

        #df_LUT.loc['BLF_STE', f'{options.var_name}_upper'] = df_LUT.loc['BLF_PAN', f'{options.var_name}_upper']
        df_LUT.loc['CFF_STE', f'{options.var_name}_upper'] = df_LUT.loc['CFF_PAN', f'{options.var_name}_upper']
        df_LUT.loc['MXF_STE', f'{options.var_name}_upper'] = df_LUT.loc['MXF_PAN', f'{options.var_name}_upper']
        df_LUT.loc['TWS_STE', f'{options.var_name}_upper'] = df_LUT.loc['TWS_PAN', f'{options.var_name}_upper']


    # dump the results
    print('* write results to disk')
    dump_it(options, eco_list, dict_eco, dict_statistics_upper, dict_statistics_lower, df_LUT)

    print('All processing successfully done. Have a nice day.')

    # set umask to old settings
    try:
        os.umask(old_umask)
    except Exception:
        print('!!! Could not change UMASK setting back!!!')
        pass

    print('---------------------------')
    print('TOTAL TIME IN MINUTES: {0:0.1f}'.format((time.time() - start_time) / 60))
    print('END OF MODULE: forest condition variable extraction')


if __name__ == '__main__':
    main()
