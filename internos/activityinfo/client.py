#!/usr/bin/env python
# coding=utf-8
__author__ = 'jcranwellward'

import json
import os
import argparse
from urlparse import urljoin
from ConfigParser import SafeConfigParser

from . import auth

import requests
from requests.auth import HTTPBasicAuth


class ActivityInfoClient(object):
    """ ActivityInfo python client to allow the following requests:

        List all databases visible to the client: /databases
        Retrieve the structure of database id 504: /database/504/schema
        Retrieve all sites in activity 33: /sites?activity=33
        Retrieve all sites in activity 33 in GeoJSON format: /sites/points?activity=33

        List all countries: /countries
        List all administrative levels in Lebanon (country code LB): /country/LB/adminLevels
        List all administrative entities in level 1370: /adminLevel/1370/entities
        List all administrative entities in level 1370 in GeoJSON format: /adminLevel/1370/entities/features
        List all location types in Lebanon: /country/LB/locationTypes
        List all locations of type 1370: /locations?type=1370

    """

    def __init__(self,
                 username='',
                 password='',
                 base_url='https://v4.activityinfo.org/'):
        self.base_url = base_url
        if username and password:
            self.auth = HTTPBasicAuth(username, password)

    def build_path(self, path=None):
        """ Builds the full path to the service.

        Args:
            path (string): The part of the path you want to append
            to the base url.

        Returns:
            A string containing the full path to the endpoint.
            e.g if the base_url was "http://woo.com" and the path was
            "databases" it would return "http://woo.com/databases/"
        """
        if path is None:
            return self.base_url
        return "{}{}".format(self.base_url, path)
        # return urljoin(
        #     self.base_url, os.path.normpath(path),
        # )

    def make_request(self, path, **params):

        response = requests.get(
            self.build_path(path),
            params=params,
            auth=getattr(self, 'auth', ()),
        )
        return response

    def call_command(self, type, **properties):

        payload = json.dumps(
            {
                'type': type,
                'command': {
                    'properties': properties
                }
            }
        )

        response = requests.post(
            self.build_path('command'),
            headers={'content-type': 'application/json'},
            auth=getattr(self, 'auth', ()),
            data=payload,
        )
        return response

    def get_databases(self):
        return self.make_request('resources/databases').json()

    def get_databases_v4(self, database_id):
        return self.make_request('resources/databases/{}'.format(database_id)).json()

    def get_database_indicators_v4(self,form_id):
        return self.make_request('/resources/form/{}/schema'.format(form_id)).json()

    def get_database(self, db_id):
        return self.make_request('resources/database/{}/schema'.format(db_id)).json()

    def get_partners(self,form_id):
        return self.make_request('resources/form/{}/query/rows'.format(form_id)).json()

    def get_sites(self, database=None, partner=None, activity=None, indicator=None, attribute=None):
        sites = self.make_request(
            'resources/sites',
            database=database,
            partner=partner,
            activity=activity,
            indicator=indicator,
            attribute=attribute).json()
        return sites

    def get_activity(self, activity=None):
        return self.make_request(
            'resources/sites?activity='+str(activity)).json()

    def get_indicator(self, indicator=None):
        return self.make_request(
            'resources/sites?indicator='+str(indicator)).json()

    def get_partner(self, partner=None):
        return self.make_request(
            'resources/sites?partner='+str(partner)).json()

    def get_attribute(self, attribute=None):
        return self.make_request(
            'resources/sites?attribute='+str(attribute)).json()

    def get_cube(self, form_ids, month=None):
        return self.make_request(
            'resources/sites/cube?'
            'dimension=indicator'
            '&dimension=site'
            '&dimension=month'
            '{}'
            '&form={}'.format(
                '&month='+month if month is not None else '',
                '&form='.join([str(id) for id in form_ids])
            )).json()

    def get_monthly_reports_for_site(self, site_id):
        # return self.make_request('resources/sites/{}/monthlyReports'.format(site_id)).json()
        result = self.make_request('resources/sites/{}/monthlyReports'.format(site_id))
        print(result.content)

    def get_countries(self):
        return self.make_request('resources/countries').json()

    def get_admin_levels(self, country):
        return self.make_request('resources/country/{}/adminLevels'.format(country)).json()

    def get_location_types(self, country):
        return self.make_request('resources/country/{}/locationTypes'.format(country)).json()

    def get_entities(self, level_id):
        return self.make_request('resources/adminLevel/{}/entities'.format(level_id)).json()

    def get_locations(self, type_id):
        return self.make_request('resources/locations', type=type_id).json()


def main():
    """
    Main method for command line usage
    """
    parser = argparse.ArgumentParser(
        description='ActivityInfo API Python Client'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--database',
                       type=int,
                       help='Database to query')
    group.add_argument('-a', '--activity',
                       type=int,
                       help='Filter results by activty')
    parser.add_argument('-p', '--partner',
                        type=int,
                        default=None,
                        help='Filter results by partner')
    parser.add_argument('-i', '--indicator',
                        type=int,
                        default=None,
                        help='Filter results by indicator')
    parser.add_argument('-U', '--username',
                        type=str,
                        default='',
                        help='Optional username for authentication')
    parser.add_argument('-P', '--password',
                        type=str,
                        default='',
                        help='Optional password for authentication')

    args = parser.parse_args()

    try:
        parser = SafeConfigParser()
        parser.read('settings.ini')
        username = parser.get('auth', 'user')
        password = parser.get('auth', 'pass')
        client = ActivityInfoClient(
            username=username or args.username,
            password=password or args.password,
        )
        if args.database:
            response = client.get_database(args.database)
        elif args.activity:
            response = client.get_sites(args.partner,
                                        args.activity,
                                        args.indicator)
        else:
            response = client.get_sites()

        print (response)

    except Exception as exp:
        print (str(exp))


class Client:
    """Client to interact with the ActivityInfo API."""

    def __init__(self, token='a18228497221bfb35998a01984fe2446', base_url='https://www.activityinfo.org'):
        """Initialize a Client object

        :param token: Your API token.
        :param base_url: The base URL of the ActivityInfo API **without** a trailing backslash.
        """
        self.auth = auth.TokenAuth(token)
        self.base_url = base_url

    def get_resource(self, path, query_params=None):
        """Send a GET request to the ActivityInfo API

        :param path: The path of the resource. For example, 'resources/databases'.
        :param query_params: Dictionary, list of tuples or bytes to send in the query string for the request.
        :return: JSON-encoded contents of the response.
        """
        r = requests.get(url=self.base_url + '/' + path,
                         params=query_params,
                         auth=self.auth,
                         headers={'Accept': 'application/json'})
        r.raise_for_status()
        return r.json()

    def post_resource(self, path, body):
        """Send a POST request to the ActivityInfo API

        :param path: The path of the resource. For example, 'resources/databases'.
        :param body: JSON payload.
        :return: JSON-encoded contents of the response.
        """
        r = requests.post(url=self.base_url + '/' + path,
                          json=body,
                          auth=self.auth,
                          headers={'Accept': 'application/json'})
        r.raise_for_status()
        return r.json()
