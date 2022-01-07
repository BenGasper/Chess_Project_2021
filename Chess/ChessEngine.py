"""
This class is responsible for storing all information about the current state of a chess game and will be responsible for determining valid moves at current state.
It will also keep a move log.
"""


def in_range(r, c):
    return 7 >= r >= 0 and 7 >= c >= 0


class GameState():
    def __init__(self):
        # board is an 8x8 2d list that has each space represented by 2 characters
        # first character represents color of piece "b" "w"
        # second character determines type "P", "R", "N", "B", "K", "Q"
        # a blank space is represented by "--"
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        # self.board = [
        #     ["bR", "bN", "bB", "bQ", "--", "bK", "--", "bR"],
        #     ["bP", "bP", "--", "wP", "bB", "bP", "bP", "bP"],
        #     ["--", "--", "bP", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "wB", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["wP", "wP", "wP", "--", "wN", "bN", "wP", "wP"],
        #     ["wR", "wN", "wB", "wQ", "wK", "--", "--", "wR"]]
        self.moveFunctions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                              "K": self.get_king_moves, 'B': self.get_bishop_moves, 'Q': self.get_queen_moves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enPassantPossible = ()
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.wqs,
                                             self.currentCastlingRight.bks, self.currentCastlingRight.bqs,)]
        self.checkmate = False
        self.stalemate = False
        self.drawRep = False
        # Keep track of board positions that have happened using FEN notation
        self.currentPosition = self.generateFENNotation()
        self.boardPositions = []
        self.repPositions = []

    """
    Makes a given move on the board
    """
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move to undo or record
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        # Pawn Promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
            move.isPawnPromotion = False
        # en passant move
        if move.isEnPassantMove:
            move.pieceCaptured = self.board[move.startRow][move.endCol]
            self.board[move.startRow][move.endCol] = "--"

        # en passant available
        if move.pieceMoved[1] == "P" and abs(move.endRow-move.startRow) == 2:
            self.enPassantPossible = ((move.startRow+move.endRow)//2, move.startCol)
        else:
            self.enPassantPossible = ()

        # Castle Move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # Kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]  # Moves Rook
                self.board[move.endRow][move.endCol+1] = "--"
            else:  # Queenside castle move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # Moves Rook
                self.board[move.endRow][move.endCol - 2] = "--"

        # Update castling rights - whenever it is a rook or king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
        self.enPassantPossibleLog.append(self.enPassantPossible)

    """
    Undo last move
    """
    def undo_move(self):
        if len(self.moveLog) != 0:
            last_move = self.moveLog.pop()
            self.board[last_move.startRow][last_move.startCol] = last_move.pieceMoved
            self.board[last_move.endRow][last_move.endCol] = last_move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if last_move.pieceMoved == "wK":
                self.whiteKingLocation = (last_move.startRow, last_move.startCol)
            elif last_move.pieceMoved == "bK":
                self.blackKingLocation = (last_move.startRow, last_move.startCol)
            # undo en passant
            if last_move.isEnPassantMove:
                self.board[last_move.endRow][last_move.endCol] = "--"
                self.board[last_move.startRow][last_move.endCol] = last_move.pieceCaptured
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]
            self.checkmate = False
            self.stalemate = False
            self.drawRep = False
            # Undo castle rights
            self.castleRightsLog.pop() # get rid of new castle rights
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs) # set current rights to rights of previous move
            # Undo Castle Move
            if last_move.isCastleMove:
                if last_move.endCol-last_move.startCol == 2:
                    self.board[last_move.endRow][last_move.endCol+1] = self.board[last_move.endRow][last_move.endCol - 1]
                    self.board[last_move.endRow][last_move.endCol-1] = "--"
                else: # Queen side Castle
                    self.board[last_move.endRow][last_move.endCol-2] = self.board[last_move.endRow][last_move.endCol+1]
                    self.board[last_move.endRow][last_move.endCol + 1] = "--"


    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wqs = False
            self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bqs = False
            self.currentCastlingRight.bks = False
        elif move.pieceMoved[1] == "R":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False   # White Queenside rook moved
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False   # White Kingside rook moved
            elif move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False   # Black Queenside rook moved
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False   # Black Kingside rook moved
        if move.pieceCaptured[1] == "R":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False   # White Queenside rook moved
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False   # White Kingside rook moved
            elif move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False   # Black Queenside rook moved
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False   # Black Kingside rook moved
                
    """
    All moves considering checks
    """
    def get_valid_moves(self):
        moves = []
        captures = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:   # Only one check, block check, capture, or move king
                moves = self.get_all_possible_moves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.get_king_moves(kingRow, kingCol, moves, captures)
                moves = moves + captures
        else:
            moves = self.get_all_possible_moves()
        #for move in moves:
            #print(move)
        #print("----")
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        return moves


    """
    Gets all moves without considering checks
    """
    def get_all_possible_moves(self):
        moves = []
        captures = []
        for r in range(len(self.board)):    # rows
            for c in range(len(self.board[r])): # cols in row
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves, captures)  # calls appropriate piece move retrieval function
        moves = captures+moves
        return moves
    """
    Get all pawn moves for pawn at row, col and add them to list of moves.
    """
    def get_pawn_moves(self, r, c, moves, captures):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:  # White pawn moves
            if self.board[r-1][c] == "--":      # 1 square forward
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":       # 2 squares forward
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == "b":  # Capture to the left
                    if not piecePinned or pinDirection == (-1, -1):
                        captures.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enPassantPossible:
                    if not piecePinned or pinDirection == (-1, -1):
                        # Addresses the niche problem where pawn can't en passant because it would put King in check
                        if self.whiteKingLocation[0] == 3:
                            self.board[self.enPassantPossible[0]+1][self.enPassantPossible[1]] = "--"
                            incheck, pins, checks = self.checkForPinsAndChecks()
                            self.board[self.enPassantPossible[0]+1][self.enPassantPossible[1]] = "bP"
                            for i in range(len(pins) - 1, -1, -1):
                                if pins[i][0] == r and pins[i][1] == c:
                                    piecePinned = True
                            if not piecePinned:
                                captures.append(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
                        else:
                            captures.append(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == "b":  # capture to the right
                    if not piecePinned or pinDirection == (-1, 1):
                        captures.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enPassantPossible:
                    if not piecePinned or pinDirection == (-1, 1):
                        # Addresses the niche problem where pawn can't en passant because it would put King in check
                        if self.whiteKingLocation[0] == 3:
                            self.board[self.enPassantPossible[0] + 1][self.enPassantPossible[1]] = "--"
                            incheck, pins, checks = self.checkForPinsAndChecks()
                            self.board[self.enPassantPossible[0] + 1][self.enPassantPossible[1]] = "bP"
                            for i in range(len(pins) - 1, -1, -1):
                                if pins[i][0] == r and pins[i][1] == c:
                                    piecePinned = True
                            if not piecePinned:
                                captures.append(Move((r, c), (r - 1, c + 1), self.board, isEnPassantMove=True))
                        else: captures.append(Move((r, c), (r - 1, c + 1), self.board, isEnPassantMove=True))
        else:    # black pawn moves
            if self.board[r + 1][c] == "--":  # 1 square forward
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":     # 2 Squares forward
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == "w":  # Capture to the left
                    if not piecePinned or pinDirection == (1, -1):
                        captures.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enPassantPossible:
                    if not piecePinned or pinDirection == (1, -1):
                        # Addresses the niche problem where pawn can't en passant because it would put King in check
                        if self.blackKingLocation[0] == 4:
                            self.board[self.enPassantPossible[0] - 1][self.enPassantPossible[1]] = "--"
                            incheck, pins, checks = self.checkForPinsAndChecks()
                            self.board[self.enPassantPossible[0] - 1][self.enPassantPossible[1]] = "wP"
                            for i in range(len(pins) - 1, -1, -1):
                                if pins[i][0] == r and pins[i][1] == c:
                                    piecePinned = True
                            if not piecePinned:
                                captures.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove=True))
                        else:
                            captures.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove=True))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == "w":  # capture to the right
                    if not piecePinned or pinDirection == (1, 1):
                        captures.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enPassantPossible:
                    if not piecePinned or pinDirection == (1, 1):
                        # Addresses the niche problem where pawn can't en passant because it would put King in check
                        if self.blackKingLocation[0] == 4:
                            self.board[self.enPassantPossible[0] - 1][self.enPassantPossible[1]] = "--"
                            incheck, pins, checks = self.checkForPinsAndChecks()
                            self.board[self.enPassantPossible[0] - 1][self.enPassantPossible[1]] = "wP"
                            for i in range(len(pins) - 1, -1, -1):
                                if pins[i][0] == r and pins[i][1] == c:
                                    piecePinned = True
                            if not piecePinned:
                                captures.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove=True))
                        else:
                            captures.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove=True))
    """
    Uses piece_helper function to pass in the valid steps to calculate valid rook moves.
    """
    def get_rook_moves(self, r, c, moves, captures):
        steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        self.qbr_piece_helper(r, c, moves, steps, captures)

    def get_queen_moves(self, r, c, moves, captures):
        steps = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]
        self.qbr_piece_helper(r, c, moves, steps, captures)

    def get_bishop_moves(self, r, c, moves, captures):
        steps = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
        self.qbr_piece_helper(r, c, moves, steps, captures)

    def qbr_piece_helper(self, r, c, moves, steps, captures):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
        for x, y in steps:  # Increments in each direction on board until not blank.
            x_step = x
            y_step = y
            while in_range(r + x, c + y) and self.board[r + x][c + y] == "--":
                if (not piecePinned) or (pinDirection == (x, y) or pinDirection == (-x, -y)):
                    moves.append(Move((r, c), (r + x, c + y), self.board))
                    x += x_step
                    y += y_step
                else:
                    break
            if in_range(r + x, c + y) and self.board[r + x][c + y][0] == "b" and self.whiteToMove:
                captures.append(Move((r, c), (r + x, c + y), self.board))
            elif in_range(r + x, c + y) and self.board[r + x][c + y][0] == "w" and not self.whiteToMove:
                captures.append(Move((r, c), (r + x, c + y), self.board))

    def get_knight_moves(self, r, c, moves, captures):
        steps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
        if not piecePinned:
            for x, y in steps:  # Checks in each step direction one time.
                if in_range(r + x, c + y) and self.board[r + x][c + y] == "--":
                    moves.append(Move((r, c), (r + x, c + y), self.board))
                if in_range(r + x, c + y) and self.board[r + x][c + y][0] == "b" and self.whiteToMove:
                    captures.append(Move((r, c), (r + x, c + y), self.board))
                elif in_range(r + x, c + y) and self.board[r + x][c + y][0] == "w" and not self.whiteToMove:
                    captures.append(Move((r, c), (r + x, c + y), self.board))

    def get_king_moves(self, r, c, moves, captures):
        steps = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]
        allyColor = self.board[r][c][0]
        for x, y in steps:  # Checks in each step direction one time.

            if in_range(r + x, c + y) and self.board[r + x][c + y][0] != allyColor:
                if not self.squareUnderAttack(r+x, c+y, allyColor):
                    moves.append(Move((r, c), (r + x, c + y), self.board))

        self.getCastleMoves(r, c, captures, allyColor)

    """
    Generate all valid castle moves for the king at (r,c) and add them to the list of moves
    """
    def getCastleMoves(self, r, c, moves, allyColor):
        if self.inCheck:  # can't castle in check
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves, allyColor)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves, allyColor)

    def getKingsideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1, allyColor) and not self.squareUnderAttack(r, c+2, allyColor):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.squareUnderAttack(r, c - 1, allyColor) and not self.squareUnderAttack(r, c - 2, allyColor):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def squareUnderAttack(self, r, c, allyColor):
        enemyColor = "b" if allyColor == "w" else "w"
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c +d[1] * i
                if in_range(endRow, endCol):
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities in this conditional
                        # 1) orthogonally away from king and piece is rook
                        # 2) Diagonally away from king and piece is bishop
                        # 3) 1 square diagonally and piece is pawn
                        # 4) Any direction and piece is queen
                        # 5) any direction 1 square and piece is king
                        if (0 <= j <= 3 and type == "R") or \
                        (4 <= j <=7 and type == "B") or \
                        (i == 1 and type == "P" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5)) or \
                        (type == "Q") or type == "K" and i == 1):
                            return True
                        else:  # no checks
                            break
                else:
                    break  # off board
        # Check for knight moves
        knightMoves = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, -2), (-1, 2))
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if in_range(endRow, endCol):
                endPiece = self.board[endRow][endCol]
                if (endPiece[0] == enemyColor and endPiece[1] == "N"): #enemy knight attacking king
                    return True
        return False


    """
    Checks outward from king's location to find checks and pins. Returns the list of checks and pinned pieces.
    """
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () # reset possible pins
            for i in range(1,8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if in_range(endRow, endCol):
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == (): # 1st allied piece could be pinned.
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:   # 2nd allied piece encountered, no pin.
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities in this conditional
                        # 1) orthogonally away from king and piece is rook
                        # 2) Diagonally away from king and piece is bishop
                        # 3) 1 square diagonally and piece is pawn
                        # 4) Any direction and piece is queen
                        # 5) any direction 1 square and piece is king
                        if (0 <= j <= 3 and type == "R") or \
                        (4 <= j <=7 and type == "B") or \
                        (i == 1 and type == "P" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5)) or \
                        (type == "Q") or type == "K" and i ==1):
                            if possiblePin == (): #its a check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: # piece blocking (pin)
                                pins.append(possiblePin)
                                break
                        else:  # no checks
                            break
                else:
                    break  # off board
        # Check for knight moves
        knightMoves = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, -2), (-1, 2))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if in_range(endRow, endCol):
                endPiece = self.board[endRow][endCol]
                if (endPiece[0] == enemyColor and endPiece[1] == "N"): #enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    '''
    Generates segment 1 of FEN notation for a board's position. Used to keep track of repetitions, not load game states.
    '''
    def generateFENNotation(self):
        newPosition = ""
        blanksquares = 0
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                if self.board[row][col] != "--":
                    if blanksquares > 0:
                        newPosition += str(blanksquares)
                        blanksquares = 0
                    pieceAdded = self.board[row][col][1] if self.board[row][col][0] == "w" else self.board[row][col][1].lower()
                    newPosition += pieceAdded
                else:
                    blanksquares += 1
            if blanksquares > 0:
                newPosition += str(blanksquares)
                blanksquares = 0
            if row < 7:
                newPosition += "/"
        self.currentPosition = newPosition
        return newPosition
    def addBoardPosition(self):
        if self.currentPosition in self.boardPositions:
            if self.currentPosition in self.repPositions:
                self.drawRep = True
            else:
                self.repPositions.append(self.currentPosition)
        else:
            self.boardPositions.append(self.currentPosition)
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"h": 7, "g": 6, "f": 5, "e": 4,
                   "d": 3, "c": 2, "b": 1, "a": 0}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove=False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

        # Piece Promotion
        self.isPawnPromotion = self.pieceMoved[1] == "P" and (self.endRow == 7 or self.endRow == 0)
        # en passant
        self.isEnPassantMove = isEnPassantMove
        #Castle move
        self.isCastleMove = isCastleMove


    """
    Overriding equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __str__(self):
        return self.get_chess_notation()