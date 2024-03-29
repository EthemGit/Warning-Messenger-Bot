from typing import List, Union, Any, Tuple

import requests
import shapely
from fuzzywuzzy import process
import geopy
from geopy.geocoders import Nominatim
from shapely.geometry import Polygon

# District => Kreis
# Place => Ort
# Places are needed for everything besides Covid info
# Districts are needed for Covid info
# Districts' IDs (5 numbers) are shorter than Places' IDs (12 numbers)


_districts_dictionary = {}
"""dictionary district_id : str -> district_name : str """

_places_dictionary = {}
"""dictionary place_id : str -> place_name : str"""

_postal_code_dictionary = {}
"""dictionary postal_code: str -> [place_name : str, district_id : str, polygon_area : list[[float, float]]]"""

_postal_place_dictionary = {}
"""dictionary postal_code: str -> place_name : str"""


def _fill_districts_dict() -> None:
    """
    Fills the _districts_dictionary dictionary with selected infos from
    https://warnung.bund.de/assets/json/converted_corona_kreise.json
    Format: district_id -> district_name
    """
    converted_covid_districts = requests.get('https://warnung.bund.de/assets/json/converted_corona_kreise.json').json()
    for district_id, district_description in converted_covid_districts.items():
        _districts_dictionary[district_id] = district_description["n"]


_fill_districts_dict()


def _fill_places_dict() -> None:
    """
    Fills the _places_dictionary dictionary with selected infos from
    https://www.xrepository.de/api/xrepository/urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs_2021-07-31
    /download/Regionalschl_ssel_2021-07-31.json
    Format: place_id -> place_name
    """
    bevoelkerungsstaat_key = requests.get(
        'https://www.xrepository.de/api/xrepository/urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs_2021-07'
        '-31/download/Regionalschl_ssel_2021-07-31.json').json()
    for area_triple in bevoelkerungsstaat_key['daten']:
        if area_triple[2] is None:
            _places_dictionary[area_triple[0]] = area_triple[1]
        else:
            possible_district_id = area_triple[0][0:5]
            try:
                _districts_dictionary[possible_district_id]
            except KeyError:
                pass
            else:
                _places_dictionary[area_triple[0]] = area_triple[1]


_fill_places_dict()


def _fill_postal_code_dict() -> None:
    """
    Fills the _postal_code_dictionary dictionary with selected infos from
    https://public.opendatasoft.com/api/records/1.0/search/?dataset=georef-germany-postleitzahl&q=&rows=-1
    Format: postal_code : str -> [place_name : str, district_id : str, polygon_area : list[[float, float]]]
    """
    postal_code_table = requests.get(
        'https://public.opendatasoft.com/api/records/1.0/search/?dataset=georef-germany-postleitzahl&q=&rows=-1').json()
    for record in postal_code_table['records']:
        _postal_code_dictionary[record['fields']['plz_code']] = [record['fields']['plz_name'],
                                                                 record['fields']['krs_code'],
                                                                 record['fields']['geometry']['coordinates'][0]]


_fill_postal_code_dict()


def _fill_postal_place_dict() -> None:
    """
    Fills the _postal_name_dictionary dictionary with selected infos from _postal_code_dictionary
    Format: postal_code : str -> place_name : str
    """
    for record in _postal_code_dictionary:
        _postal_place_dictionary[record] = _postal_code_dictionary[record][0]


_fill_postal_place_dict()


def _get_exact_address_from_coordinates(latitude: float, longitude: float) -> Tuple[str, str]:
    geo_loc = Nominatim(user_agent="GetLoc")
    location_name = geo_loc.reverse((latitude, longitude))
    address = location_name.address
    address_as_list = address.split(", ")
    if "kreis" in address_as_list[-4].lower():
        place_name = address_as_list[-5]
    else:
        place_name = address_as_list[-4]
    postal_code = address_as_list[-2]
    return place_name, postal_code


def _get_suggestions_for_place_name(place_name: str, suggestion_limit: int) -> list[dict]:
    """
    Returns a list of dicts {'place_name', 'place_id'} with suggestions for the given place name

    Arguments:
        place_name (str): the given place name
        suggestion_limit (int): limits the number of suggestions to the top x
    Returns:
        similar_places_dicts (list[dict]): list of suggested dicts
    """
    similar_place_names = process.extract(place_name, _places_dictionary, limit=suggestion_limit)
    similar_places_dicts = []
    for place_info in similar_place_names:
        similar_place_dict = {'place_name': place_info[0], 'place_id': place_info[2]}
        similar_places_dicts.append(similar_place_dict)
    return similar_places_dicts


