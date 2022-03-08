import gspread

from typing import Any, Dict, List


class Translation:
    """
    Translation class is responsible for integrating 3rd party app
    to translate some properties of imported data from pomag.am site.

    It uses google Spreadsheet API to give opportunity to share it with
    translators group.
    """
    def __init__(self, credential_filename, spreadsheet_key):
        self.gc = gspread.service_account(filename=credential_filename)
        self.spreadsheet = self.gc.open_by_key(spreadsheet_key)

    def fetch(
        self,
        worksheet: gspread.Worksheet = None,
        head=1
    ) -> List[Dict[str, Any]]:
        """
        Read whole spreadsheet from given worksheet
        :param worksheet: if none it uses default 'sheet1' worksheet
        :param head: row number with headers
        :return: all data from workshet in format: [
            {'col1': val1, 'col2': val2},
            {'col1': val1, 'col2': val2},
        ]
        """
        if worksheet is None:
            worksheet = self.spreadsheet.sheet1

        return worksheet.get_all_records(head=head)

    @staticmethod
    def _rstrip_list(data: List[Any]):
        """
        Removes trailing non True value from list
        """
        while data and not data[-1]:
            data.pop()

    def update(
        self,
        data: List[Dict[str, Any]],
        worksheet: gspread.Worksheet = None,
        head=1,
        empty_value=''
    ):
        """
        Update whole spreadsheet with given data
        :param worksheet: if none it uses default 'sheet1' worksheet
        :param head: row number with headers
        :param empty_value: value which will be used to fill cells with missing
        key: value pairs in data
        """
        if worksheet is None:
            worksheet = self.spreadsheet.sheet1

        headers = worksheet.row_values(1)
        Translation._rstrip_list(headers)

        ordered_data = [[header for header in headers]]
        for row in data:
            ordered_row = [row.get(header, empty_value) for header in headers]
            ordered_data.append(ordered_row)

        worksheet.update(ordered_data)