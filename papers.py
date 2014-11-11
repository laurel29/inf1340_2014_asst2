#!/usr/bin/env python3

""" Computer-based immigration office for Kanadia """

__author__ = 'Susan Sim'
__email__ = "ses@drsusansim.org"

__copyright__ = "2014 Susan Sim"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line
import re
import datetime
import json


def decide(input_file, watchlist_file, countries_file):
    """
    Decides whether a traveller's entry into Kanadia should be accepted

    :param input_file: The name of a JSON formatted file that contains cases to decide
    :param watchlist_file: The name of a JSON formatted file that contains names and passport numbers on a watchlist
    :param countries_file: The name of a JSON formatted file that contains country data, such as whether
        an entry or transit visa is required, and whether there is currently a medical advisory
    :return: List of strings. Possible values of strings are: "Accept", "Reject", "Secondary", and "Quarantine"
    """
    results = list()

    with open(input_file, 'r') as input_file:
        input_file_contents = input_file.read()
        entries_contents = json.loads(input_file_contents)

    with open(watchlist_file, 'r') as watchlist_file:
        watchlist_file_contents = watchlist_file.read()
        watchlist_contents = json.loads(watchlist_file_contents)

    with open(countries_file, 'r') as countries_file:
        countries_file_contents = countries_file.read()
        countries_contents = json.loads(countries_file_contents)

    for entry in entries_contents:
        #Check for quarantine
        #Check if person on the watchlist
        #Check if person returning and home country is KAN
        #Check for visas

        entry_status = "Quarantine"

        entry_first_name = entry["first_name"]
        entry_last_name = entry["last_name"]
        entry_passport = entry["passport"]
        entry_reason = entry["entry_reason"]

        entry_home = dict()
        entry_from = dict()
        entry_via = dict()
        entry_visa = dict()

        if "home" in entry:
            entry_home = entry["home"]

        if "from" in entry:
            entry_from = entry["from"]

        if "via" in entry:
            entry_via = entry["via"]

        if "visa" in entry:
            entry_visa = entry["visa"]

        if not entry_first_name or not entry_last_name or not entry_passport or not entry_home or not entry_from or not\
                entry_reason:
            if entry_via:
                if check_medical_advisory(entry_via["country"], countries_contents):
                    #this condition checks if the country is on the medical advisory list
                    entry_status = "Quarantine"
                    #if the country is on the medical list then it will send the entry to Quarantine
                    results.append(entry_status)
                    continue
                    #continues to the next loop

            if entry_home:
                if check_medical_advisory(entry_from["country"], countries_contents):
                    entry_status = "Quarantine"
                    results.append(entry_status)
                    continue

            entry_status = "Reject"
            results.append(entry_status)
            continue
        elif not valid_passport_format(entry_passport):
            entry_status = "Reject"
            results.append(entry_status)
            continue
        else:
            if entry_home["country"] == "KAN" and entry_reason == "returning":
                if entry_via:
                    #Checks via country against countries with medical advisory
                    if check_medical_advisory(entry_via["country"], countries_contents):
                        #if the via country has a medical advisory the entry is sent to Quarantine
                        entry_status = "Quarantine"
                        results.append(entry_status)
                        continue

                if check_medical_advisory(entry_from["country"], countries_contents):
                    entry_status = "Quarantine"
                    results.append(entry_status)
                    continue

                watch_status = check_watch_list(entry_first_name, entry_last_name, entry_passport, watchlist_contents)
                #Checks if entry is on the watchlist, returns Reject or Secondary if on list, Accept if not on list
                if watch_status == "Reject":
                    entry_status = "Reject"
                    results.append(entry_status)
                    continue
                elif watch_status == "Secondary":
                    entry_status = "Secondary"
                    results.append(entry_status)
                    continue
                else:
                    entry_status = "Accept"
                    results.append(entry_status)
                    continue
            else:
                #Checks if the via country has a medical advisory
                if entry_via:
                    if check_medical_advisory(entry_via["country"], countries_contents):
                        entry_status = "Quarantine"
                        results.append(entry_status)
                        continue
                #Checks if the country traveled from has a medical advisory
                if check_medical_advisory(entry_from["country"], countries_contents):
                    entry_status = "Quarantine"
                    results.append(entry_status)
                    continue
                #Checks if the country traveled from requires a visa for entry
                if check_visa_required(entry_from["country"], countries_contents, entry_reason):
                    if not entry_visa:
                        entry_status = "Reject"
                        results.append(entry_status)
                        continue
                    elif not valid_visa(entry_visa):
                        entry_status = "Reject"
                        results.append(entry_status)
                        continue

                #Checks status on watchlist, returns either Secondary or Reject if on watchlist
                #Returns accept if entry not on watch list
                watch_status = check_watch_list(entry_first_name, entry_last_name, entry_passport, watchlist_contents)
                if watch_status == "Secondary":
                    entry_status = "Secondary"
                    results.append(entry_status)
                    continue
                elif watch_status == "Reject":
                    entry_status = "Reject"
                    results.append(entry_status)
                    continue
                else:
                    entry_status = "Accept"
                    results.append(entry_status)
                    continue
    return results


#Used to check if a country has a medical advisory or not
def check_medical_advisory(country, country_list):
    #If country has medical advisory, returns True
    if country_list[country]["medical_advisory"]:
        return True
    #If not, return False
    else:
        return False


def check_watch_list(first_name, last_name, passport, watchlist):
    # Check person against every record in the watchlist return Reject or Secondary if found
    # Return Accept if not in list
    for item in watchlist:
        if first_name == item["first_name"] and last_name == item["last_name"] and passport == item["passport"]:
            return "Reject"
        elif first_name == item["first_name"] or last_name == item["last_name"] or passport == item["passport"]:
            return "Secondary"
        else:
            continue
    else:
        return "Accept"


def check_visa_required(country, country_list, entry_reason):
    # Check if visa is required for country with appropriate reason
    # Return True or False
    if entry_reason == "visit":
        if country_list[country]["visitor_visa_required"] == "1":
            return True
        else:
            return False
    elif entry_reason == "transit":
        if country_list[country]["transit_visa_required"] == "1":
            return True
        else:
            return False


def valid_passport_format(passport_number):
    """
    Checks whether a passport number is five sets of five alpha-number characters separated by dashes
    :param passport_number: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('.{5}-.{5}-.{5}-.{5}-.{5}')

    if passport_format.match(passport_number):
        return True
    else:
        return False


def valid_visa(visa_number, visa_date):
    """
    Checks whether a visa number is 2 sets of five alpha-number characters separated by dashes
    :rtype : object
    :param visa_number: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """

    valid_format = False
    valid_date = False

    visa_format = re.compile('.{5}-.{5}')

    if visa_format.match(visa_number):
        valid_format = True

    visa_years = datetime.datetime.now() - datetime.datetime.strptime(visa_date, "%Y-%m-%d")
    visa_years_difference = visa_years.days / 365

    if visa_years_difference < 2:
        valid_date = True
        #this if condition checks if the visa validity is less than two years

    if valid_date and valid_format:
        #return True only if visa has a valid format and is not over two years old
        return True
    else:
        return False


def valid_date_format(date_string):
    """
    Checks whether a date has the format YYYY-mm-dd in numbers
    :param date_string: date to be checked
    :return: Boolean True if the format is valid, False otherwise
    """
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
