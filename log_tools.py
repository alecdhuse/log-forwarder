#!/usr/local/bin/python3.0

import os

def read_single_line_log_file(log_file):
    """Reads all logs from a file where logs are denoted by a line break."""
    log_lines = []

    if os.path.exists(log_file):
        with open(log_file) as f:
            log_lines = f.readlines()
    else:
        print ("Log file not found: %s" % str(log_file))

    return log_lines

def read_line_delimited_file(monitor_obj):
    log_lines = read_single_line_log_file(monitor_obj["location"])

    # Check to see if log was rotated
    if len(log_lines) < monitor_obj["last_line_read"]:
        monitor_obj["last_line_read"] = 0
        print ("Log Rotated: %s" % str(monitor_obj["location"]))

    monitor_obj["last_line_read"] = len(log_lines)

    return log_lines

def parse_delimited_file(log_lines, read_start_line, monitor_config):
    first_line_read = False
    parsed_data = []
    read_start_line = read_start_line * -1

    for line in log_lines[read_start_line:]:
        if (monitor_config["has_header"] == True and first_line_read == False):
            #Skip first line
            first_line_read = True
        else:
            fields = line.split(monitor_config["delimiter"])

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
                    data_object = {"label": entry["label"], "value":entry["indexes"][0]}
                else:
                    print ("No index value for label: %s" % (entry["label"]))
                    data_object = {}

                parsed_data.append(data_object)

            # Add the aditional data lines to the parsed data
            for additional_field in monitor_config["additional_fields"]:
                parsed_data.append(additional_field)

        first_line_read = True

    return parsed_data
