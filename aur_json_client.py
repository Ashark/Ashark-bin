#!/usr/bin/env python3.12

# This script allows you to make aur queries.
# See https://wiki.archlinux.org/title/Aurweb_RPC_interface
# Author: Andrew Shark <ashark linuxcomp ru>

import json
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
    parser.set_defaults(search_mode=0)  # sets options.search_mode to 0 by default
    parser.add_argument("-s",
                        "--search",
                        action="store_const",
                        const=0,
                        dest="search_mode",
                        help="Operate in search mode")
    parser.add_argument("-i",
                        "--info",
                        action="store_const",
                        const=1,
                        dest="search_mode",
                        help="Operate in info mode")
    parser.add_argument("-b",
                        "--by",
                        action="append",
                        choices=["name", "name-desc", "maintainer", "depends", "makedepends", "optdepends", "checkdepends"],
                        help="The name of the field to search in. Support multiple occurrences (see https://wiki.archlinux.org/title/Talk:Aurweb_RPC_interface#Use_several_by_arguments?)")
    parser.add_argument("arg", help="String to search")
    
    options = parser.parse_args()
    
    ajc = AurJsonClient()
    if options.search_mode == 1:
        result = ajc.info(options.arg)
        ajc.print_results(result)
    else:
        for single_by in options.by:
            result = ajc.search(options.arg, single_by)
            ajc.print_results(result)


if __name__ == "__main__":
    main()
