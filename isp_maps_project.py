"""
Project for Week 4 of "Python Data Visualization".
Unify data via common country codes.

Be sure to read the project description page for further information
about the expected behavior of the program.
"""

import csv
import math
import pygal

def read_csv_as_nested_dict(filename, keyfield, separator, quote):
    """
    Inputs:
      filename  - name of CSV file
      keyfield  - field to use as key for rows
      separator - character that separates fields
      quote     - character used to optionally quote fields
    Output:
      Returns a dictionary of dictionaries where the outer dictionary
      maps the value in the key_field to the corresponding row in the
      CSV file.  The inner dictionaries map the field names to the
      field values for that row.
    """
    with open(filename, "rt", newline="") as file:
        dictreader = csv.DictReader(file, delimiter=separator, quotechar=quote)
        dict_dict = {}
        for row in dictreader:
            dict_dict[row[keyfield]] = row
        return dict_dict

def build_country_code_converter(codeinfo):
    """
    Inputs:
      codeinfo      - A country code information dictionary

    Output:
      A dictionary whose keys are plot country codes and values
      are world bank country codes, where the code fields in the
      code file are specified in codeinfo.
    """
    code_table = read_csv_as_nested_dict(codeinfo["codefile"],
                                         codeinfo["plot_codes"],
                                         codeinfo["separator"],
                                         codeinfo["quote"])
    code_dict = {}
    for country in code_table:
        data_code = code_table[country][codeinfo["data_codes"]]
        code_dict[country] = data_code
    return code_dict

# info2 = {"codefile" : "isp_code_csv_files/code2.csv", "quote" : "\'",
#          "separator" : ",", "plot_codes" : "Code1", "data_codes" : "Code2"}
# # print(build_country_code_converter(info1))
# pygal_countries = pygal.maps.world.COUNTRIES
#
# gdp1 = {"ABC" :[1,2,3,4,5,6],
# "GHI": [10,11,12,13,14,15]}
# #}

def reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries):
    """
    Inputs:
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      gdp_countries  - Dictionary whose keys are country codes used in GDP data

    Output:
      A tuple containing a dictionary and a set.  The dictionary maps
      country codes from plot_countries to country codes from
      gdp_countries.  The set contains the country codes from
      plot_countries that did not have a country with a corresponding
      code in gdp_countries.

      Note that all codes should be compared in a case-insensitive
      way.  However, the returned dictionary and set should include
      the codes with the exact same case as they have in
      plot_countries and gdp_countries.
    """
    ctry_dict = build_country_code_converter(codeinfo)
    shared_ctr = {}
    plot_countries_only = set()
    gdp_countries_codes_up = {code.upper(): code for code in gdp_countries}
    ctry_dict_up = {code.upper(): ctry_dict[code].upper() for code in ctry_dict}
    for code in plot_countries:
        code_up = code.upper()
        if code_up in ctry_dict_up:
            if ctry_dict_up[code_up] in gdp_countries_codes_up:
                shared_ctr[code] = gdp_countries_codes_up[ctry_dict_up[code_up]]
            else:
                plot_countries_only.add(code)
        else:
            plot_countries_only.add(code)

    return (shared_ctr, plot_countries_only)


def build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year for which to create GDP mapping

    Output:
      A tuple containing a dictionary and two sets.  The dictionary
      maps country codes from plot_countries to the log (base 10) of
      the GDP value for that country in the specified year.  The first
      set contains the country codes from plot_countries that were not
      found in the GDP data file.  The second set contains the country
      codes from plot_countries that were found in the GDP data file, but
      have no GDP data for the specified year.
    """


    gdp_dict = read_csv_as_nested_dict(gdpinfo["gdpfile"],
                                       gdpinfo["country_code"],
                                       gdpinfo["separator"],
                                       gdpinfo["quote"]
                                       )

    code_to_code, absent_countries = reconcile_countries_by_code(codeinfo,
                                                                 plot_countries,
                                                                 gdp_dict)
    gdp_info_year_name = {}
    countries_absent_year = set()

    for code in code_to_code:
        gdpcode = code_to_code[code]
        if gdp_dict[gdpcode][year] != "":
            gdp = float(gdp_dict[gdpcode][year])
            gdp_info_year_name[code] = math.log(gdp, 10)
        else:
            countries_absent_year.add(code)

    return (gdp_info_year_name, absent_countries, countries_absent_year)

# build_map_dict_by_code({'gdpfile': 'gdptable1.csv', 'separator': ',',
#                         'quote': '"', 'min_year': 2000, 'max_year': 2005,
#                         'country_name': 'Country Name', 'country_code': 'Code'},
#                        {'codefile': 'code2.csv', 'separator': ',', 'quote': "'",
#                         'plot_codes': 'Cd2', 'data_codes': 'Cd3'},
#                        {'C1': 'c1', 'C2': 'c2', 'C3': 'c3',
#                         'C4': 'c4', 'C5': 'c5'},
#                        '2001')
def render_world_map(gdpinfo, codeinfo, plot_countries, year, map_file):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year of data
      map_file       - String that is the output map file name

    Output:
      Returns None.

    Action:
      Creates a world map plot of the GDP data in gdp_mapping and outputs
      it to a file named by svg_filename.
    """
    data_dict, not_in, not_in_year = build_map_dict_by_code(gdpinfo, codeinfo,
                                                            plot_countries,
                                                            year)
    worldmap_gdp = pygal.maps.world.World()
    worldmap_gdp.add("GDP data", data_dict)
    worldmap_gdp.add("Not in GDP Data", not_in)
    worldmap_gdp.add("No {} Info".format(year), not_in_year)
    worldmap_gdp.render_to_file(map_file)



def test_render_world_map():
    """
    Test the project code for several years
    """
    gdpinfo = {
        "gdpfile": "isp_gdp.csv",
        "separator": ",",
        "quote": '"',
        "min_year": 1960,
        "max_year": 2015,
        "country_name": "Country Name",
        "country_code": "Country Code"
    }

    codeinfo = {
        "codefile": "isp_country_codes.csv",
        "separator": ",",
        "quote": '"',
        "plot_codes": "ISO3166-1-Alpha-2",
        "data_codes": "ISO3166-1-Alpha-3"
    }

    # Get pygal country code map
    pygal_countries = pygal.maps.world.COUNTRIES

    # 1960
    render_world_map(gdpinfo, codeinfo, pygal_countries, "1960", "isp_gdp_world_code_1960.svg")

    # 1980
    render_world_map(gdpinfo, codeinfo, pygal_countries, "1980", "isp_gdp_world_code_1980.svg")

    # 2000
    render_world_map(gdpinfo, codeinfo, pygal_countries, "2000", "isp_gdp_world_code_2000.svg")

    # 2010
    render_world_map(gdpinfo, codeinfo, pygal_countries, "2010", "isp_gdp_world_code_2010.svg")


# Make sure the following call to test_render_world_map is commented
# out when submitting to OwlTest/CourseraTest.

#test_render_world_map()