def _get_suggestion_dicts_for_non_covid_place_name(place_name: str, suggestion_limit: int) -> list[dict]:
    """
    Returns a list of dicts {'place_name', 'postal_code'} with suggestions for the given place name

    Arguments:
        place_name (str): the given place name
        suggestion_limit (int): limits the number of suggestions to the top x
    Returns:
        similar_places_dicts (list[dict]): list of suggested dicts
    """
    similar_place_names = process.extract(place_name, _postal_place_dictionary, limit=suggestion_limit)
    similar_places_dicts = []
    for place_info in similar_place_names:
        district_id = _postal_code_dictionary[place_info[2]][1]
        district_name = _districts_dictionary[district_id]
        similar_place_dict = {'place_name': place_info[0], 'postal_code': place_info[2], 'district_id': district_id,
                              'district_name': district_name}
        similar_places_dicts.append(similar_place_dict)
    return similar_places_dicts


def _get_place_dict_suggestions(place_name: str, suggestion_limit: int) -> list[dict]:
    """
    Returns a list of dicts {'place_name', 'place_id', 'district_name', 'district_id'} with suggestions for the given
    place name

    Arguments:
        place_name (str): the given place name
        suggestion_limit (int): limits the number of suggestions to the top x
    Returns:
        place_dict_suggestions (list[dict]): list of suggested dicts
    """
    place_dict_suggestions = _get_suggestions_for_place_name(place_name, suggestion_limit)

    for place in place_dict_suggestions:
        district_id = place['place_id'][0:5]
        place['district_name'] = _districts_dictionary[district_id]
        place['district_id'] = district_id
    return place_dict_suggestions


def _get_suggestions_for_district_name(district_name: str, suggestion_limit: int) -> list[dict]:
    """
    Returns a list of dicts {'district_name', 'district_id'} with suggestions for the given district name

    Arguments:
        district_name (str): the given district name
        suggestion_limit (int): limits the number of suggestions to the top x
    Returns:
        similar_districts_dicts (list[dict]): list of suggested dicts
    """
    similar_district_names = process.extract(district_name, _districts_dictionary, limit=suggestion_limit)
    similar_districts_dicts = []
    for district_info in similar_district_names:
        similar_district_dict = {'district_name': district_info[0], 'district_id': district_info[2]}
        similar_districts_dicts.append(similar_district_dict)
    return similar_districts_dicts


def _get_district_dict_suggestions(district_name: str, suggestion_limit: int) -> list[dict]:
    """
    Returns a list of dicts {'place_name', 'place_id', 'district_name', 'district_id'} with suggestions for the given
    district name

    Arguments:
        district_name (str): the given district name
        suggestion_limit (int): limits the number of suggestions to the top x
    Returns:
        district_dict_suggestions (list[dict]): list of suggested dicts, dict['place_name'] can be None
    """
    district_dict_suggestions = _get_suggestions_for_district_name(district_name, suggestion_limit)

    for district in district_dict_suggestions:
        place_id = district['district_id'] + "0000000"
        try:
            place_name = _places_dictionary[place_id]
        except KeyError:
            district['place_name'] = None
        else:
            district['place_name'] = place_name
        district['place_id'] = place_id
    return district_dict_suggestions


def _get_place_and_district_dict_suggestions(name: str, suggestion_limit: int) -> list[dict]:
    """
    Returns a list of dicts {'place_name', 'place_id', 'district_name', 'district_id'} with suggestions for the given
    district or place name

    Arguments:
        name (str): the given name
        suggestion_limit (int): limits the number of suggestions to the top x
    Returns:
        dict_suggestions (list[dict]): list of suggested dicts
    """
    district_dict_suggestions = _get_district_dict_suggestions(name, suggestion_limit)
    place_dict_suggestions = _get_place_dict_suggestions(name, suggestion_limit)
    for place_dict in place_dict_suggestions:
        for district_dict in district_dict_suggestions:
            if place_dict['place_id'] == district_dict['place_id']:
                district_dict_suggestions.remove(district_dict)
    dict_suggestions = place_dict_suggestions + district_dict_suggestions
    return dict_suggestions


