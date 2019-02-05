'''
Escape key - Exit game
F1 - Toggle debug mode
F2 - Reload world
Z - Zoom in [GLITCHY]
X - Zoom out [GLITCHY]
'''

#fix the texturing of the subterrain blocks

import pygame as pygame
import os as os
import random as random
import time as time
import _thread as thread

if ('default.hlworld' not in os.listdir('./utils/saves')):
    file = open('./utils/saves/default.hlworld', 'w')
    file.write('{}')
    file.close()

class game:
    data = None
    screenSize = (0, 0)
    screen = None
    running = True
    clock = pygame.time.Clock()
    fillColor = (184, 240, 255)
    runs = 0
    debugMode = False
    fps = 0
    charPosition = [0, 0]
    blockWidthPixels = 48
    tickFps = 35
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

exec('game.data = {}'.format(str(open('./utils/saves/default.hlworld').read())))

if (game.data == {}):
    game.data = game.generateTerrainData()

pygame.display.init()
pygame.font.init()
pygame.mouse.set_visible(False)

game.screenSize = (pygame.display.Info().current_w, pygame.display.Info().current_h)

game.screen = pygame.display.set_mode(game.screenSize, pygame.FULLSCREEN)

last = time.time()
current = time.time()

def saveThread():
    while (game.running):
        time.sleep(5)
        file = open('./utils/saves/default.hlworld', 'w')
        file.write(str(game.data))
        file.close()

thread.start_new_thread(saveThread, ())

centerHeight = 0

while (game.running):
    last = time.time()
    game.screen.fill(game.fillColor)

    for event in pygame.event.get():
        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_ESCAPE):
                game.running = False
            if (event.key == pygame.K_F1):
                game.debugMode = not game.debugMode
            if (event.key == pygame.K_a):
                game.kdowns.left = True
            if (event.key == pygame.K_d):
                game.kdowns.right = True
            if (event.key == pygame.K_w):
                game.charPosition[1] = 1 * game.blockWidthPixels
            if (event.key == pygame.K_z):
                game.blockWidthPixels += 1
            if (event.key == pygame.K_x):
                game.blockWidthPixels -= 1
            if (event.key == pygame.K_F2):
                game.data = game.generateTerrainData()
        elif (event.type == pygame.KEYUP):
            if (event.key == pygame.K_a):
                game.kdowns.left = False
            if (event.key == pygame.K_d):
                game.kdowns.right = False

    if (game.kdowns.left):
        game.charPosition[0] -= (0.5)# * (game.tickFps / game.fps)
    if (game.kdowns.right):
        game.charPosition[0] += (0.5)# * (game.tickFps / game.fps)

    gameBlockAvailableWidth = game.screen.get_size()[0] // game.blockWidthPixels

    if (game.charPosition[0] < (gameBlockAvailableWidth // 2)):
        game.charPosition[0] = (gameBlockAvailableWidth // 2)

    for block in range((gameBlockAvailableWidth)):
        currentChunk = game.data[int(game.charPosition[0] + block)]
        height = currentChunk['height']
        blockImage = pygame.image.load('./utils/images/blocks/grassy_dirt_block_1.png')
        blockImage = pygame.transform.scale(blockImage, (game.blockWidthPixels, game.blockWidthPixels))
        blockY = (height * game.blockWidthPixels) + ((game.screen.get_size()[1] // 2) + centerHeight)
        game.screen.blit(blockImage, ((block * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), blockY))
        blockImageBelow = pygame.image.load('./utils/images/blocks/plain_dirt_block_1.png')
        blockImageBelow = pygame.transform.scale(blockImage, (game.blockWidthPixels, game.blockWidthPixels))
        belowChunk = 0
        if (currentChunk['foliage'].split(':')[0] == 'tree'):
            treeStumpImage = pygame.image.load('./utils/images/blocks/tree_stump_block_1.png')
            treeStumpImage = pygame.transform.scale(treeStumpImage, (game.blockWidthPixels, game.blockWidthPixels))
            for stump in range(currentChunk['treeHeight']):
                game.screen.blit(treeStumpImage, ((block * game.blockWidthPixels) + (float('0.' + str(float(game.charPosition[0])).split('.')[1])), (blockY - (game.blockWidthPixels * (stump + 1)))))
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

    characterSprite = pygame.image.load('./utils/images/sprites/character_still_1.png')
    aspectRatio = characterSprite.get_size()[1] / characterSprite.get_size()[0]
    characterSprite = pygame.transform.scale(characterSprite, (game.blockWidthPixels, int(game.blockWidthPixels * aspectRatio)))
    spriteHeight = game.data[int(game.charPosition[0] + (game.screen.get_size()[0] // 2) // game.blockWidthPixels)]['height'] * game.blockWidthPixels
    spriteHeight += game.screen.get_size()[1] // 2
    spriteHeight -= characterSprite.get_size()[1]
    spriteHeight -= game.charPosition[1]
    spriteHeight += centerHeight
    game.screen.blit(characterSprite, ((game.screen.get_size()[0] // 2), spriteHeight))

    if (game.debugMode):
        runCountText = game.text('./utils/fonts/arial.ttf', 20, str(game.runs) + ' - total runs', (0, 0, 0))
        fpsCountText = game.text('./utils/fonts/arial.ttf', 20, str(game.fps) + ' - current fps', (0, 0, 0))
        playerPos = game.text('./utils/fonts/arial.ttf', 20, 'X:{}   Y:{}   BW:{}'.format(int(game.charPosition[0]), int(game.charPosition[1]), int(game.blockWidthPixels)), (0, 0, 0))
        game.screen.blit(runCountText, (0, 0))
        game.screen.blit(fpsCountText, (0, (runCountText.get_size()[1])))
        game.screen.blit(playerPos, (0, (fpsCountText.get_size()[1] + runCountText.get_size()[1])))
    if (game.charPosition[1] > 0):
        game.charPosition[1] -= 5
    pygame.display.update()
    game.clock.tick(game.tickFps)
    game.runs += 1
    current = time.time()
    game.fps = int(1 / (current - last))

pygame.quit()
exit()
