#!/usr/bin/env /usr/bin/python
##############################################

import argparse
import sys
import getpass
import json
import requests
import urllib3
import time
import csv
import copy
from operator import itemgetter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


defuser = "admin"
dclist = ["dal3", "pok3"]
actions = ["listvms", "listsrvs", "showvmd", "srvdisks", "adddisks"]
baseUri = ""
ovmserver = ""


def parseargs():

    parser = argparse.ArgumentParser(description="Gather Server/VMs info")
    parser.add_argument(
        "action",
        default="listvms",
        choices=actions,
        nargs="?",
        help="Actions to Perform",
    )
    parser.add_argument("-u", "--user", nargs="?", default=defuser, help="OVM Username")
    parser.add_argument("-p", "--passwd", nargs="?", help="OVM Password")
    parser.add_argument("-v", "--vm", nargs="?", help="VM Name")
    parser.add_argument("-sr", "--srv", nargs="?", help="Server Name")
    parser.add_argument(
        "-a", "--ans", nargs="?", help="Answerfile for DiskAddition in CSV"
    )
    parser.add_argument(
        "-d", "--dc", nargs="?", help="Which DataCenter to Workon", choices=dclist,
    )

    args = parser.parse_args()
    return args


def setdc(args):
    if args.dc == "dal3":
        ovmserver = "10.131.26.21:7002"
    elif args.dc == "pok3":
        ovmserver = "10.130.26.21:7002"
    return "https://" + ovmserver + "/ovm/core/wsapi/rest"


def OpenSess(args, baseUri, extrav):
    s = requests.session()
    s.auth = (args.user, args.passwd)
    s.verify = False
    s.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
    r = s.get(baseUri + "/" + extrav)
    if r.status_code != 200:
        sys.exit(r.status_code)
    else:
        return r
        r.close()


def CheckDups(args):
    res = 200
    CHECKFILE = args.ans
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


def vmList(args, baseUri, extrav):
    print(
        "{:^20} {:^30} {:^12} {:^5} {:^8} {:^15}".format(
            "NAME", "OVMID", "VMSTATUS", "CPUs", "MEM", "OVSHOST"
        )
    )
    res = OpenSess(args, baseUri, extrav)
    for i in res.json():
        #        print(json.dumps(i, indent=2, sort_keys=True))
        print(
            "{:20} {:30} {:12} {:5} {:8} {:15}".format(
                i["name"],
                i["id"]["value"],
                i["vmRunState"],
                i["cpuCount"],
                i["currentMemory"],
                i["serverId"]["name"],
            )
        )


def srvList(args, baseUri, extrav):
    print("{:^20} {:^30} {:^20}".format("NAME", "SRVSTATUS", "SERIALNO"))
    res = OpenSess(args, baseUri, extrav)
    for i in res.json():
        print(
            "{:20} {:30} {:20}".format(
                i["name"], i["serverRunState"], i["serialNumber"]
            )
        )


def Diskadd(args, baseUri, extrav):
    pass


def ValidateAnsFile(args, scsiids, cphydisks, sphydisks, disknames):
    validres = " "
    with open(args.ans, "r") as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        for line in csv_reader:
            if line[0] in scsiids:
                print(line[0] + " is already used on " + args.vm)
                validres = 999
                sys.exit(0)
            elif ("3" + line[1].lower()) in cphydisks:
                print(("3" + line[1]) + " is already attached on " + args.vm)
                validres = 999
                sys.exit(0)
            elif ("3" + line[1].lower()) not in sphydisks:
                print(("3" + line[1]) + " is not attached on " + args.srv)
                validres = 999
                sys.exit(0)
            elif line[3] in disknames:
                print(line[3] + " diskname is already used on " + args.vm)
                validres = 999
                sys.exit(0)
            else:
                validres = 200
    return validres


