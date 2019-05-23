'''
Class: CPSC 427 
Team Member 1: Andrew Abbott
Team Member 2: None
Submitted By Andrew Abbott
GU Username: aabbott
File Name: othello.py
An implemntation of the game othello with a a-b prune and huristic AI. The AI will play as the balck player,
if player chosen is 'b' then the AI will make the first move, if the player 'w' is chosen then the AI will go second.
Usage: python othello.py boardConfiguration
	board configuration can be either left blank where the board
	will be created in standart form
		wb
		bw
	or the board configureation can be changed to the alternate form 
	by entering a '1' as the boardConfiguration where it will result
	in the starting board of 
		bw
		wb
Huristic: My hurisitic was roughly based on the sudo code that can be found here http://www.cs.cornell.edu/~yuli/othello/othello.html
	It uses general chip count to evaluate the associated number with the huristic. Normal moves receive a score of +1 
	where as the edges are weighted more heavily of 5. Also weighted the corners moves as very positive considering they cannot be taken. 
	Lastly offed a very poor score to chips that would place the AI next to a corner, seeing as though they then would lose the untakable space. 
'''

from math import *
from time import *
from random import *
from copy import deepcopy
import sys
import threading

#init some global varibale 
nodes = 0
moves = 0
#4 becuaes 4 peices on the board
depth = 4


class Board:
	def __init__(self,boardConfig):
		#White goes first (0 is white and player,1 is black and computer)
		self.player = 'w'
		self.passed = False
		self.won = False
		#Initializing an empty board
		self.array = []
		for x in range(8):
			self.array.append([])
			for y in range(8):
				self.array[x].append('/')

		#Initializing center values
		if boardConfig == 1:
			self.array[3][3]="b"
			self.array[3][4]="w"
			self.array[4][3]="w"
			self.array[4][4]="b"
		else: 
			self.array[3][3]="w"
			self.array[3][4]="b"
			self.array[4][3]="b"
			self.array[4][4]="w"

		#Initializing old values
		self.oldarray = self.array


	#prints the current boardstate array and the current score of the game
	def printBoard(self):
		i = 1
		headerLst = ["A","B","C","D","E","F","G","H"]
		print(' '),
		for letter in headerLst:
			print letter,
		print

		for x in range(8):
			print (i),
		        i+=1
			for y in range(8):
				print (self.array[y][x]),
			print
		wScore, bScore = self.createScore()
		print('SCORE: W = ' + str(wScore) + '\t B = '+ str(bScore)) 
		print 

	def makeAIMove(self):
		if not self.won:
			self.oldarray = self.array
			#THIS IS WHERE AB PRUNE IS CALLED
			alphaBetaResults = self.alphaBeta(self.array,depth,-float('inf'),float('inf'),1)
			#returns the list of the best board to make the move 
			return alphaBetaResults[2]
		self.passTest()
		
					
	#Moves to position
	def boardMove(self,x,y):
		#global nodes
		#Move and update screen
		self.oldarray = self.array
		self.oldarray[x][y]="w"
		new, old = move(self.array,x,y,self.player)	

		#Switch Player
		if self.player =='w':
				self.player = 'b'
		else:
			self.player = 'w'
		self.array = new
		self.printBoard()

		#see if user wants to revert to old state
		choice = raw_input('Do we want to revert? (y or n)> ')
		print
		if choice == 'y':
			self.array = old
			self.array[x][y]="/"
			self.printBoard()
			if self.player =='w':
				self.player = 'b'
			else:
				self.player = 'w'

	
		#Check if the player must pass on their turn
		self.passTest()

	#calcualtes the score of the game
	def createScore(self):
		wScore = 0
		bScore = 0
		for x in range(8):
			for y in range(8):
				if self.array[x][y]=="w":
					wScore+=1
				elif self.array[x][y]=="b":
					bScore+=1
		return wScore, bScore
		
	#checks to see if the next player has a possible move, if they dont then
	#they must pass on their turn. 
	def passTest(self):
		mustPass = True
		#checks the game boar, if there is a valid move to be made
		#then the player doesn't have to pass
		for x in range(8):
			for y in range(8):
				if valid(self.array,self.player,x,y):
					mustPass=False
		#if the player does have to pass then we need to switch the player
		if mustPass:
			if self.player =='w':
				self.player = 'b'
			else:
				self.player = 'w'
			#if it isnt the first time the player has had to pass, the gmae is over
			if self.passed==True:
				self.won = True
			else:
				self.passed = True
		#if a good move was found, then the game is not over adn the pass is
		#removed from the player
		else:
			self.passed = False

	#alphaBeta pruning
	def alphaBeta(self,node,depth,alpha,beta,maximizing):
		global nodes 
		nodes += 1
		boards = []
		choices = []

		#cycles though all of the choices on the board given a certain board
		#if is a valid move, appends the the new board state to the text list 
		#as well as the move that got the board to that position
		for x in range(8):
			for y in range(8):
				if valid(self.array,self.player,x,y):
					test, oldBoard = move(node,x,y,self.player)
					boards.append(test)
					choices.append([x,y])
		
		#once we run out of boards to test, then we exit recursion with our hurristic
		if depth==0 or len(choices)==0:
			return ([heuristic(node,maximizing),node])
		
		#the maximizing portion of ab prune
		if maximizing:
			v = -float("inf")
			bestBoard = []
			bestChoice = []
			for board in boards:
				#recursivly call alpha beta on min
				boardValue = self.alphaBeta(board,depth-1,alpha,beta,0)[0]
				if boardValue>v:
					v = boardValue
					bestBoard = board
					bestChoice = choices[boards.index(board)]
				alpha = max(alpha,v)
				if beta <= alpha:
					break
			#return our best option
			return([v,bestBoard,bestChoice])
		else:
			v = float("inf")
			bestBoard = []
			bestChoice = []
			for board in boards:
				#recursivly call alpha beta on max
				boardValue = self.alphaBeta(board,depth-1,alpha,beta,1)[0]
				if boardValue<v:
					v = boardValue
					bestBoard = board
					bestChoice = choices[boards.index(board)]
				beta = min(beta,v)
				if beta<=alpha:
					break
			#return our best option
			return([v,bestBoard,bestChoice])


