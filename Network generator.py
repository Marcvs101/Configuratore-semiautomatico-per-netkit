lab_conf = open("lab.conf",mode='r')
lab_conf_lines = lab_conf.readlines()
lab_conf.close()

topology = {}

for i in lab_conf_lines:
	if (i.strip() == ""):
	print("skip")
	else:
	device = i[:i.find("[")].strip()
	interface = i[i.find("[")+1:i.find("]")].strip()
	domain = i[i.find("=")+1:].strip()

	if not (domain in topology):
		topology[domain] = {}
		topology[domain]["devices"] = {}
		topology[domain]["address"] = "_NOT_SET"
		topology[domain]["mask"] = "_NOT_SET"
		topology[domain]["type"] = "_NOT_SET"

	topology[domain]["devices"][device] = {}
	topology[domain]["devices"][device][interface] = "_NOT_SET"

for i in topology:
	if "tap" in i:
	print("skip")
	else:
	print("Input network address for domain "+i+" (ex. 1.2.3.4/24)")
	addr = input(">:").strip()
	while (addr == "" or addr.count(".")!=3 or addr.count("/")!=1):
		print("Format not recognized, retry")
		addr = input(">:").strip()
	addr = addr.split("/")
	topology[i]["address"]=addr[0]
	topology[i]["mask"]=addr[1]
	print("Addressing "+addr[0]+" and netmask "+addr[1]+" assigned to domain "+i+"\n")
	
	print("Input network addressing protocol for domain "+i+" (DHCP or STATIC)")
	type = input(">:").strip().lower()
	while (type != "dhcp" and type != "static"):
		print("Format not recognized, retry")
		type = input(">:").strip().lower()
	topology[i]["type"] = type
	print("Network type "+type+" assigned to domain "+i+"\n")

for i in topology:
        if "tap" in i:
	print("skip")
	else:
	if topology[i]["type"] == "dhcp":
		print("DHCP configuration for domain "+i)
		print("Input DHCP server from list")
		for j in topology[i]["devices"]:
		print(" - "+j)

		srvr = input(">:").strip().lower()
		while (not (srvr in topology[i]["devices"].lower())):
		print("Warning, device not in list, retry")
		srvr = input(">:").strip().lower()

		print("Input static address for dhcp server (no netmask)")
		addr = input(">:").strip()
		while (addr == "" or addr.count(".")!=3):
		print("Format not recognized, retry")
		addr = input(">:").strip()

		topology[i]["devices"][srvr][ topology[i]["devices"][srvr].keys()[0] ] = addr

		print(srvr + "appointed as server with address "+addr+", all orthers will be slaves\n")

	else:
		print("static!")



print(topology)
