"""
Main driver file. Responsible for handling user input and displaying the current GameState object.
"""
import pygame as p
from Chess import ChessEngine, ChessAI

BOARD_WIDTH = BOARD_HEIGHT = 768
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = (BOARD_WIDTH) // DIMENSION
MAX_FPS = 15
IMAGES = {}

"""
Initialize a global dictionary of images. This will be called exactly once in the main
"""
def load_images():
    pieces = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


"""
Main driver for our program. Handles user input and uploading graphics
"""
def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("gray"))
    moveLogFont = p.font.SysFont("Calibri", 12, True, False)
    gs = ChessEngine.GameState()
    validMoves = gs.get_valid_moves()
    moveMade = False #flag variable for when a move is made
    load_images()
    running = True
    sqSelected = ()  # no square is selected, keep track of last click
    playerClicks = []  # Keep track of player clicks (Two tuples: [(5,3), (2,6)]
    gameOver = False

    # Set player vs computer
    playerOne = True  # If a human is playing white, this will be True, if AI is white, false
    playerTwo = False  # Same as above for black

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False


            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() # x and y location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col) or col > 7: #User clicks same sq or clicks move log
                        sqSelected = () #deselect
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                gs.addBoardPosition()  # Adds board position to past positions and checks for repeats
                                gs.currentPosition = gs.generateFENNotation()  # Updates current position
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

                # Key Handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    # Remove Current Board position from log
                    if gs.currentPosition in gs.repPositions:
                        gs.repPositions.pop()
                    else:
                        gs.boardPositions.pop()
                    gs.currentPosition = gs.generateFENNotation()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r: # reset the board when r is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.get_valid_moves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False


        #AI move finder logic
        if not gameOver and not humanTurn:
            AIMove = ChessAI.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = ChessAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.get_valid_moves()
            moveMade = False


        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkmate or gs.stalemate or gs.drawRep:
            gameOver = True
            if gs.checkmate:
                if gs.whiteToMove:
                    text = "Black Wins by Checkmate!"
                else:
                    text = "White Wins by Checkmate!"
            elif gs.stalemate:
                text = "Stalemate"
            else:
                text = "Draw by Repetition"
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()



"""
Responsible for all graphics with current gamestate
"""
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen) # draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of board
    drawMoveLog(screen, gs, moveLogFont)

"""
Draw squares on board (Top left is light)
"""
def drawBoard(screen):
    colors = [p.Color(238, 238, 210), p.Color(118, 150, 86)]  # Light Color / Dark Color
    ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]
    files = ["a", "b", "c", "d", "e", "f", "g", "h"]
    font = p.font.SysFont("Calibri", 20, True, False)
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    for r in range(DIMENSION):
        # Write letters and numbers of the rank and file
        textObject = font.render(files[r], 0, p.Color("Black"))
        textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(.88 * SQ_SIZE + (r * SQ_SIZE), BOARD_HEIGHT - 20)
        screen.blit(textObject, textLocation)
        textObject = font.render(ranks[r], 0, p.Color("Black"))
        textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(4, .1 * SQ_SIZE + (r * SQ_SIZE))
        screen.blit(textObject, textLocation)


"""
Highlight square selected and moves for piece selected
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):  # square selected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(50)  # Transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))



"""
Draw pieces using current gamestate
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Draws and updates move log
"""
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("gray"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = moveLog
    textWidth = 5
    textHeight = 5
    for i in range(len(moveTexts)):
        text = moveTexts[i].get_chess_notation()
        textObject = font.render(text, True, p.Color("black"))
        textLocation = moveLogRect.move(textWidth, textHeight)
        textWidth = textWidth + 35
        if textWidth > 200:
            textWidth = 5
            textHeight += 20
        screen.blit(textObject, textLocation)

"""
Animates the move that is made
"""
def animateMove(move, screen, board, clock):
    colors = [p.Color(238, 238, 210), p.Color(118, 150, 86)]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 2  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount+1):
        r, c = ((move.startRow + dR*frame/frameCount, move.startCol + dC * frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # Draw captured piece onto square
        if move.pieceCaptured != "--":
            if move.isEnPassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceMoved[0] == "w" else (move.endRow - 1)
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        if move.pieceMoved != "--":
            screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


"""
Takes in a given endgame text and displays it on the screen
"""
def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitica", 32, True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move((2, 2)))


if __name__ == "__main__":
    main()
