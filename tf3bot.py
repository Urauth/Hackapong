def handle(data):
	return data;

def rotation(data):		
	if "ball" in data:	
		prevX=bX
		prevY=bY
		bX = data["ball"]["pos"]["x"]
		bY = data["ball"]["pos"]["y"]
		rot = (bY-prevY)/(bX-prevX)
		return rot


