import math
import numpy as np
import pygame

white = (255, 255, 255)
grey = (96, 125, 139)
red = (244, 67, 54)
green = (10, 151, 41)
black = (0, 0, 0)


# Class Definitions 7/1/17
# Each Node has coordinates and ID
# Member has ID, toNode (endNode) and fromNode (startNode) and then dx,dy, and length,
# Reactions have id,node,and direction
# External forces have force mag, direction, and node

# A Structure has a list of Members, and a member has a list of nodes
class Structure:
    def __init__(self):
        self.membList = []
        self.array = np.array([])
        self.structNodes = []  # running list of all the nodes of the struct
        self.forceList= []
        self.memberAdded = False
        self.display()
        # self.testingScenario()

    def createMemb(self, pos):  # will be called when mouse is clicked
        if len(self.membList) > 0:  # If membList is populated
            lastMemb = self.membList[len(self.membList) - 1]  # get the last member
            if lastMemb.moving:
                self.startPosList = self.getStartPos()
                var = checkCollide(self.startPosList, pos, 15)
                lastMemb.moving = False  # If this was entered, the member is now "complete"
                lastMemb.startNode
                if var:
                    if var.__class__.__name__ == 'list':
                        var = var[0]  # this condition happens when you trace over members
                    lastMemb.endPos = var
            else:  # Check collide with end of other memb (to connect) and then add new Memb
                # var = checkCollide(lastMemb, (mouseX, mouseY), 15)
                var = checkCollide(self.membList, pos, 15)
                if var:
                    if var.__class__.__name__ == 'list':
                        var = var[0]  # this condition happens when you trace over members
                    # self.addMemb(lastMemb.endPos)  # start new memb
                    self.addMemb(var.endPos)
        else:  # No membList population, start one.
            self.addMemb((mouseX, mouseY))

    def createForce(self, pos, type):  # This is where Force IDs are created
        global forceCount
        var = checkCollide(self.structNodes, pos, 50)
        if var:
            if var.__class__.__name__ == 'list':
                var = var[0]  # this condition happens when you trace over members
            nodeInInterest = var
            forceCount = forceCount + 1
            id = forceCount
            nodeInInterest.addForce((nodeInInterest.x, nodeInInterest.y), type, id)
        else:
            print('something weird happened')  # This is where a force is not attached to a node

    def addMemb(self, pos):
        self.membList.append(Member(pos, self))
        self.memberAdded = True

    def forceMembPos(self, pos1, pos2):
        self.addMemb(pos1)
        membInFocus = self.membList[len(self.membList) - 1]
        membInFocus.moving = False
        membInFocus.endPos = pos2
        membInFocus.endMember(pos2)
        self.memberAdded = True

    def testingScenario(self):  # This function generates a known truss
        a = 300
        b = 150
        self.forceMembPos((a, a), (a, a + b))
        self.printMembInfo()
        self.forceMembPos((a, a + b), (a + b, a))
        self.printMembInfo()
        self.forceMembPos((a, a + b), (a + b, a + b))
        self.printMembInfo()
        self.forceMembPos((a, a), (a + b, a))
        self.printMembInfo()
        self.forceMembPos((a + b, a), (a + b, a + b))
        self.printMembInfo()
        self.createForce((a, a + b), 'roller')
        self.printMembInfo()
        self.createForce((a + b, a + b), 'pin')
        self.printMembInfo()
        self.createForce((a + b, a), 'vec')
        self.printMembInfo()

    def getStartPos(self):
        list = []
        for m in self.membList:
            list.append(m.startPos)
        return list

    def printMembInfo(self):
        self.display()
        self.membInInterest = self.membList[len(self.membList) - 1]
        self.tempNodeList = self.membInInterest.nodeList

    def printInfo(self):
        print("Number of Nodes: " + str(len(self.structNodes)))
        for n in self.structNodes:
            print(n.id)
        print("Number of Members: " + str(len(self.membList)))

        print("")

    def display(self):
        # self.structNodes = []  # running list of all the nodes of the struct
        i = 0  # assigning Node IDS
        for n in self.structNodes:
            i = i + 1
            n.id = i
        i = 0  # assigning Node IDS
        for m in self.membList:
            i = i + 1
            m.id = i
        if self.memberAdded:
            self.structNodes = self.structNodes + self.membList[len(self.membList) - 1].nodeList
            self.memberAdded = False
            self.structNodes = list(set(self.structNodes))  # This is a a trick to remove duplicates
        for m in self.membList:
            m.display()
            # self.structNodes = self.structNodes + m.nodeList  # This is inefiicient, creatign a whole new list everytime

    def get(self):
        self.printInfo()
        global forceCount
        for m in self.membList:
            node1 = m.nodeList[0]  # getting the two nodes of each member
            node2 = m.nodeList[1]
            unit1 = getUnit(node1.pos, node2.pos)
            (self.temp1, self.temp2) = unit1
            unit2 = (-self.temp1, -self.temp2)
            node1.forceList.append(memberForce(node1.pos, unit1, True, forceCount + 1))
            node2.forceList.append(memberForce(node2.pos, unit2, False, forceCount + 1))
            forceCount += 1
            # for n in m.nodeList:
            #     #print("Number of Forces: " + str(len(n.forceList)))
            #     #     for f in n.forceList:
            #     #         if f.__class__.__name__ == 'Pin':
            #     #             print("Pin support in this node")
            #     #         elif f.__class__.__name__ == 'Roller':
            #     #             print("Rolelr support in this node")
            #     #         else:
            #     #             print("No Pin or Roller")
            #     # print('Unit 1:' + str(unit1))
            #     # print('Unit 2:' + str(unit2))
            for n in self.structNodes:
                for f in n.forceList:
                    self.forceList.append(f)
                    if f.__class__.__name__ == 'Pin':
                        # print("Pin support in this node")
                        f.resolve()
                    elif f.__class__.__name__ == 'Roller':
                        f.resolve()
                        # print("Rolelr support in this node")
                        # else:
                        # print("No Pin or Roller")\
            self.forceList = list(set(self.forceList)) # Removes duplicates


