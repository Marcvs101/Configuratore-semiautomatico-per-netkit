lab_conf = open("lab.conf",mode='r')
lab_conf_lines = lab_conf.readlines()
lab_conf.close()

topology = {}

for i in lab_conf_lines:
    if (i.strip() == ""):
        #Empty line, skip
        print("skip")
    else:
        #Parsing
        device = i[:i.find("[")].strip()
    interface = i[i.find("[")+1:i.find("]")].strip()
    domain = i[i.find("=")+1:].strip()

    #Register domain if necessary
    if not (domain in topology):
        topology[domain] = {}
        topology[domain]["devices"] = {}
        topology[domain]["address"] = "_NOT_SET"
        topology[domain]["mask"] = "_NOT_SET"
        topology[domain]["type"] = "_NOT_SET"

    #Assign device to domain
    topology[domain]["devices"][device] = {}
    topology[domain]["devices"][device][interface] = "_NOT_SET"

for i in topology:
    if "tap" in i:
        #TAP handled differently
        print("skip")
    else:
        #Assign address to domain
        print("Input network address for domain "+i+" (ex. 1.2.3.4/24)")
        addr = input(">:").strip()
        while (addr == "" or addr.count(".")!=3 or addr.count("/")!=1):
            print("Format not recognized, retry")
            addr = input(">:").strip()
        addr = addr.split("/")
        topology[i]["address"]=addr[0]
        topology[i]["mask"]=addr[1]
        print("Addressing "+addr[0]+" and netmask "+addr[1]+" assigned to domain "+i+"\n")

        #Assign addressing protocol to domain
        print("Input network addressing protocol for domain "+i+" (DHCP or STATIC)")
        ptype = input(">:").strip().lower()
        while (ptype != "dhcp" and ptype != "static"):
            print("Format not recognized, retry")
            ptype = input(">:").strip().lower()
        topology[i]["type"] = ptype
        print("Network type "+ptype+" assigned to domain "+i+"\n")

for i in topology:
    if "tap" in i:
        #TAP handled differently
        print("skip")
    else:
        if topology[i]["type"] == "dhcp":
            #DHCP Handler
            print("DHCP configuration for domain "+i)

            #List all members of the domain
            print("Input DHCP server from list")
            for j in topology[i]["devices"]:
                print(" - "+j)

            #Select one member of domain to be elected as server
            srvr = input(">:").strip().lower()
            while (not (srvr in topology[i]["devices"].lower())):
                print("Warning, device not in list, retry")
                srvr = input(">:").strip().lower()

            #Assign static address to server
            print("Input static address for dhcp server (no netmask)")
            addr = input(">:").strip()
            while (addr == "" or addr.count(".")!=3):
                print("Format not recognized, retry")
                addr = input(">:").strip()

            topology[i]["devices"][srvr][ topology[i]["devices"][srvr].keys()[0] ] = addr

            print(srvr + "appointed as server with address "+addr+", all orthers will be slaves\n")
            #End of DHCP handler
            #Note, only server has an assigned address, all others have "_NOT_SET"
        else:
            #Static Handler
            print("static!")
            if (topology[i]["mask"]=="31"):
                #Special /31 handler, for convenience
                #Build sorted device list for /31 link
                devicelist = list()
                for j in topology[i]["devices"]:
                    devicelist.append(j)
                devicelist.sort()

                #Assign automatically addresses to devices in /31 link
                addr1 = topology[i]["address"]
                addr2split = topology[i]["address"].split(".")
                addr2 = ""+addr2split[0]+":"+addr2split[1]+":"+addr2split[2]+":"+str(int(addr2split[3])+1)
                dev1 = devicelist[0]
                dev2 = devicelist[1]
                topology[i]["devices"][dev1][ topology[i]["devices"][dev1].keys()[0] ] = addr1
                topology[i]["devices"][dev2][ topology[i]["devices"][dev2].keys()[0] ] = addr2

                #Ask for user confirmation
                print("Assigned address "+addr1+" for device "+dev1+" and address "+addr2+" for device "+dev2+" over /31 domain "+i)
                print("Are the assigned adddresses good? (Y/N)")
                confrm = input(">:").strip().lower()
                while (confrm != "y" and confrm != "n" and confrm != "yes" and confrm != "no"):
                    print("Format not recognized, retry")
                    confrm = input(">:").strip().lower()

                #Handle the no case
                if (confrm == "n" or confrm == "no"):
                    #Manually configure dev1
                    print("Manually assign address for "+dev1)
                    addr = input(">:").strip()
                    while (addr == "" or addr.count(".")!=3):
                        print("Format not recognized, retry")
                        addr = input(">:").strip()
                    topology[i]["devices"][dev1][ topology[i]["devices"][dev1].keys()[0] ] = addr
                    print("Address "+addr+" assigned to device "+dev1+"\n")

                    #Manually configure dev2
                    print("Manually assign last address digit for "+dev2)
                    addr = input(">:").strip()
                    while (addr == "" or addr.count(".")!=3):
                        print("Format not recognized, retry")
                        addr = input(">:").strip()
                    topology[i]["devices"][dev2][ topology[i]["devices"][dev2].keys()[0] ] = addr
                    print("Address "+addr+" assigned to device "+dev2+"\n")
            else:
                #General netmask handler
                print("other mask!")



print(topology)

