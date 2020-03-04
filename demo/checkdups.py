import argparse
import sys
import getpass
import json
import requests
import urllib3
import time
import csv
import copy


def CheckDups(myfile):
    res = 200
    CHECKFILE = myfile
    with open(CHECKFILE, "r") as AnsF:
        csv_reader = csv.reader(AnsF)
        next(csv_reader)
        slot_list = [line[0] for line in csv_reader]
        with open(CHECKFILE, "r") as AnsF:
            csv_reader = csv.reader(AnsF)
            next(csv_reader)
            disk_list = [line[1] for line in csv_reader]
            with open(CHECKFILE, "r") as AnsF:
                csv_reader = csv.reader(AnsF)
                next(csv_reader)
                name_list = [line[3] for line in csv_reader]

    for item in slot_list:
        if slot_list.count(item) > 1:
            Repeats = slot_list.count(item)
            print("slot {} used {} times in your answer file".format(item, Repeats))
            res = 999

    for item in disk_list:
        if disk_list.count(item) > 1:
            Repeats = disk_list.count(item)
            print("slot {} used {} times in your answer file".format(item, Repeats))
            res = 999

    for item in name_list:
        if name_list.count(item) > 1:
            Repeats = name_list.count(item)
            print("slot {} used {} times in your answer file".format(item, Repeats))
            res = 999

    return res


my_res = CheckDups("demo/ans.csv")
print(my_res)

# print(slot_list)
# print(disk_list)
# print(name_list)

