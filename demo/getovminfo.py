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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


defuser = "admin"
dclist = ["dal3", "pok3"]
actions = ["listvms", "listsrvs", "showvmd", "srvdisks"]
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

    # for row in output_list:
    #     print(type(row))
    #     print(row)

    return (current_dlist, scsi_idlist, output_list)


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
        (current_dlist, scsi_idlist, output_list) = vmShowd(args, baseUri, "Vm")
        WriteToFile(fname, fieldnames, output_list)
        print(scsi_idlist)
        print(current_dlist)

    if args.action == "srvdisks" and (args.srv):
        fname = "{}_diskinfo.csv".format(args.srv)
        fieldnames = [
            "DISKTYPE",
            "SIZE",
            "SHAREABLE",
            "NAME",
            "VENDOR",
            "DISKINFO",
        ]
        (diskid_list, output_list) = srvDiskList(args, baseUri, "Server")
        WriteToFile(fname, fieldnames, output_list)
        print(diskid_list)


if __name__ == "__main__":
    main()

