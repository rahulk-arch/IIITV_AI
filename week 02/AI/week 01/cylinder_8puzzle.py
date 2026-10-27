from collections import deque

class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent

def get_successors(current):
    successors = []
    index = current.state.index(0)

    moves = [-1, 1, -3, 3]
    for pos in moves:
        new = index + pos
        if new < 0 or new > 8:
            continue
        new_state = current.state[:]
        new_state[index], new_state[new] = new_state[new], new_state[index]
        successors.append(Node(new_state, current))
    return successors

def agent(start_state, goal_state):
    queue = deque([(Node(start_state), [])])
    visited = set()

    while queue:
        (current, path) = queue.popleft()
        if current.state == goal_state:
            return path
        visited.add(tuple(current.state))
        for successor in get_successors(current):
            if tuple(successor.state) not in visited:
                queue.append((successor, path + [successor.state]))
    
    return None

start_state = [4,6,2,7,0,8,3,5,1]
goal_state = [1,2,3,4,5,6,7,8,0]

solution = agent(start_state, goal_state)
if solution:
    print("Solution found:")
    for step in solution:
        print(step)
else:
    print("No solution found.")