def srvDiskList(args, baseUri, extrav):
    output_list = []
    diskid_list = []
    res = OpenSess(args, baseUri, extrav)
    time.sleep(1)
    for i in res.json():
        if i["name"] == args.srv:
            print(
                "{:20} {:30} {:20}".format(
                    i["name"], i["serverRunState"], i["serialNumber"]
                )
            )
            for d in i["storageElementIds"]:
                extrav = "StorageElement/" + d["value"]
                pdres = OpenSess(args, baseUri, extrav)
                time.sleep(1)
                pdres_out = pdres.json()
                dname = str(pdres_out["deviceNames"][0])
                dname = dname.split("/dev/mapper/")[1]
                to_append = {
                    "DISKTYPE": pdres_out["type"],
                    "SIZE": (pdres_out["size"] / 1024 / 1024 / 1024),
                    "SHAREABLE": pdres_out["shareable"],
                    "NAME": pdres_out["name"],
                    "OVMID": pdres_out["id"]["value"],
                    "VENDOR": pdres_out["vendor"],
                    "DISKINFO": dname,
                }
                output_list.append(copy.deepcopy(to_append))
                diskid_list.append(dname)
    return (diskid_list, output_list)


def vmShowd(args, baseUri, extrav):
    res = OpenSess(args, baseUri, extrav)
    time.sleep(1)
    output_list = []
    scsi_idlist = []
    current_dlist = []
    currentN_list = []
    for i in res.json():
        if i["name"] == args.vm:
            print("{:20} {:55}".format(i["name"], i["vmRunState"]))
            for d in i["vmDiskMappingIds"]:
                if "CDROM" not in d["name"]:
                    extrav = "VmDiskMapping/" + d["value"]
                    dres = OpenSess(args, baseUri, extrav)
                    time.sleep(1)
                    dout = dres.json()
                    # for iter in range(len(dout)):
                    if "virtualDiskId" in dout and dout.get("storageElementId") == None:
                        extrav = "VirtualDisk/" + dout["virtualDiskId"]["value"]
                        pdres = OpenSess(args, baseUri, extrav)
                        time.sleep(1)
                        pdres_out = pdres.json()
                        pdres_out["vendor"] = " "
                        print(
                            "Gathering SCSIID "
                            + str(dout["diskTarget"])
                            + " Disk information"
                        )
                        to_append = {
                            "SCSIID": dout["diskTarget"],
                            "OVMID": dout["id"]["value"],
                            "DISKTYPE": pdres_out["diskType"],
                            "SIZE": (pdres_out["size"] / 1024 / 1024 / 1024),
                            "SHAREABLE": pdres_out["shareable"],
                            "NAME": pdres_out["name"],
                            "VENDOR": pdres_out["vendor"],
                            "DISKINFO": pdres_out["absolutePath"],
                        }
                        output_list.append(copy.deepcopy(to_append))
                        scsi_idlist.append(dout["diskTarget"])
                        currentN_list.append(pdres_out["name"])

                        # print(json.dumps(pdres_out, indent=2))
                        # print(
                        #     dout["diskTarget"],
                        #     dout["id"]["value"],
                        #     dout["virtualDiskId"]["value"],
                        #     dout["virtualDiskId"]["name"],
                        # )
                    elif (
                        "storageElementId" in dout
                        and dout.get("storageElementId") != None
                    ):
                        # print(json.dumps(dout, indent=2))
                        extrav = "StorageElement/" + dout["storageElementId"]["value"]
                        pdres = OpenSess(args, baseUri, extrav)
                        time.sleep(1)
                        pdres_out = pdres.json()
                        print(
                            "Gathering SCSIID "
                            + str(dout["diskTarget"])
                            + " Disk information"
                        )
                        dname = str(pdres_out["deviceNames"][0])
                        dname = dname.split("/dev/mapper/")[1]
                        to_append = {
                            "SCSIID": dout["diskTarget"],
                            "OVMID": dout["id"]["value"],
                            "DISKTYPE": pdres_out["type"],
                            "SIZE": (pdres_out["size"] / 1024 / 1024 / 1024),
                            "SHAREABLE": pdres_out["shareable"],
                            "NAME": pdres_out["name"],
                            "VENDOR": pdres_out["vendor"],
                            "DISKINFO": dname,
                        }

                        output_list.append(copy.deepcopy(to_append))
                        scsi_idlist.append(dout["diskTarget"])
                        current_dlist.append(dname)
                        currentN_list.append(pdres_out["name"])

    # for row in output_list:
    #     print(type(row))
    #     print(row)

    return (currentN_list, current_dlist, scsi_idlist, output_list)


