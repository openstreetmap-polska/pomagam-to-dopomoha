import requests

import json

from typing import Any, Dict, List, Tuple

from parser import Parser


# map_id=1 – production, map_id=2 – tests
POMAGAM_URL = 'https://pomag.am/index.php' \
              '?rest_route=/wpgmza/v1/markers' \
              '&filter={"map_id":"1"}'

FIELD_PARSER = {
    'id': Parser.parse_id,
    'category': Parser.parse_category,
    'verified': Parser.parse_verified,
    'lat': Parser.parse_lat,
    'lng': Parser.parse_lng,
    'name': Parser.parse_name,
    'description': Parser.parse_description,
    'phone': Parser.parse_phone,
    'address': Parser.parse_address,
    'opening_hours': Parser.parse_opening_hours,
    'website': Parser.parse_website,
}


def download_markers() -> List[Dict[str, Any]]:
    return requests.get(POMAGAM_URL).json()


def custom_to_dict(custom_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {field['name']: field['value'] for field in custom_fields}


def remap_filter_attributes(
    raw_markers: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    """
    Raw marker contains 'category' and 'categories' attributes!
    But they don't have the same value (probably plugin or wordpress fault)
    So only 'categories' is correct, but it can contain multiple values
    which will be parsed (or not) to only one, so it's remaped to
    'category' name anyway.
    """
    fields = {
        # meta data
        'id': 'id',
        'categories': 'category',

        # marker data
        'title': 'name',
        'address': 'address',
        'lat': 'lat',
        'lng': 'lng',
        'description': 'description',
        'link': 'website',
    }

    # nested additional fields used for "custom_fields"
    other_fields = {
        # meta data
        'Czy zweryfikowany?': 'verified',

        # marker data
        'Numer telefonu': 'phone',
        'Godziny otwarcia': 'opening_hours',
    }
    markers = []

    for raw_marker in raw_markers:
        marker = {}

        for key, value in fields.items():
            marker[value] = raw_marker.get(key, None)

        custom_field_data = custom_to_dict(raw_marker['custom_field_data'])

        for key, value in other_fields.items():
            marker[value] = custom_field_data.get(key, None)

        markers.append(marker)

    return markers


def parse_pois(markers: List[Dict[str, Any]]) -> Tuple[List, List]:
    pois = []
    invalid_markers = []

    for marker in markers:
        poi = {}
        errors = {}

        for key, value in marker.items():
            try:
                poi[key] = FIELD_PARSER[key](value)

            except ValueError as error:
                errors[key] = str(error)

        if errors:
            invalid_markers.append((errors, marker))
        else:
            pois.append(poi)

    return pois, invalid_markers


def pois_to_geojson(pois: List[Dict[str, Any]]) -> Dict[str, Any]:
    geojson = {
        'type': 'FeatureCollection',
        'features': []
    }

    for poi in pois:
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [poi['lng'], poi['lat']]
            },
        }
        del poi['lng']
        del poi['lat']
        feature['properties'] = {k: v for k, v in poi.items()}
        geojson['features'].append(feature)

    return geojson


def group_by_category(pois: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    categorized_pois = {
        v: [] for v in Parser.CATEGORIES.values()
    }
    for poi in pois:
        categorized_pois[poi['category']].append(poi)

    return categorized_pois


def main():
    raw_markers = download_markers()
    markers = remap_filter_attributes(raw_markers)
    all_pois, invalid_markers = parse_pois(markers)

    verified_pois = list(filter(lambda x: x['verified'], all_pois))
    with open('pomagam.geojson', 'w', encoding='utf-8') as f:
        json.dump(
            pois_to_geojson(verified_pois),
            f,
            ensure_ascii=False,
            indent=4
        )

    # Write to multiple files (per category)
    # categorized_pois = group_by_category(verified_pois)
    # for category, pois in categorized_pois.items():
    #     with open(f'pomagam-{category}.geojson', 'w', encoding='utf-8') as f:
    #         json.dump(pois_to_geojson(pois), f, ensure_ascii=False, indent=4)

    with open('pomagam_invalid.json', 'w', encoding='utf-8') as f:
        json.dump(invalid_markers, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
