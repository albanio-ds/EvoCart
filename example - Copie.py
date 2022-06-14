import math
import grpc
import random
import time
import minecraft_pb2_grpc
from minecraft_pb2 import *
from perlin_noise import PerlinNoise
from random import randrange


class MyPoint:
    x = 0
    y = 0
    z = 0

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    # true if the point is downer the other point
    def IsDown(self, MyPointB):
        if self.y < MyPointB.y:
            return True
        return False

    # return the downer point from a point list
    def GetMinPoint(self, MyPointList):
        res = MyPointList[0]
        for MyPoint in MyPointList:
            if MyPoint.IsDown(res):
                res = MyPoint
        return res

    # operetor equal -- return true if same coordinates
    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.z == other.z:
            return True
        return False

    # operator to string
    def __str__(self):
        return "({0}, {1}, {2})".format(self.x, self.y, self.z)

    # return distance between two points
    def Distance(self, other):
        return math.dist((self.x, self.z), (other.x, other.z))


channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)
"""
print("map generation...")
# Clear previous area
client.fillCube(FillCubeRequest(
    cube=Cube(
        min=Point(x=0, y=5, z=-0),
        max=Point(x=50, y=31, z=50)
    ),
    type=AIR
))
"""


# ================================================================================================================
# create a noise map for creating the map

noise = PerlinNoise(octaves=10, seed=2056)
xpix, ypix = 25, 25  # size of map
pic = [[noise([i / xpix, j / ypix]) for j in range(xpix)] for i in range(ypix)]  # creation of noise map

AxisTried = []
RailPlaced = []
CurrentPath = []
NewPath = []
BestPath = []
BestPathLenght = 10000

# generating physical map
"""
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

client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=6, y=4, z=-5), type=REDSTONE_BLOCK, orientation=NORTH),
    ]))

    time.sleep(0.5)

    client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=6, y=4, z=-5), type=AIR, orientation=NORTH),
    ]))
"""
#start at 12,height,0
"""starter = Point(x=12, y=int(round(pic[12][0] * 5 + 8, 0)), z=-0)
nextStep = Point(x=12, y=int(round(pic[12][0] * 5 + 8, 0)), z=-0)
penultimateStep = Point(x=12, y= 7, z=-1)
"""
starter = Point(x=12, y=8, z=-1)
nextStep = Point(x=12, y=int(round(pic[12][0] * 5 + 8, 0)), z=-0)
penultimateStep = Point(x=12, y=8, z=-2)

client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=starter.x, y=starter.y, z=starter.z), type=RAIL, orientation=NORTH),
    ]))

goalx = randrange(1,23)
goalz = randrange(1,23)
goal = Point(x = goalx, y = int(round(pic[goalx][goalz] * 5 + 7, 0)), z = goalz)

client.spawnBlocks(Blocks(blocks=[
    Block(position=Point(x=4, y=4, z=-5), type=REDSTONE_BLOCK, orientation=NORTH),
]))
time.sleep(0.5)
client.spawnBlocks(Blocks(blocks=[
    Block(position=Point(x=4, y=4, z=-5), type=AIR, orientation=NORTH),
]))

nextStep = Point(x=12, y=int(round(pic[12][0] * 5 + 8, 0)), z=-0)
penultimateStep = Point(x=12, y=7, z=-1)
previousStep = Point(x=nextStep.x, y=nextStep.y, z=nextStep.z)