def _get_dicts_for_postal_code(postal_code: str, suggestion_limit: int) -> list[dict]:
    """
    Returns a list of dicts {'place_name', 'place_id', 'district_name', 'district_id', 'postal_code'} that fit the place
    name and district id of given postal code (is not 100% accurate)

    Arguments:
        postal_code (str): the given postal code
        suggestion_limit (int): limits the number of suggestions to the top x
    Returns:
        place_dict_suggestions (list[dict]): list of dicts with fitting suggested place name and district id
    """
    try:
        record = _postal_code_dictionary[postal_code]
    except KeyError:
        return []  # no postal code found
    else:
        place_name = record[0]
        district_id = record[1]

    unfiltered_place_dict_suggestions = _get_place_dict_suggestions(place_name, suggestion_limit)
    place_dict_suggestions = []
    for place_dict in unfiltered_place_dict_suggestions:
        if place_dict['district_id'] == district_id:
            place_dict['postal_code'] = postal_code
            place_dict_suggestions.append(place_dict)
    return place_dict_suggestions


def get_name_for_id(given_id: str) -> Any:
    """
       Returns the district or place name of the given ID, if found

       Arguments:
           given_id (str): the given ID of a place or a district
       Returns:
           name (str): the place or district name of the given ID, can be None if not found
       """

    if len(given_id) == 5:  # district id
        try:
            district_name = _districts_dictionary[given_id]
        except KeyError:
            return None
        else:
            return district_name
    elif given_id[5:12] == '0000000':  # could still be only a district id
        try:
            place_name = _places_dictionary[given_id]
        except KeyError:
            try:
                given_id = given_id[0:5]
                district_name = _districts_dictionary[given_id]
            except KeyError:
                return None
            else:
                return district_name
        else:
            return place_name
    else:  # place id
        try:
            place_name = _places_dictionary[given_id]
        except KeyError:
            return None
        else:
            return place_name


def get_dicts_for_exact_district_name(district_name: str) -> list[dict]:
    """
    Returns a list of dicts {'place_name', 'place_id', 'district_name', 'district_id'} with the given district name

    Arguments:
        district_name (str): the name of the given district
    Returns:
        district_dicts (list[dict]): list of dicts, can be empty
    """
    district_dicts = []
    for district_id in _districts_dictionary.keys():
        if _districts_dictionary[district_id] == district_name:
            place_id = district_id + "0000000"
            try:
                place_name = _places_dictionary[place_id]
            except KeyError:
                place_name = None
            district_dict = {'place_name': place_name, 'place_id': place_id, 'district_name': district_name,
                             'district_id': district_id}
            district_dicts.append(district_dict)
    return district_dicts  # can be empty


def get_dicts_for_exact_place_name(place_name: str) -> list[dict]:
    """
    Returns a list of dicts {'place_name', 'place_id', 'district_name', 'district_id'} for the exact given place name

    Arguments:
        place_name (str): the given place name
    Returns:
        matching_place_dicts (list[dict]): list of suggested dicts
    """
    matching_place_dicts = []
    for place_id in _places_dictionary.keys():
        if _places_dictionary[place_id] == place_name:
            district_id = place_id[0:5]
            district_name = _districts_dictionary[district_id]
            place_dict = {'place_name': place_name, 'place_id': place_id, 'district_name': district_name,
                          'district_id': district_id}
            matching_place_dicts.append(place_dict)
    return matching_place_dicts


def get_dict_suggestions(given_string: str, suggestion_limit=11) -> list[dict]:
    """
    Returns a list of dicts {'place_name', 'place_id', 'district_name', 'district_id'} with suggestions for the given
    district or place name (alphabetic string) or postal code (numeric string)

    Arguments:
        given_string (str): the given name or postal code
        suggestion_limit (int): limits the number of suggestions to the top x, 11 by default
    Returns:
        dict_suggestions (list[dict]): list of suggested dicts
    """
    if given_string.isnumeric():
        return _get_dicts_for_postal_code(given_string, suggestion_limit)
    else:
        return _get_place_and_district_dict_suggestions(given_string, suggestion_limit)


def get_non_covid_dict_suggestions(given_string: str, suggestion_limit=11) -> list[dict]:
    """
    Returns a list of dicts {'place_name', 'postal_code', 'district_id', 'district_name'} with suggestions for the given
    place name (alphabetic string) or postal code (numeric string)

    Arguments:
        given_string (str): the given name or postal code
        suggestion_limit (int): limits the number of suggestions to the top x, 11 by default
    Returns:
        dict_suggestions (list[dict]): list of suggested dicts
    """
    if given_string.isnumeric():
        try:
            record = _postal_code_dictionary[given_string]
        except KeyError:
            return []
        else:
            dict_list = []
            postal_dict = {'postal_code': given_string, 'place_name': record[0],
                           'district_name': _districts_dictionary[record[1]], 'district_id': record[1]}
            dict_list.append(postal_dict)
            return dict_list
    else:
        return _get_suggestion_dicts_for_non_covid_place_name(given_string, suggestion_limit)


