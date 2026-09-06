from collections import deque

def successor_state(state):
    state=list(state)
    successor=[]
    empty=state.index(-1)

    moves=[
        empty-1,
        empty+1,
        empty-2,
        empty+2,
    ]

    for pos in moves:
        if pos<0 or pos>=len(state):
            continue

        rabbit=state[pos]

        if rabbit==0 and pos<empty:
            if(state[pos+1]==-1 or state[pos+1]==1):
                new_state=state[:]
                new_state[empty]=0
                new_state[pos]=-1
                successor.append(tuple(new_state))

        if rabbit==1 and pos>empty:
            if(state[pos-1]==-1 or state[pos-1]==0):
                new_state=state[:]
                new_state[empty]=1
                new_state[pos]=-1
                successor.append(tuple(new_state))

    return successor

def agent(start_state, goal_state):
    queue=deque([(start_state, [])])
    visited=set()
    while queue:
        state, path=queue.pop()
        if state in visited:
            continue
        visited.add(state)
        path = path + [state]
        if state==goal_state:
            return path
        for successor in successor_state(state):
            queue.append((successor, path))
    return None

start_state=(0, 0, 0, -1, 1, 1, 1)
goal_state=(1, 1, 1, -1, 0, 0, 0)

solution= agent(start_state, goal_state)
if solution:
    print("Solution found:")
    for step in solution:
        print(step)

else:
    print("No solution found.")
