#!/usr/bin/env python3

# This script allows you to make aur queries.
# See https://wiki.archlinux.org/title/Aurweb_RPC_interface
# Author: Andrew Shark <ashark linuxcomp ru>

import json
import sys
from urllib.parse import urlencode
from urllib.request import urlopen
import argparse


class AurJsonClient:
    def __init__(self):
        self.target_url = "https://aur.archlinux.org/rpc/v5"
        self.full_url = None

    def search(self, args, by):
        self.full_url = self.target_url + "/search"
        self.full_url += f"/{args}"
        values = {}
        if by:
            values["by"] = by
        params = urlencode(values)
        self.full_url = f"{self.full_url}?{params}"
        response = urlopen(self.full_url).read()
        return json.loads(response)

    def info(self, args):
        self.full_url = self.target_url + "/info"
        self.full_url += f"/{args}"
        params = urlencode({})
        self.full_url = f"{self.full_url}?{params}"
        response = urlopen(self.full_url).read()
        return json.loads(response)

    def print_results(self, data):
        print("Request url:\n  " + self.full_url)
        if data["type"] == "error":
            print(f"Error: {data["results"]}")
            return
        if not isinstance(data["results"], list):
            data["results"] = [data["results"], ]
        if data["results"]:
            print("Response:")
            for pkg in data["results"]:
                # print the name first, for convenience
                if "Name" in pkg:
                    print(f"  Name: {pkg["Name"]}")
                    print(f"  https://aur.archlinux.org/packages/{pkg["Name"]}")  # print link to aur page
                    del pkg["Name"]
                
                for prop in pkg:
                    print(f"    {prop}: {pkg[prop]}")
                print()
        else:
            print("Empty response.")


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(search_mode=1)  # sets options.search_mode to 1 by default
    parser.add_argument("-s",
                        "--search",
                        action="store_const",
                        const=1,
                        dest="search_mode",
                        help="Operate in search mode")
    parser.add_argument("-i",
                        "--info",
                        action="store_const",
                        const=0,
                        dest="search_mode",
                        help="Operate in info mode")
    parser.add_argument("-b",
                        "--by",
                        action="append",
                        choices=["name", "name-desc", "maintainer", "depends", "makedepends", "optdepends", "checkdepends"],
                        help="The name of the field to search in. Support multiple occurrences (see https://wiki.archlinux.org/title/Talk:Aurweb_RPC_interface#Use_several_by_arguments?)")

    options, unknown_args = parser.parse_known_args(sys.argv[1:])

    # Sometimes, user have to use "--" parameter, to pass some arguments that are otherwise recognized as options.
    # For example, ./script.py --search --by name -- -bin
    # Otherwise, that "-bin" argument is parsed as "-b" "in", which is unwanted.
    # So, here we delete that "--" parameter, if was presented.
    if len(unknown_args):
        if unknown_args[0] == "--":
            unknown_args.pop(0)

    try:
        assert len(unknown_args) == 1
    except AssertionError:
        print("You should use exactly one argument string.")
        print("Got:", unknown_args)
        print("""\
Usage example:
  Searching all packages, which names contain "-eap" (i.e. all EAP JetBrains IDEs):
    ./script.py --search --by name -- -eap
Note that usage of "--": it allows you to pass the string to search, which starts with dash
(in this case, the "-eap" string).\
""")
        exit(1)

    arg_str = unknown_args[0]
    ajc = AurJsonClient()
    if options.search_mode == 1:
        for single_by in options.by:
            result = ajc.search(arg_str, single_by)
            ajc.print_results(result)
    else:
        result = ajc.info(arg_str)
        ajc.print_results(result)


if __name__ == "__main__":
    main()
