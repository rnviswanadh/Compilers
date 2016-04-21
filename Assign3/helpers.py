def preprocess(data):
	start = ""
	end = data
	while(end.find('eval')!=-1):
		pos = end.find('eval')
		start = start + end[:pos]
		end = end[pos:]
		print start+end
