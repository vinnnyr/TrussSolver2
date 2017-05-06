import pygame
import math
import os
from pygame.locals import *

nodeImg = pygame.image.load('node.png')  # 42px by 42px sprite of a node


class Node:
    def __init__(self, (_x, _y), _id):
        self.x = _x
        self.y = _y
        self.id = _id
        self.moving = False
        # self.colour = (0, 0, 255)
        # self.thickness = 10

    def genLabel(self):
        self.labelX = myFont.render("X: " + str(self.x), 2, (0, 0, 0))
        self.labelY = myFont.render("Y: " + str(self.y), 2, (0, 0, 0))
        self.labelId = myFont.render("ID: " + str(self.id), 2, (0, 0, 0))

    def display(self):
        # pygame.draw.circle(screen, self.colour, (self.x, self.y), self.size, self.thickness)
        if self.moving:
            self.moveMode()
        self.genLabel()
        screen.blit(nodeImg, (self.x, self.y))
        screen.blit(self.labelX, (self.x - 21, self.y - 30))
        screen.blit(self.labelY, (self.x - 21, self.y - 10))
        screen.blit(self.labelId, (self.x - 21, self.y - 50))

    def moveMode(self):
        # print("Move Mode")
        self.x = mouseX - 21
        self.y = mouseY - 21


class Member:
    def __init__(self, startTup, _id):
        self.startTup = startTup
        self.id = _id
        (self.x, self.y) = self.startTup
        self.moving = True
        # print("Member Created")

    def display(self):
        if self.moving:
            self.moveMode()
            self.color = (110, 110, 110)
        else:
            self.color = (100, 100, 100)
        pygame.draw.line(screen, self.color, self.startTup, self.endTup, 21)
        # print("Member Drawn")

    def moveMode(self):
        # print("Move Mode")
        (self.x1, self.y1) = self.startTup
        self.endTup = (mouseX, mouseY)
        (self.x, self.y) = self.endTup


def checkCollide(classList, x, y):
    var = classList.__class__.__name__
    if (var != "list"):
        classList = [classList]
    list = []
    for p in classList:
        if abs(math.hypot(p.x - x, p.y - y)) <= 42:
            list = list + [p]
    if len(list) == 0:
        return None
    elif (len(list) == 1):
        var = list[0]
        return var
    else:
        return list


def worldLabelDisplay():
    nodeLengthLabel = myFont.render("Number of Nodes: " + str(len(nodeList)), 2, (0, 0, 0))
    memberLengthLabel = myFont.render("Number of Members: " + str(len(memberList)), 2, (0, 0, 0))
    gameModeLabel = myFont.render("Game Mode: " + str(programMode), 2, (0, 0, 0))
    mouseLabelX=myFont.render("mouseX :" + str(mouseX), 2, (0, 0, 0))
    mouseLabelY=myFont.render("mouseY :" + str(mouseY), 2, (0, 0, 0))

    screen.blit(gameModeLabel, (10, 10))
    screen.blit(nodeLengthLabel, (10, 30))
    screen.blit(memberLengthLabel, (10, 50))
    screen.blit(mouseLabelX, (mouseX,mouseY+10))
    screen.blit(mouseLabelY, (mouseX, mouseY + 30))


def nodeBuilder():
    collidedNode = checkCollide(nodeList, mouseX, mouseY)  # checks to see mouse pos in relation to a node
    # print("Mouse Pressed")
    if not collidedNode:  # if the variable DOES NOT exist then add a new Node
        nodeListLength = len(nodeList)
        nodeList.append(Node((mouseX - 21, mouseY - 21), nodeListLength))
        # print("New node added")
    else:
        if not checkCollide(memberList, mouseX, mouseY):
            collidedNode.moving = not collidedNode.moving
            indexToDel = nodeList.index(collidedNode)
        if collidedNode.moving:
            return indexToDel
        return None


def memberBuilder():
    def snapNode():
        nodeInInterest = memberSnapToNode(Member((mouseX-21, mouseY-21), len(memberList)))
        if nodeInInterest:
            print("Collided with: " + nodeInInterest.__class__.__name__ + " " + str(nodeInInterest.id))
            return nodeInInterest
        return False

    collidedMember = checkCollide(memberList, mouseX, mouseY)
    if not collidedMember:
        nodeInInterest = snapNode()
        if nodeInInterest:
            print("start^")
            memberList.append(Member((nodeInInterest.x + 21, nodeInInterest.y + 21), len(memberList)))
    else:
        if collidedMember.__class__.__name__ == "list":
            if (len(collidedMember) > 1):
                collidedMember = collidedMember[0]
        memb = checkCollide(memberList, mouseX, mouseY)
        if memb:
            if collidedMember.moving:
                nodeInInterest = snapNode()
                if nodeInInterest:
                    print"end^"
                    collidedMember.moving = not collidedMember.moving
                    # memToDel = memberList.index(collidedMember)
                    # return memToDel
                    # return None


def memberSnapToNode(memberToCheck):
    for p in nodeList:
        nodeInInterest = checkCollide(memberToCheck, p.x, p.y)
        if nodeInInterest:
            return p
    return None


# Pygame Stuff
pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Vinny's Truss Solver")
clock = pygame.time.Clock()

# Font Stuff
defaultFont = pygame.font.get_default_font()
myFont = pygame.font.SysFont(defaultFont, 22)

# Main Global Variables
nodeList = []
memberList = []
nodeDict = {}
programMode = 1  # mode 0:Node Building
# mode 1: Member Connecting

done = False
checkForDelete = False

nodeList.append(Node((500, 100), 0))
nodeList.append(Node((500, 300), 1))
nodeList.append(Node((300, 200), 2))

while not done:
    (mouseX, mouseY) = pygame.mouse.get_pos()  # Global Variables mouseX and mouseY
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if programMode == 0:
                indexToDel = nodeBuilder()  # This function builds nodes, returns the moving node as indexToDel
                if not indexToDel:
                    checkForDelete = False
                else:
                    checkForDelete = True
            elif programMode == 1:
                memberBuilder()
        if event.type == pygame.KEYDOWN:
            if programMode == 0 and event.key == pygame.K_d and checkForDelete:  # Known Bug: Can't delete the first node
                # print("Deleting Index" + str(indexToDel))
                nodeList.pop(indexToDel)
                checkForDelete = False
            elif event.key == pygame.K_1:
                programMode = 1  # program mode 1: Truss Building
            elif event.key == pygame.K_2:
                programMode = 0

    if programMode == 0:
        color = (125, 125, 120)
    else:
        color = (200, 200, 225)
    screen.fill(color)
    for m in memberList:
        m.display()
    for p in nodeList:
        p.display()
    worldLabelDisplay()
    pygame.display.flip()
    clock.tick(60)