#prints the ai's desired move
def printAiMoves(passedArray,player,chipsToChange,orgx,orgy):
	passedArray[orgx][orgy]= '~'
	for node in chipsToChange:
		passedArray[node[0]][node[1]]='~'
	
	i = 1
	headerLst = ["A","B","C","D","E","F","G","H"]
	print(' '),
	for letter in headerLst:
		print letter,
	print

	for x in range(8):
		print (i),
	        i+=1
		for y in range(8):
			if passedArray[y][x] == '~':
				print('\x1b[6;30;42m'+ player + '\x1b[0m'),
			else:
				print(passedArray[y][x]),
		print
	
	print("AI's desired move: (" + headerLst[orgx] + ',' + str(orgy + 1) + ")")
	print
	raw_input("Press Enter to continue...")
	passedArray[orgx][orgy]= 'b'


#part of the print AI moves, coppied the move function for simplicity
def makeHighlightedAIMoves(passedArray,x,y,player):
	array = deepcopy(passedArray)
	
	playerColor = player
	#makes the initial move
	array[x][y]=playerColor
	
	#Defind our neighbors to our inital move
	neighbors = []
	for i in range(max(0,x-1),min(x+2,8)):
		for j in range(max(0,y-1),min(y+2,8)):
			if array[i][j]!='/':
				neighbors.append([i,j])
	
	#Which tiles to convert
	chipsToChange = []

	#now look for a make line in the neighbors to switch to our players color
	for neighbor in neighbors:
		nX = neighbor[0]
		nY = neighbor[1]
		
		if array[nX][nY]!=playerColor:
			 #route is the way we need to go to get to our other chip
			route = []
			
			#where to go
			changeX = nX-x
			changeY = nY-y
			tempX = nX
			tempY = nY

			#While still on the board
			while 0<=tempX<=7 and 0<=tempY<=7:
				route.append([tempX,tempY])
				value = array[tempX][tempY]
				#if spot is open, stop
				if value=='/':
					break
				#if we get our own color, we get a line
				if value==playerColor:
					for node in route:
						chipsToChange.append(node)
					break
				#move to current location
				tempX = tempX + changeX
				tempY = tempY + changeY

	printAiMoves(array,player,chipsToChange,x,y)			

