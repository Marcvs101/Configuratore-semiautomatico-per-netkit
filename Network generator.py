import os

#Convert /num to a.b.c.d
def netmsk_gen(num):
    num = int(num.strip())
    b_num = ["","","",""]
    for i in range(0,num):
        b_num[i//8] = b_num[i//8] + "1"
    for i in range(num,32):
        b_num[i//8] = b_num[i//8] + "0"
    return "" + str(int(b_num[0],2)) + "." + str(int(b_num[1],2)) + "." + str(int(b_num[2],2)) + "." + str(int(b_num[3],2))

#Load file in cache
lab_conf = open("lab.conf",mode='r')
lab_conf_lines = lab_conf.readlines()
lab_conf.close()

#Initialize structures
topology = {}
files = {}


#First pass: get basic info from lab.conf
print("FIRST PASS\nParsing lab.conf file to build topology\n")
for i in lab_conf_lines:
    if (i.strip() == ""):
        #Empty line, skip
        print("Skip empty line")
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

        #Add device to fileset
        if not (device in files):
            files[device] = {}


#Second pass: assign addresses to domains
print("SECOND PASS\nAssign addresses to domains\n")
for i in topology:
    if "tap" in i:
        #TAP handled differently
        print("Domain "+i+" recognized as TAP\n")
        topology[i]["type"] = "tap"
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


#Third pass: for each domain assign addresses to devices
print("THIRD PASS\nAssign addresses to each device of domain\n")
for i in topology:
    if "tap" in i:
        #TAP handled differently
        print("Skip tap interface")
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
            while (not (srvr in topology[i]["devices"])):
                print("Warning, device not in list, retry")
                srvr = input(">:").strip().lower()

            #Assign static address to server
            print("Input static address for dhcp server (no netmask)")
            addr = input(">:").strip()
            while (addr == "" or addr.count(".")!=3):
                print("Format not recognized, retry")
                addr = input(">:").strip()

            key = ""
            for k in topology[i]["devices"][srvr].keys():
                key = k
            topology[i]["devices"][srvr][key] = addr

            print(srvr + " appointed as server with address "+addr+", all orthers will be slaves\n")
            #End of DHCP handler
            #Note, only server has an assigned address, all others have "_NOT_SET"
        else:
            #Static Handler
            print("Static configuration for domain "+i)
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
                addr2 = ""+addr2split[0]+"."+addr2split[1]+"."+addr2split[2]+"."+str(int(addr2split[3])+1)
                dev1 = devicelist[0]
                dev2 = devicelist[1]

                key = ""
                for k in topology[i]["devices"][dev1].keys():
                    key = k
                topology[i]["devices"][dev1][key] = addr1

                key = ""
                for k in topology[i]["devices"][dev2].keys():
                    key = k
                topology[i]["devices"][dev2][key] = addr2

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

                    key = ""
                    for k in topology[i]["devices"][dev1].keys():
                        key = k
                    topology[i]["devices"][dev1][key] = addr

                    print("Address "+addr+" assigned to device "+dev1+"\n")

                    #Manually configure dev2
                    print("Manually assign address for "+dev2)
                    addr = input(">:").strip()
                    while (addr == "" or addr.count(".")!=3):
                        print("Format not recognized, retry")
                        addr = input(">:").strip()

                    key = ""
                    for k in topology[i]["devices"][dev2].keys():
                        key = k
                    topology[i]["devices"][dev2][key] = addr
                    
                    print("Address "+addr+" assigned to device "+dev2+"\n")

                #Line separator
                print(" ")

                #End of /31 handler
            else:
                #General netmask handler
                #Manual enumeration, for now
                for j in topology[i]["devices"]:
                    print("Manually assign address for "+j)
                    addr = input(">:").strip()
                    while (addr == "" or addr.count(".")!=3):
                        print("Format not recognized, retry")
                        addr = input(">:").strip()

                    key = ""
                    for k in topology[i]["devices"][j].keys():
                        key = k
                    topology[i]["devices"][j][key] = addr
                    
                    print("Address "+addr+" assigned to device "+j+"\n")
                #End of /any handler


#Prepare startup files
print("Preparing startup files for all devices\n")
for i in files:
    #Assign content to startup file of device i
    files[i]["startup"] = "/etc/init.d/networking restart\n\n"


#Fourth pass: for each domain, prepare all relevant file contents
print("FOURTH PASS\nPrepare file contents for each device\n")
for i in topology:
    if (topology[i]["type"] == "tap"):
        #TAP handled differently
        print("Skip tap interface")
    else:
        #Ask user which file to use
        print("For domain "+i+" use startup file (S) or network/interfaces (N/I)?")
        choice = input(">:").strip().lower()
        while (choice != "n" and choice != "s" and choice != "i" and choice != "startup" and choice != "network" and choice != "interfaces"):
            print("Format not recognized, retry")
            choice = input(">:").strip().lower()

        if (choice == "n" or choice == "network" or choice == "i" or choice == "interfaces"):
            #Use network/interfaces
            print("Using network/interfaces files for domain "+i+"\n")

            if (topology[i]["type"] == "dhcp"):
                #DHCP handler

                #Scan all devices in domain
                for dev in topology[i]["devices"]:
                    #Setup structure if not present
                    if not ("interfaces" in files[dev]):
                        files[dev]["interfaces"] = ""

                    #Select one interface -- ASSUME ONE INTERFACE PER DEVICE IN NETWORK
                    iface = ""
                    for k in topology[i]["devices"][dev].keys():
                        iface = k

                    if (topology[i]["devices"][dev][iface] == "_NOT_SET"):
                        #Not server
                        files[dev]["interfaces"] = files[dev]["interfaces"] + "auto eth" + iface + "\n"
                        files[dev]["interfaces"] = files[dev]["interfaces"] + "iface eth" + iface + " inet dhcp\n\n"
                    else:
                        #Server found
                        files[dev]["interfaces"] = files[dev]["interfaces"] + "auto eth" + iface + "\n"
                        files[dev]["interfaces"] = files[dev]["interfaces"] + "iface eth" + iface + " inet static\n"
                        files[dev]["interfaces"] = files[dev]["interfaces"] + "\taddress " + topology[i]["devices"][dev][iface] + "\n"
                        files[dev]["interfaces"] = files[dev]["interfaces"] + "\tnetmask " + netmsk_gen(topology[i]["mask"]) + "\n\n"

                #End of DHCP handler
            else:
                #Static addressing handler

                #Scan all devices in domain
                for dev in topology[i]["devices"]:
                    #Setup structure if not present
                    if not ("interfaces" in files[dev]):
                        files[dev]["interfaces"] = ""

                    #Select one interface -- ASSUME ONE INTERFACE PER DEVICE IN NETWORK
                    iface = ""
                    for k in topology[i]["devices"][dev].keys():
                        iface = k

                    #Flush static values
                    files[dev]["interfaces"] = files[dev]["interfaces"] + "auto eth" + iface + "\n"
                    files[dev]["interfaces"] = files[dev]["interfaces"] + "iface eth" + iface + " inet static\n"
                    files[dev]["interfaces"] = files[dev]["interfaces"] + "\taddress " + topology[i]["devices"][dev][iface] + "\n"
                    files[dev]["interfaces"] = files[dev]["interfaces"] + "\tnetmask " + netmsk_gen(topology[i]["mask"]) + "\n\n"

                #End of static handler

            #End of interfaces handler
        else:
            #Use startup files
            print("WARN: Startup files are buggy, please check them manually after generation")
            print("WARN: Routing is not yet implemented, please do it manually")
            print("Using .startup files for domain "+i+"\n")

            if (topology[i]["type"] == "dhcp"):
                #DHCP handler

                #Scan all devices in domain
                for dev in topology[i]["devices"]:
                    #Setup structure if not present
                    if not ("startup" in files[dev]):
                        files[dev]["startup"] = ""

                    #Select one interface -- ASSUME ONE INTERFACE PER DEVICE IN NETWORK
                    iface = ""
                    for k in topology[i]["devices"][dev].keys():
                        iface = k

                    if (topology[i]["devices"][dev][iface] == "_NOT_SET"):
                        #Not server
                        files[dev]["startup"] = files[dev]["startup"] + "dhclient eth" + iface + "\n\n"
                    else:
                        #Server found
                        files[dev]["startup"] = files[dev]["startup"] + "ip link set eth" + iface + " up\n"
                        files[dev]["startup"] = files[dev]["startup"] + "ip addr add " + topology[i]["devices"][dev][iface] + "/" + topology[i]["mask"] + " dev eth" + iface + "\n"

                #End of DHCP handler

            else:
                #Static addressing handler

                #Scan all devices in domain
                for dev in topology[i]["devices"]:
                    #Setup structure if not present
                    if not ("startup" in files[dev]):
                        files[dev]["startup"] = ""

                    files[dev]["startup"] = files[dev]["startup"] + "ip link set eth" + iface + " up\n"
                    files[dev]["startup"] = files[dev]["startup"] + "ip addr add " + topology[i]["devices"][dev][iface] + "/" + topology[i]["mask"] + " dev eth" + iface + "\n\n"

                #End of static handler

            #End of startup handler


#Fifth pass: handle dhcp servers
print("FIFTH PASS\nHandling DHCP servers\n")
for i in topology:

    #Look for a dhcp domain among the ones i is connected to
    if (topology[i]["type"] == "dhcp"):

        #Scan all devices
        for dev in topology[i]["devices"]:

            #Select one interface -- ASSUME ONE INTERFACE PER DEVICE IN NETWORK
            iface = ""
            for k in topology[i]["devices"][dev].keys():
                iface = k

            #Look for DHCP server
            if (topology[i]["devices"][dev][iface] != "_NOT_SET"):

                #Setup structure if not present
                if not ("dhcp" in files[dev]):
                    files[dev]["dhcp"] = "default-lease-time 3600;\noption domain-name-servers 8.8.8.8;\n\n"

                #Device dev is server
                print("Handling DHCP server configuration for server "+dev+" on network "+topology[i]["address"]+"/"+topology[i]["mask"])
                print("WARN: Address range is not yet checked, the program will not throw errors for invalid ranges")

                #Ask for DHCP range
                print("Define minimum assignable address for DHCP server "+dev+" on network "+topology[i]["address"]+"/"+topology[i]["mask"])
                print("Please use a.b.c.d format")
                min_addr = input(">:").strip()
                while (min_addr == "" or min_addr.count(".")!=3):
                    print("Format not recognized, retry")
                    min_addr = input(">:").strip()

                print("Define maximum assignable address for DHCP server "+dev+" on network "+topology[i]["address"]+"/"+topology[i]["mask"])
                print("Please use a.b.c.d format")
                max_addr = input(">:").strip()
                while (max_addr == "" or max_addr.count(".")!=3):
                    print("Format not recognized, retry")
                    max_addr = input(">:").strip()

                print("Address range "+min_addr+" - "+max_addr+" selected for this DHCP configuration\n")
                
                #Prepare content
                files[dev]["dhcp"] = files[dev]["dhcp"] + "subnet " + topology[i]["address"] + " netmask " + netmsk_gen(topology[i]["mask"]) + " {\n"
                files[dev]["dhcp"] = files[dev]["dhcp"] + "\trange " + min_addr + " " + max_addr + ";\n"
                files[dev]["dhcp"] = files[dev]["dhcp"] + "\toption routers " + topology[i]["devices"][dev][iface] + ";\n"
                files[dev]["dhcp"] = files[dev]["dhcp"] + "}\n\n"

                files[dev]["startup"] = files[dev]["startup"] + "/etc/init.d/dhcp3-server start\n"


#Sixth pass: write files to disk
print("SIXTH PASS\nWrite files to disk\n")
for dev in files:
    for file in files[dev]:
        if (file == "startup"):
            #Startup file handler
            f = open(dev+".startup","w")
            print(files[dev][file].strip(),file=f)
            f.close()
        elif (file == "interfaces"):
            #Network/interfaces file handler

            #Make appropriate directories
            if not os.path.exists(dev+"/etc/network"):
                os.makedirs(dev+"/etc/network")

            #Write to file
            f = open(dev+"/etc/network/interfaces","w")
            print(files[dev][file].strip(),file=f)
            f.close()
        elif (file == "dhcp"):
            #Network/interfaces file handler

            #Make appropriate directories
            if not os.path.exists(dev+"/etc/dhcp3"):
                os.makedirs(dev+"/etc/dhcp3")

            #Write to file
            f = open(dev+"/etc/dhcp3/dhcpd.conf","w")
            print(files[dev][file].strip(),file=f)
            f.close()



print("\nEND OF FUNCTIONALITY FOR NOW\nDUMPING DEBUG INFO\n")

#Debug
print(topology)
print(" ")
input("quit")