class Member:
    def __init__(self, startPos, struct):
        self.startPos = startPos
        self.myStruct = struct
        # self.endPos = (mouseX, mouseY)
        self.nodeList = []
        # self.nodeList.append(Node(self.startPos, True))
        self.addNode(startPos, True)
        self.color = white  # white
        self.moving = True

    def addNode(self, pos, isStartNode):  # Create new node if there isn't one in the pos in question
        self.var = checkCollide(self.myStruct.structNodes, pos, 2)
        if self.var:
            if self.var.__class__.__name__ == 'list':
                self.var = self.var[0]  # To take care of duplicaes
            self.nodeList.append(self.var)
            if isStartNode:
                self.startNode = self.var
            else:
                self.endNode = self.var
        else:
            self.nodeList.append(Node(pos, isStartNode))  # Create new Node
            if isStartNode:
                self.startNode = self.nodeList[len(self.nodeList) - 1]
            else:
                self.endNode = self.nodeList[len(self.nodeList) - 1]

    def endMember(self, pos):
        if len(self.nodeList) < 2:  # Each member only has two nodes
            # print(len(self.nodeList))
            self.addNode(self.endPos, False)
        (self.x, self.y) = self.endPos
        self.calc()

    def calc(self):
        (x1, y1) = self.startNode.pos
        (x2, y2) = self.endNode.pos
        self.dx = x2 - x1
        self.dy = y2 - y1
        self.length = math.sqrt(self.dx ** 2 + self.dy ** 2)

    def display(self):
        if self.moving:
            self.endPos = (mouseX, mouseY)
            (self.x, self.y) = self.endPos
        pygame.draw.line(screen, self.color, self.startPos, self.endPos, 5)
        if self.moving == False:
            self.endMember(self.endPos)
        if len(self.nodeList) == 2:
            self.startNode = self.nodeList[0]
            self.endNode = self.nodeList[1]

        for n in self.nodeList:
            n.display()


