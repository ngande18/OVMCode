
**Gather VM info from OVM**
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

