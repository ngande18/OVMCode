
**Gather and Disk Addition  VM  from OVM**
---------------------------

```
This script will connect to OVM and provide  following Information

```

If you don't Specify the username - it will assume default user as admin and ask for password

**Actions:**

```    listvms     - It will list all VMs on the OVM with corresponding Server where it is hosted
       listsrvs    - It will list all OVS servers
       showvmd     - List of all disk attached to particular VM
       srvdisks    - List disks attached to OVS server
       adddisks    - It will take your answer file and  will create all commands which you need to run on OVM
                       - adddisks action will do following checks
                       - It will validate your answerfile by checking following
                               -  Check any duplication slot numbers in your file
                               -  Check any duplication on provided disks
                               -  Check any duplicates in the disk names
                               -  It will validate all slot numbers - whether it is used already on the VM
                               -  Will check if the disknames are already used on the VM
                               -  Will check if the physical disks are already attached to VM
```

**Answer File Specification:**

        * It should be comma sperated
        * one disk info per one line
        * Header Needs to be added

**Sample  answer file:**

```
        slot,disk,sharble,diskname
        12,6005076810810103F000000000000056,NO,a0680o3odbsd415IBM-OS
        13,6005076810810103F000000000000057,nO,a0680o3odbsd415IBM-swap
        14,6005076810810103F00000000000006D,YES,+ocr_vote1-a0680o3odbsd415_416_417
```

*** Sample Commnds: ***

**Help**

```
./getovminfo --help
usage: getovminfo [-h] [-u [USER]] [-p [PASSWD]] [-v [VM]] [-sr [SRV]]
                  [-a [ANS]] [-d [{dal3,pok3}]]
                  [{listvms,listsrvs,showvmd,srvdisks,adddisks}]

Gather Server/VMs info

positional arguments:
  {listvms,listsrvs,showvmd,srvdisks,adddisks}
                        Actions to Perform

optional arguments:
  -h, --help            show this help message and exit
  -u [USER], --user [USER]
                        OVM Username
  -p [PASSWD], --passwd [PASSWD]
                        OVM Password
  -v [VM], --vm [VM]    VM Name
  -sr [SRV], --srv [SRV]
                        Server Name
  -a [ANS], --ans [ANS]
                        Answerfile for DiskAddition in CSV
  -d [{dal3,pok3}], --dc [{dal3,pok3}]
                        Which DataCenter to Workon

```
**GetListVMs**

```
 ./getovminfo listvms -u admin -p <password> --dc pok3
        NAME                     OVMID                VMSTATUS   CPUs    MEM        OVSHOST
a0710o3oappp312      0004fb0000060000a330d5e8a455e048 RUNNING         64   524291 a0001p5hovsp307
a0710o3odbsp311      0004fb00000600003a90aec2979a7f8f RUNNING         24   196611 a0001p5hovsp307
a0264o3oappp347      0004fb0000060000363dda50239c4f79 RUNNING          4     8195 a0001p5hovsp323
a0264o3odbsp306      0004fb00000600002a8f9498a4f798a7 RUNNING         64   262147 a0001p5hovsp312
a0264o1owebp333      0004fb000006000086b8cd4c868e5139 RUNNING         32   131075 a0001p5hovsp312
a0264o3oappp316      0004fb0000060000e7de918f80df1186 RUNNING          4    16387 a0001p5hovsp324
a0264o3odbsp317      0004fb00000600003d91ef9df677ecc8 RUNNING         24    65539 a0001p5hovsp324
a0264o3oappp339      0004fb0000060000d69b6a267246f560 RUNNING          8    32771 a0001p5hovsp316
a0127o3wappp308      0004fb000006000087d102b93bbce4d7 RUNNING          4     8195 a0001p5hovsp302

```
**ListServers:**

```
./getovminfo listsrvs -u admin -p <password> --dc pok3
        NAME                   SRVSTATUS                  SERIALNO
a0001p5hovsp329      RUNNING                        J1004873
a0001p5hovsp322      RUNNING                        J1003V8V
a0001p5hovsp320      RUNNING                        J1003V8W
a0001p5hovsp321      RUNNING                        J1003V9A
a0001p5hovsp319      RUNNING                        J1003V8Y
a0001p5hovsp332      RUNNING                        J100733G
a0001p5hovsp328      RUNNING                        J1004871
a0001p5hovsp316      RUNNING                        J1003V98
a0001p5hovsp308      RUNNING                        J1003WP6
```

**Disks Attached to VM**

```
 ./getovminfo showvmd -u admin -p <password>  --dc dal3 --vm a0680o3odbsd415
a0680o3odbsd415      0004fb0000060000208e342be250381e         RUNNING
Gathering SCSIID 0 Disk information
Gathering SCSIID 1 Disk information
Gathering SCSIID 2 Disk information
Gathering SCSIID 3 Disk information

```
It will Create a file in your current Directory

```
# ls -lrt | tail -1
-rw------- 1 ngande users    1439 Mar  5 16:24 a0680o3odbsd415_diskinfo.csv
```

**Disks attached to OVS server**

```
 ./getovminfo srvdisks -u admin -p <password>  --dc dal3 --srv a0001p5hovsd325
a0001p5hovsd325      RUNNING                        J1004862

```
It will Create a file in your current Directory

```
# ls -lrt | tail -1
-rw------- 1 ngande users   30299 Mar  5 16:35 a0001p5hovsd325_diskinfo.csv

```

**Attach disks to VMs**