class Node:
    def __init__(self, pos, isStart):
        self.isStart = isStart
        self.pos = pos
        self.r = 15
        (self.x, self.y) = pos
        self.color = grey
        self.forceList = []

        # These two lists will eventually become the rows in the systyem matrix
        self.xList = []
        self.yList = []
        # Arrays
        self.array = np.array([])
        # self.label=myFont.render(str(self.pos),1, red)

    def addForce(self, pos, type, id):
        # print(type)
        if type == 'pin':
            self.forceList.append(Pin(pos,self))
        elif type == 'roller':
            self.forceList.append(Roller(pos,self))
        elif type == 'vec':
            self.forceList.append(VectorForce(pos, 50, 0, True,self))
        obj = self.forceList[(len(self.forceList) - 1)]
        obj.id = id

    def display(self):
        pygame.draw.circle(screen, self.color, self.pos, self.r)
        # screen.blit(self.label,self.pos)
        for f in self.forceList:
            f.display()
            # print(f.__class__.__name__)
            # print(f.id)


# The following 3 classes are types of Forces

# Can support x and y forces
class Pin:
    def __init__(self, pos,node):
        self.node=node
        self.pos = pos
        (self.x, self.y) = self.pos
        self.color = red
        self.id = 0

        # Dispaly Constants
        self.p1 = self.pos
        self.p2 = (self.x - 37, self.y + 50)
        self.p3 = (self.x + 37, self.y + 50)

        self.resolved = False
        self.value = "?"

    def resolve(self):
        self.theta = list([90, 180])
        self.myVec1 = VectorForce(self.pos, 50, self.theta[0], False, "null") #y
        self.myVec1.myArrow.color = green
        self.myVec1.value = '?'

        self.myVec2 = VectorForce(self.pos, 50, self.theta[1], False, "null") #x
        self.myVec2.myArrow.color = green
        self.myVec2.value = '?'

        self.resolved = True

    def display(self):
        if not self.resolved:
            pygame.draw.polygon(screen, self.color, (self.p1, self.p2, self.p3), 0)
        else:
            self.myVec1.display()
            self.myVec2.display()


# Can only support one force in a certain direction (typically straight up)
class Roller:
    def __init__(self, pos,node):
        self.node = node
        self.pos = pos
        (self.x, self.y) = self.pos
        self.color = red
        self.id = 0
        self.value = "?"
        # Display Cosntants
        self.p1 = self.pos
        self.p2 = (self.x - 37, self.y + 35)
        self.p3 = (self.x + 37, self.y + 35)
        self.p4 = (self.x + 22, self.y + 40)
        self.p5 = (self.x - 22, self.y + 40)

        self.resolved = False
        self.theta = 90

    def resolve(self):
        self.myVec = VectorForce(self.pos, 50, self.theta, False, "null")#y
        self.myVec.myArrow.color = green
        self.myVec.value = '?'
        self.resolved = True

    def display(self):
        if not self.resolved:
            pygame.draw.polygon(screen, self.color, (self.p1, self.p2, self.p3), 0)
            pygame.draw.circle(screen, self.color, self.p4, 10, 0)
            pygame.draw.circle(screen, self.color, self.p5, 10, 0)
        else:
            self.myVec.display()


# A vector force defined by value and angle from horz X axis
class VectorForce:
    def __init__(self, pos, value, angle, label,node):
        self.node = node
        self.pos = pos
        self.value = value
        self.theta = -math.radians(angle)
        self.color = red
        (self.x, self.y) = self.pos
        self.x2 = self.x + (self.value * math.cos(self.theta))
        self.y2 = self.y + (self.value * math.sin(self.theta))
        self.myArrow = Arrow(self.color, self.value, self.theta, self.pos, (self.x2, self.y2))
        self.displayLabel = label
        self.id = 0

    def display(self):
        self.myArrow.display()
        if self.displayLabel:
            self.fLabel = myFont.render("Force Value: " + str(self.value), 2, red)
            screen.blit(self.fLabel, (self.x2 + 21, self.y2))


