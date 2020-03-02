import argparse
import sys
import getpass
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


defuser = "admin"
dclist = ["dal3", "pok3"]
actions = ["listvms", "listsrvs"]
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
    parser.add_argument(
        "-d", "--dcinfo", nargs="?", help="Which DataCenter to Workon", choices=dclist,
    )

    args = parser.parse_args()
    return args


def setdc(args):
    if args.dcinfo == "dal3":
        ovmserver = "10.131.26.21:7002"
    elif args.dcinfo == "pok3":
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


def main():
    args = parseargs()
    if not args.dcinfo:
        print("provide Correct dcinfo")
        sys.exit(0)
    elif args.dcinfo not in dclist:
        print("provide Correct DC Name")
        sys.exit(0)
    else:
        baseUri = setdc(args)

    if args.action in actions:
        if not args.user:
            args.user = input("OVM Username: ")
            args.passwd = getpass.getpass("Provide OVM" + args.user + "password :")
        else:
            args.passwd = getpass.getpass("Provide OVM admin password :")

    if args.action == "listvms":
        vmList(args, baseUri, "Vm")

    print("I am using listvms argument")
    print(args.dcinfo)
    print(args.user, args.passwd)
    print(args.action)
    print(baseUri)


if __name__ == "__main__":
    main()