def WriteToFile(fname, fieldnames, output_list):
    with open(fname, "w") as file_name:
        Final_output = csv.DictWriter(file_name, fieldnames=fieldnames)
        Final_output.writeheader()
        for line in output_list:
            Final_output.writerow(line)
    file_name.close()


def main():

    args = parseargs()
    if not args.dc:
        print("provide Correct DataCenter")
        sys.exit(0)
    elif args.dc not in dclist:
        print("provide Correct DC Name")
        sys.exit(0)
    else:
        baseUri = setdc(args)

    if args.action in actions:
        if not args.user:
            args.user = input("OVM Username: ")
            args.passwd = getpass.getpass("Provide OVM" + args.user + "password :")
        elif not args.passwd:
            args.passwd = getpass.getpass("Provide OVM admin password :")

    if args.action == "listvms":
        vmList(args, baseUri, "Vm")

    if args.action == "listsrvs":
        srvList(args, baseUri, "Server")

    if args.action == "showvmd" and (args.vm):
        fname = "{}_diskinfo.csv".format(args.vm)
        fieldnames = [
            "SCSIID",
            "OVMID",
            "DISKTYPE",
            "SIZE",
            "SHAREABLE",
            "NAME",
            "VENDOR",
            "DISKINFO",
        ]
        (currentN_list, current_dlist, scsi_idlist, output_list) = vmShowd(
            args, baseUri, "Vm"
        )
        WriteToFile(fname, fieldnames, output_list)
        print(currentN_list)

    if args.action == "srvdisks" and (args.srv):
        fname = "{}_diskinfo.csv".format(args.srv)
        fieldnames = [
            "DISKTYPE",
            "SIZE",
            "SHAREABLE",
            "NAME",
            "OVMID",
            "VENDOR",
            "DISKINFO",
        ]
        (diskid_list, output_list) = srvDiskList(args, baseUri, "Server")
        WriteToFile(fname, fieldnames, sorted(output_list, key=itemgetter("SIZE")))

    if args.action == "adddisks" and (args.srv) and (args.vm) and (args.ans):
        print("Validating Current Disk Layout and Answerfile")
        my_res = CheckDups(args)
        if my_res == 200:
            (currentN_list, current_dlist, scsi_idlist, output_list) = vmShowd(
                args, baseUri, "Vm"
            )
            (diskid_list, output_list) = srvDiskList(args, baseUri, "Server")
            res = ValidateAnsFile(
                args, scsi_idlist, current_dlist, diskid_list, currentN_list
            )
            if res == 200:
                print(
                    "Answer file and current disk Layout is  validated and Building Commands list........."
                )
                with open(args.ans, "r") as myansfile:
                    csv_reader = csv.reader(myansfile)
                    next(myansfile)
                    shareans = ""
                    for line in csv_reader:
                        for item in diskid_list:
                            if line[1].lower == item["DISKINFO"]:
                                if item["SHAREABLE"] == ["Y" "y"]["E" "e"]["S" "s"]:
                                    shareans = "Yes"
                                else:
                                    shareans = "No"
                                print(
                                    "edit PhysicalDisk id="
                                    + item["OVMID"]
                                    + "shareable="
                                    + shareans
                                    + "name="
                                    + line[3]
                                )


if __name__ == "__main__":
    main()

