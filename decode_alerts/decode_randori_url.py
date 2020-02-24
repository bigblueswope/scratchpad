import argparse
import base64
import json
import sys

try:  # Python 3+
    from urllib.parse import (
        parse_qs, parse_qsl, urlencode, urlparse, urlunparse
    )
except ImportError:  # Python 2
    from urllib import urlencode
    from urlparse import parse_qs, parse_qsl, urlparse, urlunparse



def get_query_field(url, field):
    """
    Given a URL, return a list of values for the given ``field`` in the
    URL's query string.

    >>> get_query_field('http://example.net', field='foo')
    []

    >>> get_query_field('http://example.net?foo=bar', field='foo')
    ['bar']

    >>> get_query_field('http://example.net?foo=bar&foo=baz', field='foo')
    ['bar', 'baz']
    """

    print("\n###############\n")
    
    print("URL:" , url)

    try:
        return parse_qs(urlparse(url).query)[field]
    except KeyError:
        return []



example_url = 'https://alpha.randori.io/targets?limit=10&offset=0&q=eyJjb25kaXRpb24iOiJBTkQiLCJydWxlcyI6W3siY29uZGl0aW9uIjoiT1IiLCJydWxlcyI6W3sibGFiZWwiOiJsb3ciLCJjb25kaXRpb24iOiJBTkQiLCJydWxlcyI6W3siaWQiOiJ0YWJsZS5jb25maWRlbmNlIiwiZmllbGQiOiJ0YWJsZS5jb25maWRlbmNlIiwidHlwZSI6ImludGVnZXIiLCJpbnB1dCI6Im51bWJlciIsIm9wZXJhdG9yIjoiZ3JlYXRlcl9vcl9lcXVhbCIsInZhbHVlIjowfSx7ImlkIjoidGFibGUuY29uZmlkZW5jZSIsImZpZWxkIjoidGFibGUuY29uZmlkZW5jZSIsInR5cGUiOiJpbnRlZ2VyIiwiaW5wdXQiOiJudW1iZXIiLCJvcGVyYXRvciI6Imxlc3Nfb3JfZXF1YWwiLCJ2YWx1ZSI6NTl9XX0seyJsYWJlbCI6Im1lZGl1bSIsImNvbmRpdGlvbiI6IkFORCIsInJ1bGVzIjpbeyJpZCI6InRhYmxlLmNvbmZpZGVuY2UiLCJmaWVsZCI6InRhYmxlLmNvbmZpZGVuY2UiLCJ0eXBlIjoiaW50ZWdlciIsImlucHV0IjoibnVtYmVyIiwib3BlcmF0b3IiOiJncmVhdGVyX29yX2VxdWFsIiwidmFsdWUiOjYwfSx7ImlkIjoidGFibGUuY29uZmlkZW5jZSIsImZpZWxkIjoidGFibGUuY29uZmlkZW5jZSIsInR5cGUiOiJpbnRlZ2VyIiwiaW5wdXQiOiJudW1iZXIiLCJvcGVyYXRvciI6Imxlc3Nfb3JfZXF1YWwiLCJ2YWx1ZSI6NzR9XX0seyJsYWJlbCI6ImhpZ2giLCJjb25kaXRpb24iOiJBTkQiLCJydWxlcyI6W3siaWQiOiJ0YWJsZS5jb25maWRlbmNlIiwiZmllbGQiOiJ0YWJsZS5jb25maWRlbmNlIiwidHlwZSI6ImludGVnZXIiLCJpbnB1dCI6Im51bWJlciIsIm9wZXJhdG9yIjoiZ3JlYXRlcl9vcl9lcXVhbCIsInZhbHVlIjo3NX0seyJpZCI6InRhYmxlLmNvbmZpZGVuY2UiLCJmaWVsZCI6InRhYmxlLmNvbmZpZGVuY2UiLCJ0eXBlIjoiaW50ZWdlciIsImlucHV0IjoibnVtYmVyIiwib3BlcmF0b3IiOiJsZXNzX29yX2VxdWFsIiwidmFsdWUiOjEwMH1dfV0sInVpX2lkIjoiY29uZmlkZW5jZSJ9LHsidWlfaWQiOiJ1bmFmZmlsaWF0ZWQiLCJjb25kaXRpb24iOiJPUiIsInJ1bGVzIjpbeyJ1aV9pZCI6ImhpZGVfdW5hZmZpbGlhdGVkIiwiaWQiOiJ0YWJsZS50YWdzIiwiZmllbGQiOiJ0YWJsZS50YWdzIiwidHlwZSI6Im9iamVjdCIsImlucHV0IjoidGV4dCIsIm9wZXJhdG9yIjoibm90X2NvbnRhaW5zIiwidmFsdWUiOnsiU1BFQytVTkFGRklMSUFURUQiOnt9fX1dfV19&reversed_nulls=true&sort=-target_temptation'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Decode UI URL')
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", required=True, help="URL to Decode")
    args = parser.parse_args()
    
    
    query_array = get_query_field(args.input, 'q')
    
    if query_array == [] :
        print("Input URL must be quoted because the shell interprets the & as a command to background the first part of the command")
        sys.exit(1)


    for s in query_array:
        s = base64.b64decode(s)

        j_string = json.loads(s)
        
        pp_j_string = json.dumps(j_string, indent=2, sort_keys=True)
        
        print("\n###############\n")
        
        print(pp_j_string)


