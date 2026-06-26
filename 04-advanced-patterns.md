# 04 — Advanced Patterns (Bonus)

> Two graph patterns that appear constantly in interviews but don't fit neatly
> into the core 15. Learn these **after** you're comfortable with BFS/DFS.

Every section follows the same shape as the core patterns:

> **Mnemonic** · **Picture** · **When to use** · **Template** · **Worked example** · **Complexity** · **⚠️ Watch out** · **Practice**

| Jump | |
|---|---|
| [A. Dijkstra's Algorithm](#a-dijkstras-algorithm) | [B. Union-Find (Disjoint Set Union)](#b-union-find-disjoint-set-union) |

---

## A. Dijkstra's Algorithm

> **Mnemonic:** *"Always pick the cheapest unvisited node — greedy BFS with a price tag."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second top-down animation of a glowing city road map. A delivery truck starts at a depot node; at every intersection it checks all outgoing roads' cost labels and always takes the cheapest unexplored route. Visited intersections turn green and lock their shortest cost. The truck reaches the destination via the proven cheapest path. Bold text overlay: "Always pick the cheapest unvisited node." Map glow, neon route lines, satisfying lock-in stamps.
```

### Picture
BFS uses a plain queue (FIFO) → shortest by *edge count*.
Dijkstra uses a **min-heap** (priority queue) → shortest by *total weight*.

```
Graph (weighted, non-negative):

  A --1--> B --2--> D
  |        ^        ^
  4        1        1
  |        |        |
  v        |        |
  C --2--> B'  E-1--+
        (B already visited, skip)

min-heap processes: (0,A) → (1,B) → (3,D) → (4,C) → ...
dist[A]=0, dist[B]=1, dist[D]=3, dist[C]=4
```

### When to use
- **Shortest path** in a **weighted graph with non-negative edges**.
- "Minimum cost / time / distance to reach a destination."
- Network delay, cheapest flights (without bounded stops — use Bellman-Ford for that).

### Template
```python
import heapq
from collections import defaultdict

def dijkstra(graph, src, n):
    """graph: adjacency list {u: [(v, weight), ...]}, n: number of nodes."""
    dist = [float("inf")] * n
    dist[src] = 0
    heap = [(0, src)]                    # (distance, node)
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                     # stale entry — skip
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist
```

### Worked example — Network Delay Time (LeetCode 743)
How long until all nodes receive a signal sent from node `k`?

```python
import heapq
from collections import defaultdict

def network_delay_time(times, n, k):
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))

    dist = {i: float("inf") for i in range(1, n + 1)}
    dist[k] = 0
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    mx = max(dist.values())
    return mx if mx < float("inf") else -1

# network_delay_time([[2,1,1],[2,3,1],[3,4,1]], 4, 2) -> 2
```

### Complexity
- **`O((V + E) log V)`** time (each edge relaxation = heap push), **`O(V + E)`** space.

### ⚠️ Watch out
- **Negative edges break Dijkstra.** If edges can be negative, use Bellman-Ford instead.
- **Stale heap entries:** always check `if d > dist[u]: continue` after popping — without this you process nodes multiple times and it's `O(V²)`.
- **Disconnected nodes:** check for `inf` in the result — not all nodes may be reachable.
- **1-indexed vs 0-indexed nodes:** LeetCode problems vary; match your `dist` array/dict to the problem.

### Practice
- Network Delay Time (743), Path with Minimum Effort (1631), Swim in Rising Water (778).

---

## B. Union-Find (Disjoint Set Union)

> **Mnemonic:** *"Every group has a boss; to merge, just change one boss."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second animation of colored team badges. Each person wears a badge pointing to their team captain (root). When two teams merge, one captain re-badges to point to the other — instantly both groups share the same root. Queries "are they on the same team?" trace badges to the root in near-constant time. Bold text overlay: "Every group has a boss; to merge, change one boss." Playful team colors, fast merges.
```

### Picture
```
Initially: each element is its own parent.
parent = [0, 1, 2, 3, 4]

union(0, 1):  parent[1] = 0        groups: {0,1} {2} {3} {4}
union(2, 3):  parent[3] = 2        groups: {0,1} {2,3} {4}
union(0, 3):  parent[2] = 0        groups: {0,1,2,3} {4}

find(3):  3 → 2 → 0 (root)
          path compression: parent[3] = 0   (shortcut for next time)
```

### When to use
- **"Are X and Y connected?"** — connected components, cycle detection in undirected graphs.
- **"Merge two groups"** — Kruskal's MST, accounts merge, equivalence classes.
- Any problem where you group elements dynamically and query membership.

### Template — with path compression + union by rank
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n              # track number of groups

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path compression (halving)
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                 # already same group
        # union by rank: attach smaller tree under bigger
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.components -= 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)
```

### Worked example — Redundant Connection (LeetCode 684)
Find the edge that, if removed, makes the graph a tree (= no cycle).

```python
def find_redundant_connection(edges):
    n = len(edges)
    uf = UnionFind(n + 1)               # nodes are 1-indexed
    for u, v in edges:
        if not uf.union(u, v):          # u and v already connected → this edge is redundant
            return [u, v]
    return []

# find_redundant_connection([[1,2],[1,3],[2,3]]) -> [2,3]
```

### Complexity
- **`O(α(n))`** amortized per `find`/`union` (α = inverse Ackermann, effectively constant), **`O(n)`** space.

### ⚠️ Watch out
- **Directed graphs:** standard Union-Find is for *undirected* connectivity. For directed graphs, use DFS / Tarjan's / Kahn's instead.
- **Forgetting path compression:** without it, `find` degrades to `O(n)` per call on a skewed tree.
- **1-indexed nodes:** many LeetCode problems use 1-indexed edges — size your `parent` array to `n+1`.
- **Counting components:** decrement `self.components` only when `union` actually merges two *different* groups.

### Practice
- Number of Connected Components (323), Redundant Connection (684), Accounts Merge (721), Kruskal's MST (1584 — Min Cost to Connect All Points).

---

## When Dijkstra vs BFS vs Bellman-Ford?

```
Unweighted graph?                   → BFS             O(V + E)
Weighted, non-negative edges?       → Dijkstra        O((V+E) log V)
Weighted, possible negative edges?  → Bellman-Ford    O(V · E)
Bounded hops/stops?                 → Bellman-Ford    O(K · E)
```

Continue to the progress tracker → [`05-progress-tracker.md`](./05-progress-tracker.md).
