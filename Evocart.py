import math
import grpc
import random
import time
import minecraft_pb2_grpc
from minecraft_pb2 import *
from perlin_noise import PerlinNoise
from random import randrange

channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)

AxisTried = []
RailPlaced = []
BestPath = []
CurrentTryPath = []
alea = 0


class MyPoint:
    x = 0
    y = 0
    z = 0

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


def ActivateCommandBlock(px, py, pz):
    time.sleep(1)
    client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=px, y=py, z=pz), type=AIR, orientation=NORTH),
    ]))

    client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=px, y=py, z=pz), type=REDSTONE_BLOCK, orientation=NORTH),
    ]))
    time.sleep(1)
    client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=px, y=py, z=pz), type=AIR, orientation=NORTH),
    ]))


def PlaceRailAt(point):
    client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=point.x, y=point.y, z=point.z), type=RAIL,
              orientation=NORTH),
    ]))

#Decide direction to next rail
def TranslateToAxis(alea, NewPoint):
    # 0 North
    # 1 South
    # 2 East
    # 3 West

    # North/South
    if (alea < 2):
        # North
        if (alea < 1):
            if (NewPoint.z + 1 < 24):
                NewPoint.z += 1
        else:
            # South
            if (NewPoint.z - 1 > 0):
                NewPoint.z -= 1
        # East/West
    else:
        if (alea > 2):
            if (NewPoint.x + 1 < 24):
                NewPoint.x += 1
        else:
            if (NewPoint.x - 1 > 0):
                NewPoint.x -= 1
    return NewPoint

#Create the Path
def Railwork(CurrentPath):
    pic = [[noise([i / xpix, j / ypix]) for j in range(xpix)] for i in range(ypix)]
    for p in range(25):
        pic[p][10] = 32
        pic[14][p] = 32

    for z in range(100000):
        nextStep = Point(x=CurrentPath[-1].x, y=CurrentPath[-1].y, z=CurrentPath[-1].z)

        if nextStep.x == goal.x and nextStep.z == goal.z:
            return CurrentPath
            break

        # ================================|NextAxis|===============================
        alea = randrange(4)
        # ========================= TO AVOID DUPLICATE TRY
        if (len(AxisTried) < 4):
            hasBeenDone = True

            if (len(AxisTried) == 0):
                AxisTried.append(alea)
            else:
                while (hasBeenDone):
                    isInList = False

                    for a in AxisTried:
                        if (a == alea):
                            isInList = True

                    if (isInList):
                        alea = randrange(4)

                    else:
                        AxisTried.append(alea)
                        hasBeenDone = False
            # ========================= END TO AVOID DUPLICATE TRY

            nextStep = TranslateToAxis(alea, nextStep)
            nextStep.y = int(round(pic[nextStep.x][nextStep.z] * 5 + 8, 0))

            # =========================================== CHECK IF NEW POSITION IS POSSIBLE

            blocksHere = client.readCube(Cube(
                min=Point(x=nextStep.x, y=nextStep.y, z=nextStep.z),
                max=Point(x=nextStep.x, y=nextStep.y, z=nextStep.z)
            ))

            # CHECK IF WE CAN PUT RAIL THERE
            if 178 != blocksHere.blocks[0].type:
                # if same level as previous
                if abs(nextStep.y == CurrentPath[-1].y):
                    PlaceRailAt(nextStep)
                    AxisTried.clear()
                    CurrentPath.append(nextStep)
                    # print("Tchou")

                else:
                    # if one block below or above of previous
                    if abs(nextStep.y - CurrentPath[-1].y) == 1:
                        # if one block below
                        if (nextStep.y + 1 == CurrentPath[-1].y):
                            PlaceRailAt(nextStep)
                            AxisTried.clear()
                            CurrentPath.append(nextStep)
                            # print("Tchou")

                        else:
                            # if one block above
                            if (nextStep.y - 1 == CurrentPath[-1].y) and not (nextStep.y == (CurrentPath[-1].y+1) == CurrentPath[-2].y):
                                # the last and penultimate are align
                                if (nextStep.x == CurrentPath[-1].x == CurrentPath[-2].x) or (
                                        nextStep.z == CurrentPath[-1].z == CurrentPath[-2].z):
                                    PlaceRailAt(nextStep)
                                    AxisTried.clear()
                                    CurrentPath.append(nextStep)
                                    # print("Tchou")

        # =======================|IF NOT POSSIBLE / go backward
        else:
            #END OF THE LINE / NEED TO GO BACKWARD
            client.spawnBlocks(Blocks(blocks=[
                Block(position=Point(x=CurrentPath[-1].x, y=CurrentPath[-1].y, z=CurrentPath[-1].z), type=AIR,
                      orientation=NORTH),
            ]))
            pic[CurrentPath[-1].x][CurrentPath[-1].z] = 50
            AxisTried.clear()
            if (len(CurrentPath) <= 4):
                print("NO PATH AVAILABLE - TRY AGAIN")
                pic.clear
                pic = [[noise([i / xpix, j / ypix]) for j in range(xpix)] for i in range(ypix)]

                #DELETE FOR FULL EXPERIENCE (Might take more time due to randomness)
                for p in range(25):
                    pic[p][10] = 32
                    pic[14][p] = 32
                #END OF FULL

            CurrentPath.pop()

    # =========================================== CHECK IF NEW POSITION IS POSSIBLE