def get_place_name_from_dict(dictionary: dict) -> Any:
    """
    Returns the place name in a dictionary, if there is one

    Arguments:
        dictionary (dict): the given dictionary
    Returns:
        place_name (str): the place name saved in the dictionary, can be None
    """
    return dictionary['place_name']


def get_postal_code_from_dict(dictionary: dict) -> Any:  # TODO test
    """
    Returns the postal code in a dictionary, if there is one

    Arguments:
        dictionary (dict): the given dictionary
    Returns:
        place_name (str): the postal code saved in the dictionary, can be None
    """
    return dictionary['postal_code']


def get_place_id_from_dict(dictionary: dict) -> str:
    """
    Returns the place id in a dictionary, if there is one

    Arguments:
        dictionary (dict): the given dictionary
    Returns:
        place_id (str): the place id saved in the dictionary
    """
    return dictionary['place_id']


def get_district_name_from_dict(dictionary: dict) -> str:
    """
    Returns the district name in a dictionary, if there is one

    Arguments:
        dictionary (dict): the given dictionary
    Returns:
        district_name (str): the district name saved in the dictionary
    """
    return dictionary['district_name']


def get_district_id_from_dict(dictionary: dict) -> str:
    """
    Returns the district id in a dictionary, if there is one

    Arguments:
        dictionary (dict): the given dictionary
    Returns:
        district_id (str): the district id saved in the dictionary
    """
    return dictionary['district_id']


def get_suggestion_dicts_from_coordinates(latitude: float, longitude: float, suggestion_limit=11) -> list[dict]:
    """
    Returns a list of dicts {'place_name', 'place_id', 'district_name', 'district_id', 'postal_code'} that fit the given
    coordinates

    Arguments:
        latitude (float): latitude of coordinate
        longitude (float): longitude of coordinate
        suggestion_limit (int): limits the number of suggestions to the top x, 11 by default
    Returns:
        suggested_dicts (list[dict]): dicts that fit the infos
    """
    place_tuple = _get_exact_address_from_coordinates(latitude, longitude)

    postal_code = place_tuple[1]
    suggested_dicts_postal_code = _get_dicts_for_postal_code(postal_code, suggestion_limit)

    return suggested_dicts_postal_code


def get_non_covid_dict_from_coordinates(latitude: float, longitude: float) -> dict:
    """
    Returns a dict {'postal_code', 'place_name', 'district_name', 'district_id'} that fits the given
    coordinates

    Arguments:
        latitude (float): latitude of coordinate
        longitude (float): longitude of coordinate
    Returns:
        postal_dict (dict): dict that fits the infos
    """
    place_tuple = _get_exact_address_from_coordinates(latitude, longitude)

    postal_code = place_tuple[1]
    record = _postal_code_dictionary[postal_code]

    postal_dict = {'postal_code': postal_code, 'place_name': record[0],
                   'district_name': _districts_dictionary[record[1]], 'district_id': record[1]}

    return postal_dict


def get_postal_code_dicts_in_polygon(coordinate_list: list) -> list[dict]:
    """
        Returns a list of dicts {'postal_code', 'place_name', 'district_id', 'district_name'} of places that overlap
        with the given polygon coordinates.

        Arguments:
            coordinate_list (list): a list containing coordinates, making up a valid polygon
        Returns:
            list_of_matches (list[dict]): list of dicts that fit the infos, can be empty if no match is found
        """

    list_of_matches = []
    polygon = shapely.Polygon(coordinate_list)
    for place in _postal_code_dictionary:
        place_coordinates = _postal_code_dictionary[place][2]
        place_poly = shapely.Polygon(place_coordinates)

        if polygon.intersects(place_poly):
            intersections = polygon.intersection(place_poly)
            if not isinstance(intersections, shapely.geometry.multilinestring.MultiLineString):
                district_id = _postal_code_dictionary[place][1]
                district_name = _districts_dictionary[district_id]
                matching_dict = {'postal_code': place, 'place_name': _postal_code_dictionary[place][0],
                                 'district_id': district_id, 'district_name': district_name}
                list_of_matches.append(matching_dict)
    return list_of_matches


def get_place_name_for_postal_code(postal_code: str) -> str:
    """
    Returns the place name matching the postal code.

    Arguments:
        postal_code (str): the given postal code
    Returns:
        place_name (str): the place name matching the postal code
    """
    return _postal_place_dictionary[postal_code]


def get_district_name_for_district_id(district_id: str) -> str:
    """
    Returns the district name matching the district id.

    Arguments:
        district_id (str): the given district id
    Returns:
        district_name (str): the district name matching the district id
    """
    return _districts_dictionary[district_id]