class memberForce:
    def __init__(self, pos, unit, flip, id):
        (self.u1, self.u2) = unit
        self.pos = pos
        self.type = 'member'
        if self.u1 == 0:
            if self.u2 > 0:
                self.theta = 90
            else:
                self.theta = 270
        else:
            self.theta = math.degrees(-math.atan(self.u2 / self.u1))
            if flip:
                self.theta = self.theta - 180
            else:
                self.theta = self.theta
        self.id = id
        self.myVec = VectorForce(pos, 50, self.theta, False, "null")
        self.myVec.myArrow.color = green
        self.value = '?'
        self.myVec.value = self.value

    def display(self):
        self.myVec.display()


# Arrow used for VectorForce
class Arrow:
    def __init__(self, color, val, theta, (x1, y1), (x2, y2)):
        self.color = color
        self.theta = theta
        self.value = val
        (self.x1, self.y1) = (x1, y1)
        (self.x2, self.y2) = (x2, y2)
        self.x3 = self.x2 + (.15 * self.value * math.sin(-self.theta)) - 2 * math.cos(self.theta)
        self.y3 = self.y2 + (.15 * self.value * math.cos(-self.theta)) - 2 * math.sin(self.theta)
        self.x4 = self.x2 - (.15 * self.value * math.sin(-self.theta)) - 2 * math.cos(self.theta)
        self.y4 = self.y2 - (.15 * self.value * math.cos(-self.theta)) - 2 * math.sin(self.theta)
        self.x5 = self.x2 + (.15 * self.value * math.cos(self.theta))
        self.y5 = self.y2 + (.15 * self.value * math.sin(self.theta))

    def display(self):
        pygame.draw.line(screen, self.color, (self.x1, self.y1), (self.x2, self.y2), 10)
        pygame.draw.polygon(screen, self.color, ((self.x3, self.y3),
                                                 (self.x4, self.y4), (self.x5, self.y5)), 0)


def checkCollide(classList, pos, r):
    var = classList.__class__.__name__
    (x, y) = pos
    if (var != "list"):  # if single var is to be checked, make it into a list
        classList = [classList]
    list = []
    for p in classList:
        className = p.__class__.__name__
        # print(className)
        if className == 'tuple':  # if classList is a list of tups, unpack the tup
            (a, b) = p
            if abs(math.hypot(a - x, b - y)) <= r:
                list = list + [p]
        else:  # otherwise cehck against the x and y pos
            if abs(math.hypot(p.x - x, p.y - y)) <= r:
                list = list + [p]
    if len(list) == 0:
        return None
    elif (len(list) == 1):
        var = list[0]
        return var
    else:
        return list


def getUnit(pos1, pos2):
    (x1, y1) = pos1
    (x2, y2) = pos2
    (dx, dy) = (x2 - x1, y2 - y1)
    mag = math.sqrt(dx ** 2 + dy ** 2)
    unit = (dx / mag, dy / mag)
    return unit  # unit is a tuple, unit vec