def Mutation(PreviousPath):
    #Purge previous path + recreate goal
    ActivateCommandBlock(4, 4, -5)
    client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=goal.x, y=goal.y, z=goal.z), type=EMERALD_BLOCK, orientation=NORTH),
    ]))

    #regenerate map
    pic = [[noise([i / xpix, j / ypix]) for j in range(xpix)] for i in range(ypix)]
    for p in range(25):
        pic[p][10] = 32
        pic[14][p] = 32

    mutation = randrange(1, len(PreviousPath) - 3)
    for m in range(mutation):
        PreviousPath.pop()

    #Create path before mutation
    for r in range(2, len(PreviousPath)):
        client.spawnBlocks(Blocks(blocks=[
            Block(position=Point(x=PreviousPath[r].x, y=PreviousPath[r].y, z=PreviousPath[r].z), type=RAIL,
                  orientation=NORTH),
        ]))

    client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=PreviousPath[-1].x, y=12, z=PreviousPath[-1].z), type=SLIME,
              orientation=NORTH),
    ]))

    return Railwork(PreviousPath)


def SavePath(Saved):
    ActivateCommandBlock(2, 4, -5)
    for s in range(len(Saved)):
        client.spawnBlocks(Blocks(blocks=[
            Block(position=Point(x=Saved[s].x - 30, y=Saved[s].y, z=Saved[s].z), type=RAIL,
                  orientation=NORTH),
        ]))

        # add electrical rail
        if (s < (len(Saved) - 2) and s > 2):
            if (Saved[s - 1].x == Saved[s].x == Saved[s + 1].x) or (Saved[s - 1].z == Saved[s].z == Saved[s + 1].z):
                client.spawnBlocks(Blocks(blocks=[
                    Block(position=Point(x=Saved[s].x - 30, y=Saved[s].y - 1, z=Saved[s].z), type=REDSTONE_BLOCK,
                          orientation=NORTH),
                ]))
                client.spawnBlocks(Blocks(blocks=[
                    Block(position=Point(x=Saved[s].x - 30, y=Saved[s].y, z=Saved[s].z), type=GOLDEN_RAIL,
                          orientation=NORTH),
                ]))


# ================================================================================================================
# ================================================================================================================
# ================================================================================================================
# Clear previous area
print("map generation...")
# x2 54
client.fillCube(FillCubeRequest(
    cube=Cube(
        min=Point(x=-30, y=5, z=0),
        max=Point(x=54, y=15, z=24)
    ),
    type=AIR
))

# create a noise map for creating the map

noise = PerlinNoise(octaves=10, seed=randrange(10, 3000))
xpix, ypix = 25, 25  # size of map
pic = [[noise([i / xpix, j / ypix]) for j in range(xpix)] for i in range(ypix)]  # creation of noise map

