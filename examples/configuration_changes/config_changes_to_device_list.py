#!/usr/bin/env python
# Purpose:   Script commands to group of Cisco devices with success/failure feedback.

import sys
from __future__ import print_function, unicode_literals
from netmiko import ConnectHandler
from getpass import getpass


def usage(ext):
    # exit with description and command line example
    print("\nInput file should contain list of switch IP addresses.")
    print("Commands should be the commands you wish to run on your")
    print('network devices enclosed in "quotes".')
    print(
        "Results key: # = enable mode, * = successful command, w = write mem, ! = command failure"
    )
    print("\nusage:")
    print(
        ("\n%s <input file>" % sys.argv[0]),
        '"command1"',
        '"command2"',
        '"command3"',
        "wr",
    )
    sys.exit(ext)


def main():
    inputfile = ""
    config_commands = ""

    try:
        inputfile = open(sys.argv[1], "r")
    except (IndexError, IOError):
        usage(0)

    if len(sys.argv) > 2:
        # list of command line switch commands
        config_commands = sys.argv[2:]

    print("Switch configuration updater. Please provide login information.\n")
    # Get username and password information.
    username = input("Username: ")
    password = getpass("Password: ")
    enasecret = getpass("Enable Secret: ")

    print("{}{:<20}{:<40}{:<20}".format("\n", "IP Address", "Name", "Results"), end="")

    for switchip in inputfile:
        ciscosw = {
            "device_type": "cisco_ios",
            "ip": switchip.strip(),
            "username": username.strip(),
            "password": password.strip(),
            "secret": enasecret.strip(),
        }
        print()
        print("{:<20}".format(switchip.strip()), end="", flush=True)
        try:
            # Connect to switch and enter enable mode.
            net_connect = ConnectHandler(**ciscosw)
        except:
            print("** Failed to connect.", end="", flush=True)
            continue

        prompt = net_connect.find_prompt()
        # Print out the prompt/hostname of the device
        print("{:<40}".format(prompt), end="", flush=True)
        try:
            # Ensure we are in enable mode and can make changes.
            if "#" not in prompt[-1]:
                net_connect.enable()
                print("#", end="", flush=True)
        except:
            print("Unable to enter enable mode.", end="", flush=True)
            continue

        else:
            for cmd in config_commands:
                # Make requested configuration changes.
                try:
                    if cmd in ("w", "wr"):
                        output = net_connect.save_config()
                        print("w", end="", flush=True)
                    else:
                        output = net_connect.send_config_set(cmd)
                        if "Invalid input" in output:
                            # Unsupported command in this IOS version.
                            print("Invalid input: ", cmd, end="", flush=True)
                        print("*", end="", flush=True)
                except:
                    # Command failed! Stop processing further commands.
                    print("!")
                    break

        net_connect.disconnect()


if __name__ == "__main__":
    main()