#makes the move of the chips in the same mannor/method that we 
#validated the move
def move(passedArray,x,y,player):
	
	array = deepcopy(passedArray)
	
	playerColor = player
	#makes the initial move
	array[x][y]=playerColor
	
	#Defind our neighbors to our inital move
	neighbors = []
	for i in range(max(0,x-1),min(x+2,8)):
		for j in range(max(0,y-1),min(y+2,8)):
			if array[i][j]!='/':
				neighbors.append([i,j])
	
	#Which tiles to convert
	chipsToChange = []

	#now look for a make line in the neighbors to switch to our players color
	for neighbor in neighbors:
		nX = neighbor[0]
		nY = neighbor[1]
		
		if array[nX][nY]!=playerColor:
			 #route is the way we need to go to get to our other chip
			route = []
			
			#where to go
			changeX = nX-x
			changeY = nY-y
			tempX = nX
			tempY = nY

			#While still on the board
			while 0<=tempX<=7 and 0<=tempY<=7:
				route.append([tempX,tempY])
				value = array[tempX][tempY]
				#if spot is open, stop
				if value=='/':
					break
				#if we get our own color, we get a line
				if value==playerColor:
					for node in route:
						chipsToChange.append(node)
					break
				#move to current location
				tempX = tempX + changeX
				tempY = tempY + changeY
				
	for node in chipsToChange:
		array[node[0]][node[1]]=playerColor
	
	return array, passedArray


#validates a given move(returns true or false)
def valid(array,player,x,y):
	#Sets player playerColor
	playerColor = player
	#check to see if the current location is already occupied by a piece
	if array[x][y]!='/':
		return False
	#check to see if there are any peices nextdoor
	else:
		#if so, make a list of them
		neighbor = False
		neighbors = []
		#check around our current location
		for i in range(max(0,x-1),min(x+2,8)):
			for j in range(max(0,y-1),min(y+2,8)):
				if array[i][j]!='/':
					neighbor=True
					neighbors.append([i,j])
		#if there are no neighbors then you cant make the move there
		if not neighbor:
			return False
		else:
			
			valid = False
			for neighbor in neighbors:

				nX = neighbor[0]
				nY = neighbor[1]
				
				#if its your color its not going to change
				if array[nX][nY]==playerColor:
					continue
				else:
					#see which way the possible move line would be going 
					changeX = nX-x
					changeY = nY-y
					tempX = nX
					tempY = nY
					#while in the bounds of the board
					while 0<=tempX<=7 and 0<=tempY<=7:
						#if an empty spot is found, then its not a line
						if array[tempX][tempY]=='/':
							break
						#if we reach the same color then we would have found a line to flip
						#so valid move
						if array[tempX][tempY]==playerColor:
							valid=True
							break
						#then we keep going twards the current direction of the line
						tempX+=changeX
						tempY+=changeY
			return valid

def timerQuit():
	print('Move took to long, Game Over!')
	exit

