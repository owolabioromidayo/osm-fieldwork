#!/usr/bin/python3

#
#   Copyright (C) 2020, 2021, 2022, 2023 Humanitarian OpenstreetMap Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import argparse
import logging
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import xmltodict

# Instantiate logger
log = logging.getLogger(__name__)


def main():
    """This is a program that reads in the ODK Instance file, which is in XML,
    and converts it to an OSM XML file so it can be viewed in an editor.
    """
    parser = argparse.ArgumentParser(description="Convert ODK XML instance file to OSM XML format")
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-i", "--instance", required=True, help="The instance file(s) from ODK Collect")
    # parser.add_argument("-o","--outfile", default='tmp.csv', help='The output file for JOSM')
    args = parser.parse_args()

    # if verbose, dump to the terminal
    if args.verbose is not None:
        logging.basicConfig(
            level=logging.DEBUG,
            format=("%(threadName)10s - %(name)s - %(levelname)s - %(message)s"),
            datefmt="%y-%m-%d %H:%M:%S",
            stream=sys.stdout,
        )    
    else:
        logging.basicConfig(
            level=logging.INFO,
            format=("%(threadName)10s - %(name)s - %(levelname)s - %(message)s"),
            datefmt="%y-%m-%d %H:%M:%S",
            stream=sys.stderr,
        )    
        
    xmlfiles = list()
    if args.instance.find("*") >= 0:
        toplevel = Path()
        for dir in toplevel.glob(args.instance):
            if dir.is_dir():
                xml = os.listdir(dir)
                # There is always only one XML file per instance
                full = os.path.join(dir, xml[0])
                xmlfiles.append(full)
    else:
        toplevel = Path(args.instance)
        if toplevel.is_dir():
            # There is always only one XML file per instance
            full = os.path.join(toplevel, os.path.basename(toplevel))
            xmlfiles.append(full + ".xml")

    # print(xmlfiles)

    # These are all generated by Collect, and can be ignored
    rows = list()
    for instance in xmlfiles:
        logging.info("Processing instance file: %s" % instance)
        with open(instance, "rb") as file:
            # Instances are small, read the whole file
            xml = file.read(os.path.getsize(instance))
            doc = xmltodict.parse(xml)
            fields = list()
            tags = dict()
            data = doc["data"]
            for i, j in data.items():
                if j is None or i == "meta":
                    continue
                # print(f"tag: {i} == {j}")
                pat = re.compile("[0-9.]* [0-9.-]* [0-9.]* [0-9.]*")
                if pat.match(str(j)):
                    if i == "warmup":
                        continue
                    gps = j.split(" ")
                    tags["lat"] = gps[0]
                    tags["lon"] = gps[1]
                    continue
                if type(j) == OrderedDict or type(j) == dict:
                    for ii, jj in j.items():
                        pat = re.compile("[0-9.]* [0-9.-]* [0-9.]* [0-9.]*")
                        if pat.match(str(jj)):
                            gps = jj.split(" ")
                            tags["lat"] = gps[0]
                            tags["lon"] = gps[1]
                            continue
                        if jj is None:
                            continue
                        # print(f"tag: {i} == {j}")
                        if type(jj) == OrderedDict or type(jj) == dict:
                            for iii, jjj in jj.items():
                                if jjj is not None:
                                    tags[iii] = jjj
                                    # print(iii, jjj)
                        else:
                            # print(ii, jj)
                            fields.append(ii)
                            tags[ii] = jj
                else:
                    if i[0:1] != "@":
                        tags[i] = j
        rows.append(tags)

    xml = os.path.basename(xmlfiles[0])
    tmp = xml.replace(" ", "").split("_")
    now = datetime.now()
    timestamp = f"_{now.year}_{now.hour}_{now.minute}"
    outfile = tmp[0] + timestamp + ".csv"

    # with open(outfile, "w", newline="") as csvfile:
    #     fields = list()
    #     for row in rows:
    #         for key in row.keys():
    #             if key not in fields:
    #                 fields.append(key)
    #     csv = csv.DictWriter(csvfile, dialect="excel", fieldnames=fields)
    #     csv.writeheader()
    #     for row in rows:
    #         csv.writerow(row)

    print("Wrote: %s" % outfile)


if __name__ == "__main__":
    """This is just a hook so this file can be run standlone during development."""
    main()
