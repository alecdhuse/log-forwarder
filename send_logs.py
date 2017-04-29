#!/usr/local/bin/python3.0

import apache_tools
import json
import log_tools
import os
import sys
import urllib.request

from datetime import datetime

def check_monitors(config_obj):
    for monitor in config_obj['monitor']:

        #find send_to object
        log_destination_config = {}

        for connection in config_obj['connections']:
            if connection['name'] == monitor["send_to"]:
                log_destination_config = connection
                break

        # Proccess the various supported log types
        if monitor["type"] == "apache access combined":
            log_lines = log_tools.read_single_line_log_file(monitor["location"])

            # Check to see if log was rotated
            if len(log_lines) < monitor["last_line_read"]:
                monitor["last_line_read"] = 0
                print ("Log Rotated: %s" % str(monitor["location"]))

            # Parse Apache access combined
            log_list = apache_tools.read_apache_logfile(log_lines, monitor["last_line_read"])
            line_count = 0

            for log_entry in log_list:
                send_success = proccess_event(monitor, log_destination_config, log_entry)
                line_count = line_count + 1

    config_obj.write_config()

def config_load():
    config_settings = {}

    try:
        script_dir = os.path.dirname(__file__)
        config_file = "config.json"
        file_path = os.path.join(script_dir, config_file)

        if os.path.exists(file_path):
            json_file = open(file_path)
            config_settings = json.load(json_file)

    except:
        print ("Error loading config file.")

    return config_settings

def config_save(config_object):
    try:
        script_dir = os.path.dirname(__file__)
        config_file = "config.json"
        file_path = os.path.join(script_dir, config_file)

        with open(file_path, 'w') as outfile:
            json.dump(config_settings, outfile, sort_keys = True, indent = 4)

    except:
        print ("Could not write config file.")

def main():
    config_obj = config_load()
    check_monitors(config_obj)

def proccess_event(monitor_config, destination_config, log_data):
    host_id = monitor_config["host_id"]

    if destination_config['type'] == "web_request":
        try:
            post_data = {
                "time": log_data["time"],
                "host": host_id,
                "sourcetype": "access_combined",
                "event": log_data
            }

            data = json.dumps(post_data).encode('utf8')
            auth_header = "Splunk %s" % destination_config["token"]
            headers = {'Authorization' : auth_header}

            req = urllib.request.Request(destination_config["address"], data, headers)
            response = urllib.request.urlopen(req)
            read_response = response.read()

            try:
                response_json = json.loads(str(read_response)[2:-1])

                if "text" in response_json:
                    if response_json["text"] == "Success":
                        post_success = True
                    else:
                        post_success = False
            except:
                post_success = False

            if post_success == True:
                # Update last line and time read
                monitor_config["last_line_read"] = monitor_config["last_line_read"] + 1
                monitor_config["last_time_read"] = int(datetime.now().strftime('%s'))
            else:
                print ("Error sending request, server responded with error.")
                break

        except Exception as err:
            post_success = False
            print ("Error sending request")
            print (str(err))

    return post_success

def test_apache():
    script_dir = os.path.dirname(__file__)
    log_file = "test logs/Apache-WordPress.log"
    file_path = os.path.join(script_dir, log_file)
    log_list = apache_tools.read_apache_logfile(file_path)

    for l in log_list:
        r = l["resource"]
        vs = apache_tools.read_variables(r)
        print (str(vs))

    # print (log_list)

main()