while(int(round(pic[12][0] * 5 + 8, 0)) <= 8 and int(round(pic[12][0] * 5 + 8, 0)) >= 6):
    noise = PerlinNoise(octaves=10, seed=randrange(10, 3000))
    pic = [[noise([i / xpix, j / ypix]) for j in range(xpix)] for i in range(ypix)]

# generating physical map
for u in range(xpix):
    for o in range(ypix):
        # for each x/y coordonnate, we get the height by checking the noise map at the same coordinate
        client.fillCube(FillCubeRequest(
            cube=Cube(
                min=Point(x=u, y=5, z=o),
                max=Point(x=u, y=int(round(pic[u][o] * 5 + 7, 0)), z=o)
            ),
            type=RED_SANDSTONE
        ))


ActivateCommandBlock(6, 4, -5)

#Add First Rail
starter = Point(x=12, y=8, z=-1)
client.spawnBlocks(Blocks(blocks=[
    Block(position=Point(x=starter.x, y=starter.y, z=starter.z), type=RAIL, orientation=NORTH),
]))

#Purge Map
ActivateCommandBlock(4, 4, -5)

# Coordinates of first Rail to add in the list (later)
nextStep = Point(x=12, y=int(round(pic[12][0] * 5 + 8, 0)), z=-0)
previousStep = Point(x=12, y=8, z=-1)
penultimateStep = Point(x=12, y=8, z=-2)


#DELETE FOR FULL EXPERIENCE (Might take more time due to randomness)
goalx = randrange(1, 8)
goalz = randrange(1, 8)
#END OF DELETE

# Remove """ FOR FULL EXPERIENCE (Might take more time due to randomness)
"""
goalx = randrange(3, 22)
goalz = randrange(3, 22)
"""

#Generate Goal at height of 7 (7 is the average height)
goal = Point(x=goalx, y=int(round(pic[goalx][goalz] * 5 + 7, 0)), z=goalz)
while (goal.y != 7):
    # DELETE FOR FULL EXPERIENCE (Might take more time due to randomness)
    goalx = randrange(1, 8)
    goalz = randrange(1, 8)
    # END OF DELETE

    # Remove """ FOR FULL EXPERIENCE (Might take more time due to randomness)
    """
    goalx = randrange(3, 22)
    goalz = randrange(3, 22)
    """
    goal = Point(x=goalx, y=int(round(pic[goalx][goalz] * 5 + 7, 0)), z=goalz)
client.spawnBlocks(Blocks(blocks=[
    Block(position=Point(x=goal.x, y=goal.y, z=goal.z), type=EMERALD_BLOCK, orientation=NORTH),
]))

# DELETE FOR FULL EXPERIENCE (Might take more time due to randomness)
for p in range(25):
    pic[p][10] = 32
    pic[14][p] = 32
#END OF DELETE

client.spawnBlocks(Blocks(blocks=[
    Block(position=Point(x=nextStep.x, y=nextStep.y, z=nextStep.z), type=RAIL, orientation=NORTH),
]))

FirstPath = []
FirstPath.append(penultimateStep)
FirstPath.append(previousStep)
FirstPath.append(nextStep)

# Mutation
BestPath = Railwork(FirstPath.copy())
SavePath(BestPath)

while (True):
    pic = [[noise([i / xpix, j / ypix]) for j in range(xpix)] for i in range(ypix)]

    # DELETE FOR FULL EXPERIENCE (Might take more time due to randomness)
    for p in range(25):
        pic[p][10] = 32
        pic[14][p] = 32
    # END OF DELETE

    CurrentTryPath.clear
    CurrentTryPath = Mutation(BestPath.copy()).copy()

    print("current")
    print(len(CurrentTryPath))
    print("Best")
    print(len(BestPath))
    print("-")

    if (len(CurrentTryPath) < len(BestPath)):
        print("======")
        print("Faster")
        print("======")
        BestPath.clear()
        BestPath = CurrentTryPath.copy()
        SavePath(BestPath)