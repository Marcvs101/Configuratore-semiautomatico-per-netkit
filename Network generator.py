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
	type = input(">:").strip().lower()
	while (type != "dhcp" and type != "static"):
		print("Format not recognized, retry")
		type = input(">:").strip().lower()
	topology[i]["type"] = type
	print("Network type "+type+" assigned to domain "+i+"\n")

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
				print("mask 31!")
				devicelist = 
			else:
				#General netmask handler
				print("other mask!")



print(topology)
