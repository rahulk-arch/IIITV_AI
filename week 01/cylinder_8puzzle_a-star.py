from collections import deque
import heapq

class Node:
    def __init__(self, state, parent=None, g=0, h=0):
        self.state = state
        self.parent = parent
        self.g = g
        self.h = h
        self.f = g+h
    def __lt__(self, other):
        return self.f<other.f

def heuristic(state, goal_state):
    h=0
    for i in range(9):
        if state[i]!=0:
            goal_index=goal_state.index(state[i])
            h+=abs(i//3-goal_index//3)+abs(i%3-goal_index%3)
    return h

def successor(node):
    successor=[]
    index=node.state.index(0)
    row=index//3
    column=index%3

    if row==0:
        moves=[3]
    if row==1:
        moves=[-3,3]
    if row==2:
        moves=[-3]

    if column==0:
        moves+=[1,2]
    if column==1:
        moves+=[-1,1]
    if column==2:
        moves+=[-1,-2]

    for move in moves:
        valid_index=index+move
        if valid_index<0 or valid_index>8:
            continue
        new_state=list(node.state)
        new_state[index], new_state[valid_index]= new_state[valid_index], new_state[index]
        successor.append(Node(new_state, node, node.g+1, heuristic(new_state, goal_state)))
    return successor

def agent(start_state, goal_state):
    start_node=Node(start_state)
    goal_node=Node(goal_state)
    frontier=[]
    heapq.heappush(frontier, (start_node.f, start_node))
    visited=set()
    while frontier:
        _, node=heapq.heappop(frontier)
        if tuple(node.state) in visited:
            continue
        visited.add(tuple(node.state))

        if node.state==goal_state:
            path=[]

            while node:
                path.append(node.state)
                node=node.parent
            return path[::-1]
        for suss in successor(node):
            heapq.heappush(frontier, (suss.f, suss))
    return None

start_state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
goal_state = [7, 2, 3, 4, 5, 0, 1, 8, 6]

solution=agent(start_state, goal_state)
if solution:
    print("solution found")
    for sol in solution:
        print(sol)
else:
    print("No solution found")