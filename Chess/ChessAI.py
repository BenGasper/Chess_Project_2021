import random
pieceScore = {"K": 0, "Q": 900, "R": 500, "N": 300, "B": 310, "P": 100}
CHECKMATE = 10000
STALEMATE = 0
DEPTH = 4

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]


def findBestMoveOG(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE-1
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)                 # Makes a player Move
        opponentsMoves = gs.get_valid_moves()   # Gets potential opponent moves
        if gs.stalemate:
            opponentMaxScore = STALEMATE        # If it is stalemate, opponent max score = 0
        elif gs.checkmate:
            opponentMaxScore = -CHECKMATE       # If it is checkmate, opponent max score = most negative
        else:
            opponentMaxScore = -CHECKMATE       # If it is not checkmate or stalemate, calculates opposing moves
            for opponentsMove in opponentsMoves:
                gs.makeMove(opponentsMove)      # Makes a potential move
                gs.get_valid_moves()            # Checks if it is checkmate or stalemate
                if gs.checkmate:                # If checkmate, score = Max value
                    score = CHECKMATE
                elif gs.stalemate:              # If stalemate, score = 0
                    score = STALEMATE
                else:                           # If neither, calculates score of board
                    score = -turnMultiplier * scoreBoard(gs)
                if score > opponentMaxScore:    # If score is greater than opponent max score, sets opp score.
                    opponentMaxScore = score
                gs.undo_move()
        if opponentMinMaxScore > opponentMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undo_move()
    return bestPlayerMove
"""
Helper method to make first recursive call
"""
def findBestMove(gs, validMoves):
    global nextMove, counter
    nextMove = None
    counter = 0
    random.shuffle(validMoves)
    # findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    #findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(counter)
    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.get_valid_moves()
            score = findMoveMinMax(gs, nextMoves, depth -1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undo_move()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.get_valid_moves()
            score = findMoveMinMax(gs, nextMoves, depth -1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undo_move()
        return minScore


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove, counter
    if depth == 0:
        counter += 1
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.get_valid_moves()
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undo_move()
    return maxScore


'''
Finds move using negamax algorithm with alpha beta pruning
'''
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter+=1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    # Move ordering - implement later
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.get_valid_moves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undo_move()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore
'''
A positive score is good for white, a negative score is good for black
'''
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE #blackwins
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    elif gs.drawRep:
        return STALEMATE
    score = 0
    for r in range(8):
        for c in range(8):
            square = gs.board[r][c]
            if square[0] == 'w':
                score += (pieceScore[square[1]] + piece_optimal_squares[square][r][c])
            elif square[0] == "b":
                score -= (pieceScore[square[1]] + piece_optimal_squares[square][r][c])
    return score


def position_value(piece, r, c):
    piece_map = piece_optimal_squares[piece]
    value = piece_map[r][c]
    return value
  
piece_optimal_squares = {"wN": [[-20, 0, 0, 0, 0, 0, 0, -20],
                                [0, 10, 10, 10, 10, 10, 10, 0],
                                [0, 10, 20, 20, 20, 20, 10, 0],
                                [0, 10, 20, 20, 20, 20, 10, 0],
                                [0, 10, 20, 20, 20, 20, 10, 0],
                                [0, 10, 20, 20, 20, 20, 10, 0],
                                [0, 10, 10, 10, 10, 10, 10, 0],
                                [-20, 0, 0, 0, 0, 0, 0, -20]],
                         "bN": [[-20, 0, 0, 0, 0, 0, 0, -20],
                                [0, 10, 10, 10, 10, 10, 10, 0],
                                [0, 10, 20, 20, 20, 20, 10, 0],
                                [0, 10, 20, 20, 20, 20, 10, 0],
                                [0, 10, 20, 20, 20, 20, 10, 0],
                                [0, 10, 20, 20, 20, 20, 10, 0],
                                [0, 10, 10, 10, 10, 10, 10, 0],
                                [-20, 0, 0, 0, 0, 0, 0, -20]],
                         "wK": [[0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, -20, -20, 0, 0, 0],
                                  [0, 0, 0, -20, -20, 0, 0, 0],
                                  [0, 0, 0, -10, -10, 0, 0, 0],
                                  [0, 0, 0, -10, -10, 0, 0, 0],
                                  [0, 0, 0, -10, -10, 0, 0, 0],
                                  [0, 0, 0, -10, -10, 0, 0, 0],
                                  [30, 30, 20, 0, 0, 0, 30, 30]],
                         "bK": [[30, 30, 20, 0, 0, 0, 30, 30],
                                [0, 0, 0, -10, -10, 0, 0, 0],
                                [0, 0, 0, -10, -10, 0, 0, 0],
                                [0, 0, 0, -10, -10, 0, 0, 0],
                                [0, 0, 0, -10, -10, 0, 0, 0],
                                [0, 0, 0, -20, -20, 0, 0, 0],
                                [0, 0, 0, -20, -20, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0]],
                         "wB": [[-20, -10, -10, -10, -10, -10, -10, -20],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 10, 0, 0, 0, 0, 10, 0],
                                [-20, -10, -10, -10, -10, -10, -10, -20]],
                         "bB": [[-20, -10, -10, -10, -10, -10, -10, -20],
                                [0, 10, 0, 0, 0, 0, 10, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0, 0],
                                [-20, -10, -10, -10, -10, -10, -10, -20]],
                         "wR": [[0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 20, 20, 20, 0, 0]],
                         "bR": [[0, 0, 0, 20, 20, 20, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0]],
                         "wQ": [[0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0]],
                         "bQ": [[0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0]],
                         "wP": [[900, 900, 900, 900, 900, 900, 900, 900],
                              [200, 200, 200, 200, 200, 200, 200, 200],
                              [20, 20, 20, 20, 20, 20, 20, 20],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 20, 25, 25, 20, 0, 10],
                              [0, 0, 10, 10, 10, 10, 0, 10],
                              [10, 10, 10, 0, 0, 10, 10, 10],
                              [0, 0, 0, 0, 0, 0, 0, 0]],
                         "bP": [[0, 0, 0, 0, 0, 0, 0, 0],
                              [10, 10, 10, 0, 0, 10, 10, 10],
                              [0, 0, 10, 10, 10, 10, 0, 10],
                              [0, 0, 20, 25, 25, 20, 0, 10],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [20, 20, 20, 20, 20, 20, 20, 20],
                              [200, 200, 200, 200, 200, 200, 200, 200],
                              [900, 900, 900, 900, 900, 900, 900, 900]]
                         }
