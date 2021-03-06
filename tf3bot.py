import webbrowser
import math
import logging

class Vector(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def angleDeg(self, comparison):
        c = -1
        if ourside:
            c = 1
        return self.angleRad(comparison) * (180 / math.pi) * c

    def angleRad(self, comparison):
        a = self.x
        b = self.y
        c = comparison.x
        d = comparison.y

        atanSelf = math.atan2(self.x, self.y)
        atanComparison = math.atan2(comparison.x, comparison.y)

        return atanSelf - atanComparison

global name
name = ""

fieldHeight = 0
fieldWidth = 0

paddleHeight = 0
paddleWidth = 0

ballRadius = 0
tickInterval = 0

ourside=True

prevX = 0
prevY = 0 
currX = 0
currY = 0

dirX = 0
dirY = 0

arrivalVector = Vector(0,0)


def handle(data):	

	if 'ball' in data:
		collectValues(data);
		projectedY=projectedTarget(data)
		if 'left' in data:
			data = movePaddle(data, projectedY)
	return data

def direction(ballX, ballY):
	global currX
	currX=ballX
	global currY
	currY=ballY			
	
	global prevX
	global dirX
	dirX=currX-prevX
	global dirY
	global prevY
	dirY=currY-prevY
	
	prevY=currY
	prevX=currX				

def collectValues(data):
	if 'conf' in data:
		global fieldHeight
		fieldHeight=data["conf"]["maxHeight"]
		global fieldWidth
		fieldWidth=data["conf"]["maxWidth"]
		global paddleHeight
		paddleHeight = data["conf"]["paddleHeight"]
		global paddleWidth
		paddleWidth=data["conf"]["paddleWidth"]
		global ballRadius
		ballRadius=data["conf"]["ballRadius"]
		global tickInterval
		tickInterval=data["conf"]["tickInterval"]
	if 'left' in data:
		global ourside
		if data["left"]["playerName"] == name:	
			ourside=True
		else:
			ourside=False

def projectedTarget(data):	
	direction(data["ball"]["pos"]["x"],data["ball"]["pos"]["y"])	
	calcX=currX
	calcY=currY
	yFlip=1
	xFlip=1
	xFlippedFlag = False
	while (calcX > paddleWidth and ourside) or ( calcX < fieldWidth - paddleWidth and not ourside):
		calcX+=dirX*xFlip		
		calcY+=dirY*yFlip
		
		if (calcY<=ballRadius or calcY>=fieldHeight-ballRadius):
			yFlip=-yFlip
		if ((calcX < 0 and not ourside) or ( calcX > fieldWidth  and ourside)) and not xFlippedFlag:
			xFlip=-xFlip
			xFlippedFlag = True
	if xFlippedFlag:#improving future projection.
		if calcY<(fieldHeight/2):#top part
			calcY=(fieldHeight/2)-(((fieldHeight/2)-calcY)/3*2)
		else:#bottom part
			calcY=(fieldHeight/2)+((calcY-(fieldHeight/2))/3*2)
	else:
		global arrivalVector;
		arrivalVector = Vector(dirX*xFlip, dirY*yFlip)

	return calcY

def movePaddle(data, projectedY):
	global paddleHeight;
	
	ownPaddleY = 0
	enemyPaddleY = 0
	towardsCenter = Vector(0,0)
	if ourside:
		if 'left' in data:
			ownPaddleY = data["left"]["y"]
			enemyPaddleY = data["right"]["y"]
			towardsCenter.x = -1
	else:
		if 'right' in data:
			ownPaddleY = data["right"]["y"]
			enemyPaddleY = data["left"]["y"]
			towardsCenter.x = 1

	ownLocation = math.floor((ownPaddleY / fieldHeight) * 3) #0 = top, 1 = mid, 2 = bottom
	enemyLocation = math.floor((enemyPaddleY / fieldHeight) * 2) #0 = top, 1 = bottom

	ballAngle = arrivalVector.angleDeg(towardsCenter)

	offset = 0

	#MAGIC NUMBERS

	m1 = 2.4 #2.7
	m2 = 2.7 #3.2

	log = logging.getLogger(__name__)
	#POSITIIVINEN AMPUU ALASPAIN
	#TOP
	if ownLocation == 0:
		if(ballAngle > 25):
			offset = paddleHeight / m1
		elif(ballAngle < -25):
			offset = -paddleHeight / m1
		elif(ballAngle < 0 and enemyLocation == 0):
			offset = paddleHeight / m1
		else:
			offset = 0

	#MIDDLE
	elif ownLocation == 1:
		if(ballAngle > 25):
			offset = -paddleHeight / m2
		elif(ballAngle < -25):
			offset = paddleHeight / m2
		elif(enemyLocation == 0):
			offset = paddleHeight / m1
		else:
			offset = -paddleHeight / m1

	#BOTTOM
	elif ownLocation == 2:
		if(ballAngle > 25):
			offset = -paddleHeight / m1
		elif(ballAngle < -25):
			offset = paddleHeight / m1
		elif(ballAngle > 0 and enemyLocation == 2):
			offset = -paddleHeight / m1
		else:
			offset = 0

	projectedY -= paddleHeight / 2 + offset

	#clamp projectedY
	projectedY = max(min(projectedY, fieldHeight - paddleHeight), 0)
	if projectedY<25:
		projectedY+=20
	elif projectedY>(fieldWidth-25):
		projectedY-=20

	if(ownPaddleY - projectedY > 7):
		data = -1.0
	elif(projectedY - ownPaddleY > 7):
		data = 1.0
	elif(ownPaddleY - projectedY > 4):
		data = -0.5
	elif(projectedY - ownPaddleY > 4):
		data = 0.5
	elif(ownPaddleY - projectedY > 2):
		data = -0.1
	elif(projectedY - ownPaddleY > 2):
		data = 0.1
	else:
		data = 0
	return data

def open_url(msg_type, data):
	if msg_type == "joined":
		webbrowser.open_new(data)