def heuristic(array,player):
	#init all of the vairable and the weights of each of the moves
	score = 0
	cornerVal = 25
	adjacentVal = 5
	sideVal = 5
	#init the player and their opponenets colors for the given turn
	if player=='b':
		playerColor='b'
		opponent='w'
	else:
		playerColor = 'w'
		opponent = 'b'
	#look at all of the possible tiles	
	for x in range(8):
		for y in range(8):
			#if the tile is a good possible move than we add 1
			add = 1
			#tiles that are next to corners are worth -3 beucsae then we get trapped on the corner
			if (x==0 and y==1) or (x==1 and 0<=y<=1):
				if array[0][0]==playerColor:
					add = sideVal
				else:
					add = -adjacentVal
			elif (x==0 and y==6) or (x==1 and 6<=y<=7):
				if array[7][0]==playerColor:
					add = sideVal
				else:
					add = -adjacentVal
			elif (x==7 and y==1) or (x==6 and 0<=y<=1):
				if array[0][7]==playerColor:
					add = sideVal
				else:
					add = -adjacentVal
			elif (x==7 and y==6) or (x==6 and 6<=y<=7):
				if array[7][7]==playerColor:
					add = sideVal
				else:
					add = -adjacentVal
			#checks each of the edges, dis regarding the corners because
			#those are worth more than edges, if edge, add edge value
			elif (x==0 and 1<y<6) or (x==7 and 1<y<6) or (y==0 and 1<x<6) or (y==7 and 1<x<6):
				add=sideVal
			#Checks to see if it is a corner tile, if yes add corner value
			elif (x==0 and y==0) or (x==0 and y==7) or (x==7 and y==0) or (x==7 and y==7):
				add = cornerVal
			#Add or subtract the value of the tile corresponding to the playerColor
			if array[x][y]==playerColor:
				score+=add
			elif array[x][y]==opponent:
				score-=add
	#return the score of the given board	
	return score


def getNewMove(bs):
	if not bs.won:
	#if the current player is the player, Dow below
		if bs.player == 'w':
			#create lists of the possible inputs to iterate trough
			lowerCaseOptions = ['a','b','c','d','e','f','g','h']
			upperCaseOptions = ['A','B','C','D','E','F','G','H']

			#display current player
			print('Player ' + str(bs.player) + "'s move")
		
			#get the desired move from user
			xInput = raw_input("Enter your X cord (a-h)> ")
			#if quit
			if xInput == 'q':
				quit()

			isValidxInput = False
			for k in range(8):
				if xInput == lowerCaseOptions[k] or xInput == upperCaseOptions[k] or xInput == 'h' or xInput == 'H':
					isValidxInput = True
			
			if not isValidxInput:
				print('Invalid Input, please enter a new one')
				bs.printBoard()
				getNewMove(bs)
			yInput = int(input("Enter your Y cord (0-7)> "))

			#initiate x to an impossible vlaue 
			xCord = 10
			yCord = yInput - 1
			#find the number associated witht the letter entered
			for i in range(7):
				if (xInput == lowerCaseOptions[i] or xInput == upperCaseOptions[i]):
					xCord = i
					break
			if xInput == 'h' or xInput == 'H':
				xCord = 7
			
			#check validity of the entered values, if entered value was not good then
			#xCord will not change and user will be asked for a new value
			if xCord == 10: 
				print('Invalid X cord, please enter a new one')
				bs.printBoard()
				getNewMove(bs)
			if not (-1 <= yCord <= 7):
				print('Invalid Y cord, please enter a new one')
				bs.printBoard()
				getNewMove(bs)
			
			#check to see if the value entered by the user was a good/valid move
			#if not valid, make them enter new cordinates
			if(valid(bs.array,bs.player,xCord,yCord)):
				bs.boardMove(xCord,yCord)
			else: 
				print('You entered an invalid move, please enter new ones')
				bs.printBoard()
				getNewMove(bs)
		#else the move is the AI so call AI meithod
		else:
			timer = threading.Timer(10.0, timerQuit)
			#start the timer
			timer.start()
			#call for the AIs move to be made
			move = bs.makeAIMove()
			#if returns move in time, stop timer
			timer.cancel()
			#show the disired move
			makeHighlightedAIMoves(bs.array,move[0],move[1],'b')
			#make the AIs move
			bs.boardMove(move[0],move[1])
	else: 
		print('GAME OVER')
	

#gets the desired player color
def getPlayer(bs):
    chosenPlayer = raw_input('Would you like to be balck or white? b or w)> ')
    if chosenPlayer == 'b':
		bs.player = 'b' 
    else:
		bs.player = 'w'

def main():

	
	if len(sys.argv) > 1:
		boardConfig = int(sys.argv[1])
	else:
		boardConfig = 0

	board = Board(boardConfig)
	getPlayer(board)
	

	while(not board.won):
		
		board.printBoard()
		#board.printOptionalMoves()
		getNewMove(board)  

main()
