'''
Escape key - Exit game
F1 - Toggle debug mode
F2 - Reload world
W - Jump
A - Move left
D - Move right
Q - Move inventory selection left
E - Move inventory selection right
S - Save world
R - Recenter mouse
Enter/Return - Increase center height offset
Right Shift - Decrease center height offset
'''

#add caves
#increase frame rate to 30 or 25
#make it so the game doesnt crash if you go to the right corner of the world
#fix the block placement mechanic (placed blocks dont appear in the left half of the screen)
#make it so that if you destroy a block it adds back onto the block count in your inventory
#fix the sword image
#add clouds
#make it so that the cursor cant go over the Y boundaries of the screen

__author__ = 'Harrison/Katznboyz/Katznboyz1'
__language__ = 'Python 3.5.0/Pygame 1.9.4'

import pygame as pygame
import os as os
import random as random
import time as time
import math as math
import _thread as thread

if ('default-terraindata.hlworld' not in os.listdir('./utils/saves')):
    file = open('./utils/saves/default-terraindata.hlworld', 'w')
    file.write('{}')
    file.close()

class game:
    data = {}
    otherdata = {}
    screenSize = (0, 0)
    stage = 'startscreen'
    screen = None
    running = True
    clock = pygame.time.Clock()
    fillColor = (184, 240, 255)
    runs = 0
    debugMode = False
    fps = 0
    charPosition = [0, 0]
    blockWidthPixels = 60
    tickFps = 35
    inventory = {'wood': math.inf, 'stone': math.inf, 'dirt': math.inf, 'leaves': math.inf, 'darkSword': 1, 'log': math.inf}
    inventorySlotSelected = 0
    swordFacingSide = 'L'
    mousePos = [0, 0]
    centerPosOffset = 0
    class kdowns:
        left = False
        right = False
    def text(fontFace, size, text, color):
        font = pygame.font.Font(fontFace, size)
        text = font.render(text, 1, color)
        return text
    def generateTerrainData(worldMaxHeight = 100, worldMinHeight = 100, worldWidth = 1000):
        dataDict = {}
        lastchunk = 0
        for chunk in range(int(worldWidth)):
            dataDict[chunk] = {}
            dataDict[chunk]['height'] = lastchunk + random.choice([-1, 0, 0, 0, 0, 1])
            dataDict[chunk]['belowGround'] = []
            for chunk_below in range(int(worldMinHeight)):
                trues = []
                for _iter1 in range(20):
                    trues += [True]
                dataDict[chunk]['belowGround'].append(random.choice([*trues, False]))
            nones = []
            for _iter2 in range(10):
                nones += ['']
            dataDict[chunk]['foliage'] = random.choice([*nones, 'tree'])
            if (dataDict[chunk]['foliage'] != ''):
                if (dataDict[chunk]['foliage'].split(':')[0] == 'tree'):
                    dataDict[chunk]['treeHeight'] = random.randint(3, 5)
            lastchunk = dataDict[chunk]['height']
            #world does not obey min/max height boundaries yet
        return dataDict

exec('game.data = {}'.format(str(open('./utils/saves/default-terraindata.hlworld').read())))
exec('game.otherdata = {}'.format(str(open('./utils/saves/default-otherdata.hlworld').read())))
game.charPosition = game.otherdata['position']

#game.data = {} #refresh it for testing
#game.otherdata = {} #refresh it for testing

if (game.data == {} or game.data == ''):
    game.data = game.generateTerrainData()

if (game.otherdata == {} or game.otherdata == ''):
    game.otherdata = {'position': game.charPosition, 'blockPlacementData': {}}
    for newBlockPosition in range(max(game.data)):
        game.otherdata['blockPlacementData'][newBlockPosition] = {}

pygame.display.init()
pygame.font.init()
pygame.mouse.set_visible(False)

game.screenSize = (pygame.display.Info().current_w, pygame.display.Info().current_h)

game.screen = pygame.display.set_mode(game.screenSize, pygame.FULLSCREEN)