#===============================================|RAILWORK|
for e in range(50):
    pic = [[noise([i / xpix, j / ypix]) for j in range(xpix)] for i in range(ypix)]  # RESET
    RailPlaced.append([penultimateStep, nextStep, nextStep])

    client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=goal.x, y=goal.y, z=goal.z), type=EMERALD_BLOCK, orientation=NORTH),
    ]))

    client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=nextStep.x, y=nextStep.y, z=nextStep.z), type=RAIL, orientation=NORTH),
    ]))

    for z in range(100000):
        if(nextStep.x == goal.x and nextStep.z == goal.z):

            if(len(RailPlaced) < BestPathLenght):
                #SAVE BEST TRACK
                client.spawnBlocks(Blocks(blocks=[
                    Block(position=Point(x=2, y=4, z=-5), type=REDSTONE_BLOCK, orientation=NORTH),
                ]))
                time.sleep(0.5)
                client.spawnBlocks(Blocks(blocks=[
                    Block(position=Point(x=2, y=4, z=-5), type=AIR, orientation=NORTH),
                ]))
                BestPath = CurrentPath
                BestPathLenght = len(RailPlaced)
                print("================")
                print("NEW FASTER TRACK")
                print("================")
                #END SAVE BEST TRACK

                #GENERATE BEST TRACK IN RECORD
                for l in CurrentPath:
                    client.spawnBlocks(Blocks(blocks=[
                        Block(position=Point(x=l.x - 30 , y=l.y, z=l.z), type=RAIL,
                              orientation=NORTH),
                    ]))
                client.spawnBlocks(Blocks(blocks=[
                    Block(position=Point(x=goal.x - 30, y=goal.y + 1, z=goal.z), type=RAIL,
                          orientation=NORTH),
                ]))
                #END GENERATE BEST TRACK IN RECORD

                time.sleep(0.5)

                #GENERATE NEW TRACK FROM PREVIOUS WITH MUTATION
                client.spawnBlocks(Blocks(blocks=[
                    Block(position=Point(x=4, y=4, z=-5), type=REDSTONE_BLOCK, orientation=NORTH),
                ]))
                time.sleep(0.5)
                client.spawnBlocks(Blocks(blocks=[
                    Block(position=Point(x=4, y=4, z=-5), type=AIR, orientation=NORTH),
                ]))

                #GENERATE NEW TRACK FROM PREVIOUS WITH MUTATION
                mutation = randrange(len(BestPath)-1)
                for u in range(len(BestPath) - mutation):
                    client.spawnBlocks(Blocks(blocks=[
                        Block(position=Point(x=BestPath[u].x, y=BestPath[u].y, z=BestPath[u].z), type=RAIL,
                              orientation=NORTH),
                    ]))

                for p in range(mutation):
                    RailPlaced.pop()
                    CurrentPath.pop()


                penultimateStep = RailPlaced[-2][1]
                previousStep = RailPlaced[-1][1]
                nextStep = RailPlaced[-1][1]

                client.spawnBlocks(Blocks(blocks=[
                    Block(position=Point(x=penultimateStep.x, y=penultimateStep.y, z=penultimateStep.z), type=RAIL,
                          orientation=NORTH),
                ]))
                client.spawnBlocks(Blocks(blocks=[
                    Block(position=Point(x=previousStep.x, y=previousStep.y, z=previousStep.z), type=RAIL,
                          orientation=NORTH),
                ]))
                client.spawnBlocks(Blocks(blocks=[
                    Block(position=Point(x=nextStep.x, y=nextStep.y, z=nextStep.z), type=RAIL,
                          orientation=NORTH),
                ]))
                time.sleep(15)
            break


        if(len(RailPlaced) >= BestPathLenght):
            print("========")
            print("TOO MUCH")
            print("========")

            # GENERATE NEW TRACK FROM PREVIOUS WITH MUTATION
            client.spawnBlocks(Blocks(blocks=[
                Block(position=Point(x=4, y=4, z=-5), type=REDSTONE_BLOCK, orientation=NORTH),
            ]))
            time.sleep(0.5)
            client.spawnBlocks(Blocks(blocks=[
                Block(position=Point(x=4, y=4, z=-5), type=AIR, orientation=NORTH),
            ]))

            # GENERATE NEW TRACK FROM PREVIOUS WITH MUTATION
            mutation = randrange(len(BestPath) - 1)
            for m in range(len(BestPath) - mutation):
                client.spawnBlocks(Blocks(blocks=[
                    Block(position=Point(x=BestPath[m].x, y=BestPath[m].y, z=BestPath[m].z), type=RAIL,
                          orientation=NORTH),
                ]))

            for p in range(mutation):
                RailPlaced.pop()
                CurrentPath.pop()

            penultimateStep = RailPlaced[-2][1]
            previousStep = RailPlaced[-1][1]
            nextStep = RailPlaced[-1][1]

            break

        # ==================================================================
        # ==================================================================|RAIL SETUP
        # ==================================================================

        # ================================|NextAxis|
        alea = randrange(4)
        # AVOID DUPLICATE
        if(len(AxisTried) < 4):
            hasBeenDone = True

            if(len(AxisTried) == 0):
                AxisTried.append(alea)
            else:
                while(hasBeenDone):
                    isInList = False

                    for a in AxisTried:
                        if(a == alea):
                            isInList = True

                    if(isInList):
                        alea = randrange(4)

                    else:
                        AxisTried.append(alea)
                        hasBeenDone = False

            # 0 North
            # 1 South
            # 2 East
            # 3 West
            #North/South
            if(True):
                if(alea<2):
                    #North
                    if(alea<1):
                        if(nextStep.z + 1 < 24):
                            nextStep.z += 1
                    else:
                        #South
                        if (nextStep.z + 1 > 1):
                            nextStep.z -= 1
                #East/West
                else:
                    if(alea>2):
                        if (nextStep.x + 1 < 24):
                            nextStep.x += 1
                    else:
                        if (nextStep.x + 1 > 1):
                            nextStep.x -= 1

            nextStep.y = int(round(pic[nextStep.x][nextStep.z] * 5 + 8, 0))

            # ==================================================================
            # ==================================================================|CHECK IF POSSIBLE
            # ==================================================================

            blocksHere = client.readCube(Cube(
                 min=Point(x=nextStep.x, y=nextStep.y, z=nextStep.z),
                 max=Point(x=nextStep.x, y=nextStep.y, z=nextStep.z)
            ))

            #CHECK IF WE CAN PUT RAIL THERE
            if 178 != blocksHere.blocks[0].type and not abs(nextStep.y - previousStep.y) >= 2 and not((nextStep.y == penultimateStep.y) and (previousStep.y + 1 == nextStep.y)):
                if abs(nextStep.y - previousStep.y) == 1:

                    if(penultimateStep.x == nextStep.x or nextStep.z == penultimateStep.z):
                        client.spawnBlocks(Blocks(blocks=[
                            Block(position=Point(x=nextStep.x, y=nextStep.y, z=nextStep.z), type=RAIL,
                                  orientation=NORTH),
                        ]))
                        CurrentPath.append(previousStep)
                        RailPlaced.append([penultimateStep, previousStep, nextStep])
                        penultimateStep = Point(x=previousStep.x, y=previousStep.y, z=previousStep.z)
                        previousStep = Point(x=nextStep.x, y=nextStep.y, z=nextStep.z)
                        AxisTried.clear()
                        print("Tchou")


                    else:
                         nextStep = Point(x= previousStep.x,y= previousStep.y,z= previousStep.z)

                else:
                    client.spawnBlocks(Blocks(blocks=[
                        Block(position=Point(x=nextStep.x, y=nextStep.y, z=nextStep.z), type=RAIL, orientation=NORTH),
                    ]))
                    CurrentPath.append(previousStep)
                    RailPlaced.append([penultimateStep, previousStep, nextStep])
                    penultimateStep = Point(x=previousStep.x, y=previousStep.y, z=previousStep.z)
                    previousStep = Point(x=nextStep.x, y=nextStep.y, z=nextStep.z)
                    AxisTried.clear()
                    print("Tchou")

            else:
                nextStep = Point(x= previousStep.x,y= previousStep.y,z= previousStep.z)

        #=======================|IF NOT POSSIBLE
        else:
            print("END OF THE LINE")
            client.spawnBlocks(Blocks(blocks=[
                Block(position=Point(x=nextStep.x, y=nextStep.y, z=nextStep.z), type=AIR,
                      orientation=NORTH),
            ]))
            pic[nextStep.x][nextStep.z] = 50

            penultimateStep = RailPlaced[-2][0]
            previousStep = RailPlaced[-2][1]
            nextStep = RailPlaced[-1][1]

            penultimateStep = Point(x=previousStep.x, y=previousStep.y, z=previousStep.z)
            previousStep = Point(x=nextStep.x, y=nextStep.y, z=nextStep.z)
            RailPlaced.pop()
            CurrentPath.pop()
            AxisTried.clear()


    #======================
    client.spawnBlocks(Blocks(blocks=[
        Block(position=Point(x=21, y=5, z=-6), type=AIR, orientation=NORTH),
    ]))