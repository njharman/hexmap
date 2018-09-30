import heapq

from hexmap import Hex


class Node(Hex):
    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.parent = None
        self.cost = 0

    def cost_to(self, dest):
        return self.distance_to(dest) * 10

    def blocked(self, frm):
        if self.x < 1 or self.y < 1 or self.x > 99 or self.y > 99:
            return True
        if self.x % 2 and self.y % 2:
            return True
        if self.x == 9 and self.y in range(10, 24):
            return True
        return False


def astar(current, end, maxsteps=1000):
    def retrace(c):
        path = [Hex(c), ]
        while c.parent is not None:
            c = c.parent
            path.append(Hex(c))
        path.reverse()
        return path

    heap = list()
    open = set()
    closed = set()
    open.add(current)
    heap.append((0, current))
    while open:
        current = heapq.heappop(heap)[1]
        if current == end:
            return retrace(current)
        open.remove(current)
        closed.add(current)
        for node in current.sixpack():
            if node in closed:
                continue
            if node.blocked(current):
                closed.add(node)
                continue
            new_cost = current.cost + current.cost_to(node)
            if node in open:
                if node.cost > new_cost:
                    node.cost = new_cost
                    node.parent = current
            else:
                open.add(node)
                node.cost = new_cost
                node.parent = current
                heapq.heappush(heap, (node.cost_to(end) + node.cost, node))
    return list()


funk = Node('0608'), Node('1112')
path = astar(*funk)[1:]
print('from %s -> %s' % funk)
for step in path:
    print(step)
