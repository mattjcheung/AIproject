# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers

from .core import CellState, Coord, Direction, MoveAction
from .utils import render_board
from collections import deque

# GLOBAL VARIABLES
BOARD_N = 8

DIRECTIONS = [Direction.Down, Direction.DownLeft, Direction.DownRight, 
             Direction.Left, Direction.Right]

"""
Description:
A BFS approach to finding the optimal path from row 0 -> row BOARD_N

Parameters:
    `board`: a dictionary representing the initial board state, mapping
    coordinates to "player colours". The keys are `Coord` instances,
    and the values are `CellState` instances which can be one of
    `CellState.RED`, `CellState.BLUE`, or `CellState.LILY_PAD`.
    
Returns:
    A list of "move actions" as MoveAction instances, or `None` if no
    solution is possible.
"""
def search(
    board: dict[Coord, CellState]
) -> list[MoveAction] | None:
    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, ansi=True))

    solution = bfs(board)

    return solution

"""
A BFS algorithm to find the fastest route for the red frog to cross the
board.
"""
def bfs(
    board: dict[Coord, CellState]
) -> list[MoveAction] | None:
    
    # get the starting position of the red frog
    startCoord = findFrog(board)

    # variables for path reconstruction
    directions = {}   # maps coord to direction of movement
    predecessor = {}  # maps coord to predecessor coord
    
    # variables for completing BFS
    visited = {startCoord}
    queue = deque([startCoord])

    # loop through all coordinates that can be reached
    while queue:
        coord = queue.popleft() 

        if coord.r == BOARD_N - 1:
            # we can assume this was the most efficient path due to BFS
            return reconstructPath(predecessor, directions, startCoord, coord)

        # moves is a list of all possible actions from a given coordinate
        moves = generatePaths(coord, board) 

        for newCoord, newPath in moves:
            if newCoord not in visited:
                # we have found a new coordinate to be explored
                predecessor[newCoord] = coord
                directions[newCoord] = newPath
                queue.append((newCoord))
                visited.add(newCoord)

    return    # if we reach this statement, it means no solution was found

"""
A function to find the starting position of the red frog, assuming there is 
always a red frog.
"""
def findFrog(
    board: dict[Coord, CellState]
) -> Coord:
    for coord, state in board.items():
        if state == CellState.RED:
            # operates on assumption that a red frog is always present
            return coord     
        
"""
A function to generate all the possible paths from a single coordinate.
"""
def generatePaths(
    redFrogCoord: Coord,
    board: dict[Coord, CellState]
) -> list[tuple[Coord, list[Direction]]]:
    
    # a list of lists containing a new coordinate reached and the path
    # it took to get there
    moves = []

    # find all single jump actions
    for direction in DIRECTIONS:
        if validJump(redFrogCoord, direction, board):
            newCoord = redFrogCoord + direction
            moves.append((newCoord, [direction]))

    # find all leap actions    
    recursiveLeapFinder(redFrogCoord, board, {redFrogCoord}, [], moves)

    return moves

"""
A function to determine if the a single jump is permissable.
"""
def validJump(
    redFrogCoord: Coord, 
    direction: Direction, 
    board: dict[Coord, CellState]
) -> bool:
    cell = searchCoord(redFrogCoord, direction, board)

    # a jump is valid as long as there is an adjacent lily pad
    if cell == CellState.LILY_PAD:
        return True
    else:
        return False

"""
A function to determine if the a leap over a blue frog is 
permissable.
"""
def validLeap(
    redFrogCoord: Coord, 
    direction: Direction, 
    board: dict[Coord, CellState]
) -> bool:
    adjacentCell = searchCoord(redFrogCoord, direction, board)
    followingCell = searchCoord(redFrogCoord, direction * 2, board)

    # a leap if valid if it passes over a blue frog onto a lily pad
    if (adjacentCell == CellState.BLUE) and (followingCell == CellState.LILY_PAD):
        return True
    else:
        return False

"""
A Function to determine what lies in a given coordinate.
"""
def searchCoord(
    redFrogCoord: Coord, 
    direction: Direction,
    board: dict[Coord, CellState]
) -> CellState:
    
    try:
        redFrogCoord + direction
    except: 
        # addition of coord and direction is out of bounds
        return None

    # return entity at coordinate of interest
    return board.get(redFrogCoord + direction)

"""
A recursive function adds leaping actions to the list of moves 
from a given coordinate.
"""
def recursiveLeapFinder(
    redFrogCoord: Coord,
    board: dict[Coord, CellState],
    visited: set[Coord],
    currentPath: list[Direction],
    allMoves: list[tuple[Coord, list[Direction]]]
):
    # a flag for whether or not further leaping is successful
    movesFound = False

    # iterate through all the possible movements
    for direction in DIRECTIONS:
        if validLeap(redFrogCoord, direction, board):
            movesFound = True
            newCoord = redFrogCoord + (direction * 2)
            newPath = currentPath + [direction]

            # continue recursion as long as it is not repeating steps
            if newCoord not in visited:
                visited.add(newCoord)
                allMoves.append((newCoord, newPath))
                recursiveLeapFinder(newCoord, board, visited, newPath, allMoves)

    if not movesFound:
        allMoves.append((redFrogCoord, currentPath))
    
"""
A function to backtrack our solution to the starting coordinate.
"""
def reconstructPath(
    predecessor: dict[Coord, Coord],
    directions: dict[Coord, Direction],
    startCoord: Coord,
    endCoord: Coord,
) -> list[MoveAction]:
    
    path = []
    moves = []
    node = endCoord

    # iterate backwards through predecessor dict until startCoord
    while node != startCoord:
        path.append(node)
        moves.append(directions[node])
        node = predecessor[node]

    # reverse the lists as they are currently back-to-front
    path.reverse()
    moves.reverse()

    return [MoveAction(path, move) for path, move in zip(path, moves)] 

