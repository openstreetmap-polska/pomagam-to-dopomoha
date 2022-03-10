from typing import Any


class Parser:
    CATEGORIES = {
        '1': 'charityDropOff',
        '2': 'accommodation',
        '3': 'govermentCharity',
        '4': 'psychologicalAssistance',
        '5': 'legalAssistance',
        '6': 'medicalAssistance',
        '7': 'animalAssistance',
        '8': 'childcare',
        '9': 'transport',
    }

    @staticmethod
    def parse_id(value: Any) -> str:
        if not value:
            raise ValueError('ID cannot be empty!')

        return str(value)

    @staticmethod
    def parse_category(value: Any) -> str:
        if not isinstance(value, list):
            raise ValueError(f'Unexpected category data type: {value}')

        if len(value) > 1:
            raise ValueError(f'Unexpected multiple categories: {value}')

        # Currently empty should be handled same as '1'
        if len(value) == 0:
            return Parser.CATEGORIES['1']
            # raise ValueError('Category cannot be empty!')

        category_id = value[0]
        try:
            return Parser.CATEGORIES[category_id]
        except Exception:
            raise ValueError(f'Unexpected category ID: {category_id}')

    @staticmethod
    def parse_verified(value: Any) -> bool:
        TRUE_VALUES = {
            'tak',
            'zweryfikowany',
            'zweryfikowane',
            'zweryfikowana',
            'zweryfikowano',
        }
        FALSE_VALUES = {
            'nie',
            'niezweryfikowany',
            'niezweryfikowana',
            'niezweryfikowane',
            'niezweryfikowano',
        }

        # for now empty value is just False
        if not value:
            return False
            # raise ValueError('Verify cannot be empty!')

        # TODO replace <space> with other possible whitespace characters
        clean_value = value.replace(' ', '').strip().lower()

        if clean_value in TRUE_VALUES:
            return True

        elif clean_value in FALSE_VALUES:
            return False

        else:
            raise ValueError(f'Unexpected verified value: {value}')

    @staticmethod
    def parse_lat(value: Any) -> float:
        lat = float(value)

        if not (45 < lat < 56):
            raise ValueError(f'Suspicious latitude: {lat}')

        return lat

    @staticmethod
    def parse_lng(value: Any) -> float:
        lng = float(value)

        if not (12 < lng < 30):
            raise ValueError(f'Suspicious longitude: {lng}')

        return lng

    @staticmethod
    def parse_name(value: Any) -> str:
        if not value:
            raise ValueError('Name cannot be empty!')
        # TODO check is there any max_length limit
        # TODO sanitize it
        return str(value)

    @staticmethod
    def parse_description(value: Any) -> str:
        # TODO check is there any max_length limit
        # TODO sanitize it
        return str(value) if value else None

    @staticmethod
    def parse_phone(value: Any) -> str:
        # TODO exctract digits and reformat using dopomoha expected formatting
        # TODO if missing
        return str(value) if value else None

    @staticmethod
    def parse_addr(value: Any) -> str:
        # Currently not used
        return str(value) if value else None

    @staticmethod
    def parse_website(value: Any) -> str:
        # Currently not used
        return str(value) if value else None

    @staticmethod
    def parse_opening_hours(value: Any) -> str:
        # Currently not used
        return str(value) if value else None
