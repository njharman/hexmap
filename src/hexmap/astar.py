import heapq

from hexmap import Hex


class Node(Hex):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = None
        self.cost = 0

    def cost_to(self, dest):
        return self.distance_to(dest) * 10

    def blocked(self, frm):
        if self.x < 1 or self.y < 1 or self.x > 99 or self.y > 99:
            return True
        if self.x % 2 and self.y % 2:
            return True
        return self.x == 9 and self.y in range(10, 24)


def astar(current, end, maxsteps=1000):
    def retrace(c):
        path = [Hex(c), ]
        while c.parent is not None:
            c = c.parent
            path.append(Hex(c))
        path.reverse()
        return path

    heap = list()
    open_set = set()
    closed = set()
    open_set.add(current)
    heap.append((0, current))
    while open_set:
        current = heapq.heappop(heap)[1]
        if current == end:
            return retrace(current)
        open_set.remove(current)
        closed.add(current)
        for node in current.sixpack():
            if node in closed:
                continue
            if node.blocked(current):
                closed.add(node)
                continue
            new_cost = current.cost + current.cost_to(node)
            if node in open_set:
                if node.cost > new_cost:
                    node.cost = new_cost
                    node.parent = current
            else:
                open_set.add(node)
                node.cost = new_cost
                node.parent = current
                heapq.heappush(heap, (node.cost_to(end) + node.cost, node))
    return list()


if __name__ == '__main__':
    funk = Node('0608'), Node('1112')
    path = astar(*funk)[1:]
    print('from {} -> {}'.format(*funk))
    for step in path:
        print(step)
