import csv
import io
import json

import click
from in3cli.util import find_format_width
from in3cli.util import format_to_table
from in3cli.util import get_attribute_keys_from_class


class OutputFormat:
    TABLE = "DEFAULT"
    JSON = "JSON"
    CSV = "CSV"

    @staticmethod
    def choices():
        return get_attribute_keys_from_class(OutputFormat)


class OutputFormatter:
    def __init__(self, output_format, header=None):
        output_format = output_format.upper() if output_format else OutputFormat.TABLE
        self.output_format = output_format
        self._format_func = to_table
        self.header = header

        if output_format == OutputFormat.CSV:
            self._format_func = to_csv
        elif output_format == OutputFormat.TABLE:
            self._format_func = self._to_table
        elif output_format == OutputFormat.JSON:
            self._format_func = to_json

    def echo(self, output_list):
        formatted_output = self._get_formatted_output(output_list)
        for output in formatted_output:
            click.echo(output, nl=False)
        if self.output_format in [OutputFormat.TABLE]:
            click.echo()

    def echo_via_pager(self, output):
        click.echo_via_pager(self._get_formatted_output(output))

    def _format_output(self, output):
        return self._format_func(output)

    def _to_table(self, output):
        return to_table(output, self.header)

    def _get_formatted_output(self, output):
        if self._requires_list_output:
            yield self._format_output(output)
        else:
            for item in output:
                yield self._format_output(item)

    @property
    def _requires_list_output(self):
        return self.output_format in (OutputFormat.TABLE, OutputFormat.CSV)


def to_csv(output):
    """Output is a list of dicts"""

    if not output:
        return
    string_io = io.StringIO()
    fieldnames = sorted(list({k for d in output for k in d.keys()}))
    writer = csv.DictWriter(string_io, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output)
    return string_io.getvalue()


def to_table(output, header):
    """Output is a list of records"""
    if not output:
        return
    rows, column_size = find_format_width(output, header)
    return format_to_table(rows, column_size)


def to_json(output):
    """Output is a single record"""
    json_str = "{}\n".format(json.dumps(output, indent=4))
    return json_str
