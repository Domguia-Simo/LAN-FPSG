import collections

class PathFinding:
    def __init__(self, game):
        self.game = game
        self.map = game.map.mini_map
        self.ways = [-1, 0], [0, -1], [1, 0], [0, 1], [-1, -1], [1, -1], [1, 1], [-1, 1]
        self.graph = {}
        self.build_graph()

    def get_path(self, start, goal):
        try:
            self.visited = self.bfs(start, goal, self.graph)
            path = [goal]
            step = self.visited.get(goal, start)

            while step and step != start:
                path.append(step)
                step = self.visited[step]
            path.append(start)
            path.reverse()
            return path[1] if len(path) > 1 else start
        except KeyError:
            # If path cannot be found, return the start position
            return start

    def bfs(self, start, goal, graph):
        queue = collections.deque([start])
        visited = {start: None}

        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break

            # Get next nodes with error handling
            next_nodes = graph.get(cur_node, [])
            for next_node in next_nodes:
                if next_node not in visited:
                    queue.append(next_node)
                    visited[next_node] = cur_node
        return visited

    def build_graph(self):
        # Empty the graph first
        self.graph = {}
        
        # Get dimensions of the map
        height = len(self.map)
        width = len(self.map[0]) if height > 0 else 0

        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if not col:  # if this is a walkable space
                    self.graph[(x, y)] = []
                    for dx, dy in self.ways:
                        next_x, next_y = x + dx, y + dy
                        # Check boundaries and walkable space
                        if (0 <= next_x < width and 
                            0 <= next_y < height and 
                            not self.map[next_y][next_x]):
                            self.graph[(x, y)].append((next_x, next_y))

    def get_next_nodes(self, x, y):
        return self.graph.get((x, y), [])