# 00 — Complexity Foundations & Data-Structure Cheat Sheet

> Before patterns, you need a feel for **cost**. This file gives you the Big-O
> ladder, how to *recognize* each complexity, and the cost of every operation on
> the data structures you'll use. Memorize the two big tables at the end.

---

## 1. What Big-O actually measures

Big-O describes **how the running time (or memory) grows as the input `n` grows** —
ignoring constants and small terms. It answers: *"If I make the input 10× bigger,
what happens?"*

```
n -> 10n means...
O(1)        : no change            (1  -> 1)
O(log n)    : +a constant          (1  -> ~3.3 steps more)
O(n)        : 10x slower           (1  -> 10)
O(n log n)  : ~13x slower          (1  -> ~13)
O(n^2)      : 100x slower          (1  -> 100)
O(2^n)      : astronomically worse (don't)
```

**Mnemonic for the ladder** — *"Constant Logs Run Now, Linearithmic Squares Explode Fast":*

```
O(1)  <  O(log n)  <  O(sqrt n)  <  O(n)  <  O(n log n)  <  O(n^2)  <  O(n^3)  <  O(2^n)  <  O(n!)
```

**8-second memory video** — copy into your AI video generator:
```prompt
8-second cinematic camera tilt up a giant glowing ladder/staircase. Each rung is labeled in order: O(1), O(log n), O(sqrt n), O(n), O(n log n), O(n^2), O(n^3), O(2^n), O(n!). The lower rungs glow cool calm green and are gently spaced; as the camera climbs, the rungs get steeper, closer, and turn fiery orange-red, the top ones erupting in flames as costs explode. Bold text overlay: "Constant Logs Run Now, Linearithmic Squares Explode Fast." Epic, vertical, dramatic.
```

---

## 2. How to RECOGNIZE each complexity (pattern-matching cheat)

| You see... | It's usually... | Why |
|------------|-----------------|-----|
| Direct index, hash lookup, math formula | `O(1)` | One step, no loop |
| Halving the search space each step | `O(log n)` | Binary search, balanced BST |
| One loop over the input | `O(n)` | Visit each element once |
| Loop + sort, or heap of size n, or divide & conquer that merges | `O(n log n)` | Sort/heapify dominates |
| Two nested loops over the input | `O(n^2)` | Every pair |
| Three nested loops | `O(n^3)` | Every triple (e.g. interval DP) |
| Trying include/exclude for each of n items | `O(2^n)` | Subsets |
| Generating all orderings | `O(n!)` | Permutations |
| Recursion tree with branching `b`, depth `d` | `O(b^d)` | Backtracking |

> **Space tip:** recursion costs `O(depth)` stack space even if you allocate nothing,
> because each call frame stays on the stack until it returns.

---

## 3. Amortized vs worst case (one gotcha)

- **`list.append`** in Python is *amortized* `O(1)` — occasionally it resizes
  (`O(n)`), but averaged over many appends it's constant.
- **`dict`/`set` lookup** is *average* `O(1)`, *worst* `O(n)` under adversarial hash
  collisions (rare in interviews — say "O(1) average").

---

## 4. Visualizing growth (relative steps for n = 100)

```
O(1)        | ▏ 1
O(log n)    | ▏ ~7
O(sqrt n)   | ▎ 10
O(n)        | ███ 100
O(n log n)  | ██████ ~664
O(n^2)      | ████████████████████ 10,000
O(2^n)      | (1.27e30 — off the chart)
```

---

## 5. DATA-STRUCTURE OPERATION COSTS — memorize this

| Structure | Access | Search | Insert | Delete | Notes |
|-----------|:------:|:------:|:------:|:------:|-------|
| **Array / Python `list`** | `O(1)` | `O(n)` | `O(n)`* | `O(n)`* | *`append`/`pop` end = `O(1)` amortized |
| **Hash map (`dict`) / set** | — | `O(1)` avg | `O(1)` avg | `O(1)` avg | unordered; worst `O(n)` |
| **Stack (`list`/`deque`)** | `O(1)` top | `O(n)` | `O(1)` push | `O(1)` pop | LIFO |
| **Queue (`deque`)** | `O(1)` ends | `O(n)` | `O(1)` | `O(1)` | FIFO; `popleft` is `O(1)` |
| **Singly Linked List** | `O(n)` | `O(n)` | `O(1)`† | `O(1)`† | †given the node/prev pointer |
| **Balanced BST** | `O(log n)` | `O(log n)` | `O(log n)` | `O(log n)` | sorted order, ranges |
| **Binary Heap** | `O(1)` peek | `O(n)` | `O(log n)` push | `O(log n)` pop | min/max at root |
| **Trie** | `O(L)` | `O(L)` | `O(L)` | `O(L)` | `L` = key length |

> **Python note:** there is no built-in balanced BST. Use `heapq` for heaps,
> `collections.deque` for queues/stacks, `dict`/`set` for hashing, and
> `sortedcontainers.SortedList` when you truly need ordered `O(log n)` ops.

---

## 6. Common algorithm complexities — memorize this

| Algorithm / task | Time | Space |
|------------------|------|-------|
| Binary search | `O(log n)` | `O(1)` |
| Linear scan | `O(n)` | `O(1)` |
| Merge sort / Heap sort | `O(n log n)` | `O(n)` / `O(1)` |
| Quick sort | `O(n log n)` avg, `O(n^2)` worst | `O(log n)` |
| Python `sorted` / `.sort` (Timsort) | `O(n log n)` | `O(n)` |
| Heap build (`heapify`) | `O(n)` | `O(1)` |
| BFS / DFS on graph | `O(V + E)` | `O(V)` |
| Dijkstra (binary heap) | `O((V+E) log V)` | `O(V)` |
| Building all subsets | `O(2^n)` | `O(2^n)` |
| Building all permutations | `O(n!)` | `O(n)` recursion |

---

## 7. The two Python imports you'll use constantly

```python
import heapq                       # min-heap: heappush, heappop, heapify, nlargest, nsmallest
from collections import deque      # O(1) double-ended queue: append, appendleft, pop, popleft
from collections import defaultdict, Counter   # frequency maps without KeyErrors
```

Mini-reference:

```python
# Min-heap
h = []
heapq.heappush(h, 5)        # push
smallest = heapq.heappop(h) # pop smallest (O(log n))
heapq.heapify(arr)          # turn list into heap in O(n)

# Max-heap trick: push negatives
heapq.heappush(h, -value)
largest = -heapq.heappop(h)

# Deque (queue/stack)
dq = deque()
dq.append(x); dq.appendleft(x)
dq.pop();     dq.popleft()    # all O(1)

# Counter
freq = Counter("aabbbc")     # {'b':3,'a':2,'c':1}
freq.most_common(2)          # [('b',3),('a',2)]
```

Next: [`01-core-patterns.md`](./01-core-patterns.md).