game.mousePos = [game.screen.get_size()[0] // 2, game.screen.get_size()[1] // 2]

last = time.time()
current = time.time()

def saveThread():
    while (game.running):
        file = open('./utils/saves/default-terraindata.hlworld', 'w')
        file.write(str(game.data))
        file.close()
        file = open('./utils/saves/default-otherdata.hlworld', 'w')
        file.write(str(game.otherdata))
        file.close()
        time.sleep(2)

thread.start_new_thread(saveThread, ())

centerHeight = 0

inventoryOrder = [*game.inventory]

spriteHeight = 0

while (game.running):
    last = time.time()
    game.screen.fill(game.fillColor)

    events = pygame.event.get()

    for event in events:
        if (event.type == pygame.QUIT):
            game.running = False
        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_ESCAPE):
                game.running = False
            if (event.key == pygame.K_F1):
                    game.debugMode = not game.debugMode
    
    if (game.stage == 'startscreen'):
        loadingScreenMessage = pygame.image.load('./utils/images/misc/loadingScreenMessage.png')
        aspectRatio = loadingScreenMessage.get_size()[0] / loadingScreenMessage.get_size()[1]
        loadingScreenMessage = pygame.transform.scale(loadingScreenMessage, (int(game.screen.get_size()[1] * aspectRatio), int(game.screen.get_size()[1])))
        loadingScreenMessage.set_colorkey((255, 0, 255))
        loadingScreenMessage = loadingScreenMessage.convert_alpha()
        lsX, lsY = 0, 0
        lsX = ((game.screen.get_size()[0] - loadingScreenMessage.get_size()[0]) / 2)
        game.screen.blit(loadingScreenMessage, (lsX, lsY))
        if (game.debugMode):
            game.screen.blit(game.text('./utils/fonts/arial.ttf', 30, str(game.fps), (0, 0, 0)), (0, 0))
        for event in events:
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_RETURN):
                    game.stage = 'ingame'

    elif (game.stage == 'ingame'):
        for event in events:
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_a):
                    game.kdowns.left = True
                if (event.key == pygame.K_d):
                    game.kdowns.right = True
                if (event.key == pygame.K_w and game.charPosition[1] == 0):
                    game.charPosition[1] = 1 * game.blockWidthPixels
                if (event.key == pygame.K_F2):
                    game.data = game.generateTerrainData()
                    game.otherdata = {'position': game.charPosition, 'blockPlacementData': {}}
                    for newBlockPosition in range(max(game.data)):
                        game.otherdata['blockPlacementData'][newBlockPosition] = {}
                if (event.key == pygame.K_q):
                    if (game.inventorySlotSelected < len(game.inventory) - 1):
                        game.inventorySlotSelected += 1
                if (event.key == pygame.K_e):
                    if (game.inventorySlotSelected > 0):
                        game.inventorySlotSelected -= 1
                if (event.key == pygame.K_s):
                    file = open('./utils/saves/default-terraindata.hlworld', 'w')
                    file.write(str(game.data))
                    file.close()
                    file = open('./utils/saves/default-otherdata.hlworld', 'w')
                    file.write(str(game.otherdata))
                    file.close()
                if (event.key == pygame.K_r):
                    game.mousePos = [game.screen.get_size()[0] // 2, (game.data[int(int(game.screen.get_size()[0] // 2 // game.blockWidthPixels) + game.charPosition[0])]['height'] * game.blockWidthPixels)]
                if (event.key == pygame.K_RETURN):
                    game.centerPosOffset += 1
                if (event.key == pygame.K_RSHIFT):
                    game.centerPosOffset -= 1
            elif (event.type == pygame.KEYUP):
                if (event.key == pygame.K_a):
                    game.kdowns.left = False
                if (event.key == pygame.K_d):
                    game.kdowns.right = False
            elif (event.type == pygame.MOUSEBUTTONDOWN):
                if (event.button == 1):
                    mouseClickedPosition = game.mousePos
                    mouseClickedPosition = [mouseClickedPosition[0] + (game.blockWidthPixels // 2), mouseClickedPosition[1] + (game.blockWidthPixels // 2)]
                    mouseChunkClicked = [(mouseClickedPosition[0] // game.blockWidthPixels), (mouseClickedPosition[1] // game.blockWidthPixels)]
                    mouseClickXBlock = game.charPosition[0]
                    mouseClickXBlock -= (game.screen.get_size()[0] // game.blockWidthPixels) // 2
                    mouseClickXBlock += mouseChunkClicked[0]
                    mouseClickXBlock = int(mouseClickXBlock)
                    blockPlaced = 'blank_block_1.png'
                    blockSelectedInInventory = inventoryOrder[game.inventorySlotSelected]
                    placeBlock = True
                    if (blockSelectedInInventory == 'wood'):
                        blockPlaced = 'wood_block_1.png'
                    elif (blockSelectedInInventory == 'stone'):
                        blockPlaced = 'stone_block_1.png'
                    elif (blockSelectedInInventory == 'dirt'):
                        blockPlaced = 'plain_dirt_block_1.png'
                    elif (blockSelectedInInventory == 'leaves'):
                        blockPlaced = 'tree_leaves_block_1.png'
                    elif (blockSelectedInInventory == 'log'):
                        blockPlaced = 'tree_stump_block_1.png'
                    else:
                        placeBlock = False
                    if (placeBlock and game.inventory[blockSelectedInInventory] > 0):
                        game.otherdata['blockPlacementData'][mouseClickXBlock][mouseChunkClicked[1]] = blockPlaced
                        game.inventory[blockSelectedInInventory] -= 1
                if (event.button == 3):
                    mouseClickedPosition = game.mousePos
                    mouseClickedPosition = [mouseClickedPosition[0] + (game.blockWidthPixels // 2), mouseClickedPosition[1] + (game.blockWidthPixels // 2)]
                    mouseChunkClicked = [(mouseClickedPosition[0] // game.blockWidthPixels), (mouseClickedPosition[1] // game.blockWidthPixels)]
                    mouseClickXBlock = game.charPosition[0]
                    mouseClickXBlock -= (game.screen.get_size()[0] // game.blockWidthPixels) // 2
                    mouseClickXBlock += mouseChunkClicked[0]
                    mouseClickXBlock = int(mouseClickXBlock)
                    blockPlaced = 'blank_block_1.png'
                    blockSelectedInInventory = inventoryOrder[game.inventorySlotSelected]
                    try:
                        del game.otherdata['blockPlacementData'][mouseClickXBlock][mouseChunkClicked[1]]
                    except:
                        pass
                if (event.button == 4):
                    if (game.inventorySlotSelected < len(game.inventory) - 1):
                        game.inventorySlotSelected += 1
                if (event.button == 5):
                    if (game.inventorySlotSelected > 0):
                        game.inventorySlotSelected -= 1

        if (game.kdowns.left):
            game.charPosition[0] -= (0.5)# * ((game.tickFps / game.fps) / 0.5)
        if (game.kdowns.right):
            game.charPosition[0] += (0.5)# * ((game.tickFps / game.fps) / 0.5)

        gameBlockAvailableWidth = game.screen.get_size()[0] // game.blockWidthPixels

        if (game.charPosition[0] < (gameBlockAvailableWidth // 2)):
            game.charPosition[0] = (gameBlockAvailableWidth // 2)

        centerHeight = -(game.data[((game.screen.get_size()[0] // 2) // game.blockWidthPixels) + int(game.charPosition[0])]['height'] * game.blockWidthPixels) + (game.blockWidthPixels * 5) + game.charPosition[1] + (game.centerPosOffset * game.blockWidthPixels)

        for block in range(gameBlockAvailableWidth):
            currentChunk = game.data[int(game.charPosition[0] + block)]
            height = currentChunk['height']
            blockImage = pygame.image.load('./utils/images/blocks/grassy_dirt_block_1.png')
            blockImage = pygame.transform.scale(blockImage, (game.blockWidthPixels, game.blockWidthPixels))
            blockY = (height * game.blockWidthPixels) + ((game.screen.get_size()[1] // 2)) + centerHeight
            game.screen.blit(blockImage, ((block * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), blockY))
            blockImageBelow = pygame.image.load('./utils/images/blocks/plain_dirt_block_1.png')
            blockImageBelow = pygame.transform.scale(blockImage, (game.blockWidthPixels, game.blockWidthPixels))
            belowChunk = 0
            if (currentChunk['foliage'].split(':')[0] == 'tree'):
                treeStumpImage = pygame.image.load('./utils/images/blocks/tree_stump_block_1.png')
                treeStumpImage = pygame.transform.scale(treeStumpImage, (game.blockWidthPixels, game.blockWidthPixels))
                treeLeavesImage = pygame.image.load('./utils/images/blocks/tree_leaves_block_1.png')
                treeLeavesImage = pygame.transform.scale(treeLeavesImage, (game.blockWidthPixels, game.blockWidthPixels))
                stumpTopHeight = 0
                for stump in range(currentChunk['treeHeight']):
                    stumpTopHeight = stump
                    game.screen.blit(treeStumpImage, ((block * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stump + 1)))))
                game.screen.blit(treeLeavesImage, (((block - 1) * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 1)))))
                game.screen.blit(treeLeavesImage, ((block * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 1)))))
                game.screen.blit(treeLeavesImage, (((block + 1) * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 1)))))
                game.screen.blit(treeLeavesImage, (((block - 1) * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 2)))))
                game.screen.blit(treeLeavesImage, ((block * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 2)))))
                game.screen.blit(treeLeavesImage, (((block + 1) * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 2)))))
                game.screen.blit(treeLeavesImage, (((block - 1) * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 3)))))
                game.screen.blit(treeLeavesImage, ((block * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 3)))))
                game.screen.blit(treeLeavesImage, (((block + 1) * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 3)))))
                game.screen.blit(treeLeavesImage, ((block * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 4)))))
                game.screen.blit(treeLeavesImage, (((block + 2) * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 2)))))
                game.screen.blit(treeLeavesImage, (((block - 2) * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stumpTopHeight + 2)))))
            for block_below in currentChunk['belowGround']:
                belowChunk += 1
                availBelowBlocks = ((game.screen.get_size()[1] // game.blockWidthPixels) - (blockY // game.blockWidthPixels))
                if (belowChunk < availBelowBlocks):
                    if (currentChunk['belowGround'][belowChunk]):
                        if (belowChunk < 5):
                            bblockImage = pygame.image.load('./utils/images/blocks/{}'.format(('plain_dirt_block_1.png')))
                        else:
                            bblockImage = pygame.image.load('./utils/images/blocks/{}'.format(('stone_block_1.png')))
                    else:
                        bblockImage = pygame.image.load('./utils/images/blocks/{}'.format(('plain_dirt_block_1.png')))
                    bblockImage = pygame.transform.scale(bblockImage, (game.blockWidthPixels, game.blockWidthPixels))
                    ycoord = blockY + (belowChunk * game.blockWidthPixels)
                    game.screen.blit(bblockImage, ((block * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), ycoord))
            range1 = int(block + game.charPosition[0]) - (game.screen.get_size()[0] // 2 // game.blockWidthPixels) 
            for block_placed in game.otherdata['blockPlacementData'][range1]: #only blits to right half of screen for some reason
                blockPath = game.otherdata['blockPlacementData'][range1][block_placed]
                blockToBeLoaded = pygame.image.load('./utils/images/blocks/{}'.format(blockPath))
                blockToBeLoaded = pygame.transform.scale(blockToBeLoaded, (game.blockWidthPixels, game.blockWidthPixels))
                posX = (block * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])) + (game.screen.get_size()[0] // 2) - (game.screen.get_size()[0] // 2)
                game.screen.blit(blockToBeLoaded, (posX, (block_placed * game.blockWidthPixels) + 0 + centerHeight))

        characterSprite = pygame.image.load('./utils/images/sprites/character_still_1.png')
        aspectRatio = characterSprite.get_size()[1] / characterSprite.get_size()[0]
        characterSprite = pygame.transform.scale(characterSprite, (game.blockWidthPixels, int(game.blockWidthPixels * aspectRatio)))
        characterSprite.set_colorkey((255, 255, 255))
        characterSprite = characterSprite.convert_alpha()
        spriteHeight = game.data[int(game.charPosition[0] + (game.screen.get_size()[0] // 2) // game.blockWidthPixels)]['height'] * game.blockWidthPixels
        spriteHeight += game.screen.get_size()[1] // 2
        spriteHeight -= characterSprite.get_size()[1]
        spriteHeight -= game.charPosition[1]
        spriteHeight += centerHeight
        spriteX = (game.screen.get_size()[0] // 2)
        spriteX = spriteX // game.blockWidthPixels
        spriteX *= game.blockWidthPixels
        game.screen.blit(characterSprite, (spriteX, spriteHeight))

        for inventorySlots in range(len(game.inventory)):
            inventorySlotIcon = pygame.image.load('./utils/images/icons/inventory_outline_gray_icon.jpg')
            inventorySlotIcon = pygame.transform.scale(inventorySlotIcon, (50, 50))
            game.screen.blit(inventorySlotIcon, ((game.screen.get_size()[0] - ((inventorySlots + 1) * 50)) - 20, 20))
            if (game.inventorySlotSelected == inventorySlots):
                inventorySlotIconSelected = pygame.image.load('./utils/images/icons/inventory_selected_outline_green_icon.png')
                inventorySlotIconSelected = pygame.transform.scale(inventorySlotIconSelected, (50, 50))
                game.screen.blit(inventorySlotIconSelected, ((game.screen.get_size()[0] - ((inventorySlots + 1) * 50)) - 20, 20))
            if (inventoryOrder[inventorySlots] == 'darkSword'):
                inventorySlotItemIcon = pygame.image.load('./utils/images/icons/inventoryIcons/{}'.format('darkSword.jpg'))
            else:
                inventorySlotItemIcon = pygame.image.load('./utils/images/icons/inventoryIcons/{}.png'.format(inventoryOrder[inventorySlots]))
            inventorySlotItemIcon = pygame.transform.scale(inventorySlotItemIcon, (30, 30))
            game.screen.blit(inventorySlotItemIcon, ((game.screen.get_size()[0] - ((inventorySlots + 1) * 50)) - 10, 30))
            game.screen.blit(game.text('./utils/fonts/arial.ttf', 15, str(game.inventory[inventoryOrder[inventorySlots]]), (0, 0, 0)), ((game.screen.get_size()[0] - ((inventorySlots + 1) * 50)) - 13, 47))
        
        if (inventoryOrder[game.inventorySlotSelected] == 'darkSword'):
            swordImage = pygame.image.load('./utils/images/weapons/darkSword1-facing_{}.png'.format(game.swordFacingSide))
            swordImage = pygame.transform.scale(swordImage, (int(game.blockWidthPixels // 1.5), int(game.blockWidthPixels // 1.5)))
            swordImage.set_colorkey((255, 255, 255))
            swordImage = swordImage.convert_alpha()
            halfSpriteWidth = characterSprite.get_size()[0] // 2
            game.screen.blit(swordImage, ((game.screen.get_size()[0] // 2) + (halfSpriteWidth if game.swordFacingSide == 'R' else -halfSpriteWidth), spriteHeight + 17))
            #turn white background transparent

        if (game.debugMode):
            runCountText = game.text('./utils/fonts/arial.ttf', 20, str(game.runs) + ' - total runs', (0, 0, 0))
            fpsCountText = game.text('./utils/fonts/arial.ttf', 20, str(game.fps) + ' - current fps', (0, 0, 0))
            playerPos = game.text('./utils/fonts/arial.ttf', 20, 'X:{}   Y:{}   MP:{}'.format(int(game.charPosition[0]), int(game.charPosition[1]), game.mousePos), (0, 0, 0))
            game.screen.blit(runCountText, (0, 0))
            game.screen.blit(fpsCountText, (0, (runCountText.get_size()[1])))
            game.screen.blit(playerPos, (0, (fpsCountText.get_size()[1] + runCountText.get_size()[1])))
        if (game.charPosition[1] > 0):
            game.charPosition[1] -= game.blockWidthPixels // 6
            if (game.charPosition[1] < 1):
                game.charPosition[1] = 0
        
        mousePos = pygame.mouse.get_pos()
        if (game.mousePos[0] < game.screen.get_size()[0] // 2):
            game.swordFacingSide = 'L'
        else:
            game.swordFacingSide = 'R'
        
        mouseCursorIcon = 'mouse_cursor.png'
        mouseCursorImage = pygame.image.load('./utils/images/icons/{}'.format(mouseCursorIcon))
        mouseCursorImage = pygame.transform.scale(mouseCursorImage, (game.blockWidthPixels, game.blockWidthPixels))
        mouseCursorImage.set_colorkey((255, 0, 255))
        mouseCursorImage = mouseCursorImage.convert_alpha()
        mouseMovement = pygame.mouse.get_rel()
        game.mousePos[0] += mouseMovement[0]
        game.mousePos[1] += mouseMovement[1]
        game.screen.blit(mouseCursorImage, (game.mousePos[0], game.mousePos[1] + centerHeight))

        blockHoverIcon = pygame.image.load('./utils/images/icons/blockSelectionOutline.png')
        blockHoverIcon = pygame.transform.scale(blockHoverIcon, (game.blockWidthPixels, game.blockWidthPixels))
        blockHoverIcon.set_colorkey((255, 255, 255))
        blockHoverIcon = blockHoverIcon.convert_alpha()
        ActualMousePos = [(game.mousePos[0] + (game.blockWidthPixels // 2)), (game.mousePos[1] + (game.blockWidthPixels // 2))]
        game.screen.blit(blockHoverIcon, (((ActualMousePos[0] // game.blockWidthPixels) * game.blockWidthPixels), ((ActualMousePos[1] // game.blockWidthPixels) * game.blockWidthPixels) + (0 + centerHeight)))
    
    if (game.mousePos[0] < 0):
        game.mousePos[0] = 0
    elif (game.mousePos[0] > game.screen.get_size()[0] - game.blockWidthPixels):
        game.mousePos[0] = game.screen.get_size()[0] - game.blockWidthPixels

    pygame.display.update()
    game.clock.tick(game.tickFps)
    game.runs += 1
    current = time.time()
    game.fps = int(1 / (current - last))

pygame.quit()
exit()