def solveSys(struct):
    ## Populate Element Data
    numberOfNodes=len(mainStruct.structNodes)
    M=np.zeros((2*numberOfNodes,2*numberOfNodes))
    external = np.zeros((2 * numberOfNodes, 1))
    # Matlab:
    # M(2*nodeFrom-1,element)= dx/length;
    # M(2*nodeTo-1,element)= -dx/length;
    # M(2*nodeFrom,element)= dy/length;
    # M(2*nodeTo,element)= -dy/length;
    for m in mainStruct.membList:
        nodeFrom=m.startNode.id
        nodeTo=m.endNode.id
        print("node from" + str(nodeFrom))
        print("node to" + str(nodeTo))
        print("memb id" + str(m.id))
        M[(2*nodeFrom-2),(m.id-1)]=m.dx/m.length
        M[(2 * nodeTo - 2),(m.id - 1)]=-m.dx/m.length
        M[(2 * nodeFrom - 1), (m.id - 1)] = m.dy / m.length
        M[(2 * nodeTo - 1), (m.id - 1)] = -m.dy / m.length
        #print(M)
    print(M)
    print(len(mainStruct.forceList))
    fID=0
    for f in mainStruct.forceList:
        #Note... Roller and Pin IDS may not always be in the first 3... possible mode of failure
        # if ((direction == 'y') | (direction == 'Y'))
        #     M(2 * node, numberElements + reaction) = M(2 * node, numberElements + reaction) + 1;
        # elseif((direction == 'X') | (direction == 'x'))
        # M(2 * node - 1, numberElements + reaction) = M(2 * node - 1, numberElements + reaction) + 1;
        if f.__class__.__name__=='Roller': #Y
            #print(f.node)
            fID=fID+1
            #np.put(M, ((2 * nodeFrom - 1) * (len(mainStruct.membList))+f.id-1), 1) #Possible mode of failure...1
            print(len(mainStruct.membList) + f.id - 1)
            M[2*f.node.id-1,len(mainStruct.membList)+f.id-1]=1 #Y
            #f.id=fID
            #print("Roller ID:" + str(f.id))
        elif f.__class__.__name__=='Pin': # X and Y
            fID=fID+1
            print(len(mainStruct.membList) + f.id -1)
            M[2 * f.node.id - 2, len(mainStruct.membList) + f.id -1 ] = 1 #X #Possible mode of failure...1
            M[2 * f.node.id - 1, len(mainStruct.membList) + f.id ] = 1#Y
            #f.id=fID+1
            #print("Pin Id:" + str(f.id))
        elif f.__class__.__name__=='VectorForce':
            # print(f.id)
            # print(f.node)
            # print(f.theta)
            external[2*f.node.id-2]=-f.value*math.cos(f.theta) #x
            external[2 * f.node.id - 1] = -f.value * math.sin(f.theta) #y
        else:
            pass
    np.savetxt('npLog.csv',M,delimiter=",")
    #np.savetxt('npLog2.csv', external, delimiter=",")
    A= np.linalg.solve(M,external)
    print(A)



# Pygame Stuff
pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Vinny's Truss Solver")
clock = pygame.time.Clock()
# defaultFont = pygame.font.get_default_font()
myFont = pygame.font.SysFont('Futura',
                             18)  # IF this doesnt work, replace the string 'Futura' with the variable defaultFont
mainStruct = Structure()  # init structure
count = 0
done = False
mode = 0

forceList = []
forceDict = {}
forceCount = 0

while not done:
    # Main Program:
    (mouseX, mouseY) = pygame.mouse.get_pos()  # Global Variables mouseX and mouseY
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if mode == 0:
                mainStruct.createMemb((mouseX, mouseY))
            else:
                if mode == 1:
                    fType = 'pin'
                elif mode == 2:
                    fType = 'roller'
                elif mode == 3:
                    fType = 'vec'

                mainStruct.createForce((mouseX, mouseY), fType)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0:
                mode = 0
                mainStruct.printInfo()
            elif event.key == pygame.K_1:
                mode = 1  # pin
            elif event.key == pygame.K_2:
                mode = 2  # roller
            elif event.key == pygame.K_3:
                mode = 3  # ved
            elif event.key == pygame.K_a:
                mainStruct.testingScenario()
            elif event.key == pygame.K_s:
                mainStruct.get()
                solveSys(mainStruct)
                # elif event.key== pygame.K_d:
                #     populateForceDict()
                # print("Game Mode:" + str(mode))

    # Display, Flip, Tick
    screen.fill((0, 0, 0))  # black
    mainStruct.display()
    pygame.display.flip()
    clock.tick(60)
