#!/usr/local/bin/python3.0

import errno
import fnmatch
import os
import time

def read_single_line_log_file(log_file, skip_first_line):
    """Reads all logs from a file where logs are denoted by a line break."""
    log_lines = []

    if os.path.exists(log_file):
        with open(log_file) as f:
            log_lines = f.readlines()
    else:
        print ("Log file not found: %s" % str(log_file))
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(log_file))

    if skip_first_line == True:
        log_lines.pop(0)

    return log_lines

def read_line_delimited_file(monitor_obj):
    try:
        # check for wildcard in log file location
        if "*" in monitor_obj["location"]:
            #get directory
            location_array = monitor_obj["location"].rpartition(os.sep)
            matching_files = fnmatch.filter(os.listdir(location_array[0]), location_array[2])
            print ("Found matching files: %s" % (matching_files))

            # setup objects for new files
            if "file_locations" in monitor_obj:
                for matching_file in matching_files:
                    match_found = False

                    for file_location in monitor_obj["file_locations"]:
                        if file_location["location"] == matching_file:
                            match_found = True

                    if match_found == False:
                        log_file_path = os.path.join(location_array[0], matching_file)
                        file_location = {"location": log_file_path, "last_line_read": 0, "last_time_read": 0}
                        monitor_obj["file_locations"].append(file_location)
            else:
                # setup file locations in monitor config dictionary
                monitor_obj["file_locations"] = []

                for matching_file in matching_files:
                    log_file_path = os.path.join(location_array[0], matching_file)
                    file_location = {"location": log_file_path, "last_line_read": 0, "last_time_read": 0}
                    monitor_obj["file_locations"].append(file_location)
        else:
            #Single file monitor
            if "file_locations" not in monitor_obj:
                # No file locations object yet, create outdoor_longitude
                monitor_obj["file_locations"] = []
                log_file_path = os.path.join(location_array[0], log_file)
                file_location = {"location": log_file_path, "last_line_read": 0, "last_time_read": 0}
                monitor_obj["file_locations"].append(file_location)

        # read in file monitors
        lines_to_proccess = []

        for file_monitor in monitor_obj["file_locations"]:
            lines_to_proccess.extend(read_monitored_file(file_monitor, monitor_obj["has_header"]))

    except Exception as e:
        print ("Error reading delimited file.")
        raise e

    return lines_to_proccess

def read_monitored_file(monitored_file_object, skip_first_line):
    try:
        log_lines = read_single_line_log_file(monitored_file_object["location"], skip_first_line)

        # Check to see if log was rotated
        if len(log_lines) < monitored_file_object["last_line_read"]:
            monitored_file_object["last_line_read"] = 0
            print ("Log Rotated: %s" % str(monitored_file_object["location"]))

        if monitored_file_object["last_line_read"] > 0:
            read_start_line = monitored_file_object["last_line_read"] + 1
        else:
            read_start_line = 0

        #update last line read and time read
        monitored_file_object["last_line_read"] = len(log_lines)
        monitored_file_object["last_time_read"] = int(time.time())

        if read_start_line > 0:
            print ("Starting at line %i" % (read_start_line))
            read_start_line = read_start_line * -1
            total_file_lines = len(log_lines)
            log_lines = log_lines[:read_start_line]
            lines_to_read = len(log_lines)
            print ("File contains %i lines, only reading the last %i lines." % (total_file_lines, lines_to_read))

    except Exception as e:
        print ("Error reading delimited file monitor.")
        raise e

    return log_lines

def parse_delimited_file(log_lines, monitor_config):
    parsed_data = []

    for line in log_lines:
        data_entry = []
        fields_untyped = line.strip().split(monitor_config["delimiter"])
        fields = []

        #type field values
        for field in fields_untyped:
            try:
                try:
                    if (field == str(int(field))):
                        fields.append(int(field))
                    elif (field == str(float(field))):
                        fields.append(float(field))
                    else:
                        fields.append(str(field))
                except ValueError:
                    fields.append(str(field))
            except:
                fields.append(str(field))

        # Map entries from log line to the labels given in the config file.
        for entry in monitor_config["data_maping"]:
            if len(entry["indexes"]) > 1:
                #Combine indexes into a single value
                data_value = ""

                for i in range(len(entry["indexes"])):
                    data_value = data_value + ("%s%s" % (fields[i], entry["spacer"]))

                # remove last delimiter
                data_value = data_value[:-1]
                data_object = {"label": entry["label"], "value":data_value}
            elif len(entry["indexes"]) == 1:
                data_object = {"label": entry["label"], "value":fields[entry["indexes"][0]]}
            else:
                print ("No index value for label: %s" % (entry["label"]))
                data_object = {}

            data_entry.append(data_object)

        # Add the aditional data lines to the parsed data
        for additional_field in monitor_config["additional_fields"].keys():
            data_object = {"label": additional_field, "value":monitor_config["additional_fields"][additional_field]}
            data_entry.append(data_object)

        first_line_read = True
        parsed_data.append(data_entry)

    return parsed_data
