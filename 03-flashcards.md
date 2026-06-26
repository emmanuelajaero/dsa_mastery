# 03 — Flashcards & Spaced Repetition

> Don't re-read passively — **test yourself**. Cover the answer, say it out loud,
> then check. Use the schedule at the bottom so it sticks long-term.

**How to drill:** read the **Q**, answer from memory, reveal the **A**. If you miss
one, mark it and review it sooner.

---

## Deck A — Trigger → Pattern (recognition)

| Q (the clue in a problem) | A (pattern) |
|---|---|
| "Many range-sum queries on a fixed array" | Prefix Sum |
| "Sorted array, find a pair summing to X" | Two Pointers |
| "Longest/shortest **contiguous** subarray/substring" | Sliding Window |
| "Does a linked list have a cycle? / find the middle" | Fast & Slow Pointers |
| "Reverse a list (or sublist) with O(1) space" | LinkedList In-place Reversal |
| "Next greater / next smaller element" | Monotonic Stack |
| "K largest / K most frequent" | Top K (Heap) |
| "Merge / schedule overlapping ranges" | Overlapping Intervals |
| "Sorted or rotated array, find target/boundary" | Modified Binary Search |
| "Sorted output from a BST" | Inorder Tree Traversal |
| "Enumerate all paths / detect cycle / topo sort" | DFS |
| "Fewest steps / shortest path, unweighted" | BFS |
| "Islands / flood fill / regions on a grid" | Matrix Traversal |
| "ALL permutations / combinations / subsets" | Backtracking |
| "Best/min/max/number-of-ways over choices, overlapping subproblems" | Dynamic Programming |
| "Shortest path in a weighted graph, non-negative edges" | Dijkstra's Algorithm |
| "Are these nodes connected? / merge groups / detect cycle in undirected" | Union-Find (DSU) |
| "Count BSTs / balanced parenthesizations" | Catalan Numbers (DP) |
| "Best split of an interval, combine halves" | Matrix Chain / Interval DP |
| "Count valid numbers up to N with a digit property" | Digit DP |
| "Small n (≤20), track which items chosen" | Bitmask DP |
| "Expected value / survival probability over steps" | Probability DP |
| "Buy/sell/hold/rest — a few discrete modes" | State Machine DP |

---

## Deck B — Pattern → Complexity (cold recall)

| Q (pattern) | A (time / space) |
|---|---|
| Prefix Sum | build `O(n)` / query `O(1)`, space `O(n)` |
| Two Pointers | `O(n)` time `O(1)` space (`+O(n log n)` if sorting) |
| Sliding Window | `O(n)` / `O(1)`–`O(k)` |
| Fast & Slow | `O(n)` / `O(1)` |
| LL Reversal | `O(n)` / `O(1)` |
| Monotonic Stack | `O(n)` / `O(n)` |
| Top K (Heap) | `O(n log k)` / `O(k)` |
| Overlapping Intervals | `O(n log n)` / `O(n)` |
| Binary Search | `O(log n)` / `O(1)` |
| Tree Traversal | `O(n)` / `O(h)` |
| DFS / BFS | `O(V+E)` / `O(V)` |
| Matrix Traversal | `O(m·n)` / `O(m·n)` |
| Backtracking | `O(branch^depth)` / `O(depth)` |
| 0/1 & Unbounded Knapsack | `O(n·W)` / `O(W)` |
| LCS / Edit Distance | `O(n·m)` / `O(n·m)`→`O(m)` |
| LIS (optimal) | `O(n log n)` / `O(n)` |
| Interval DP (Matrix Chain) | `O(n^3)` / `O(n^2)` |
| Bitmask DP | `O(2^n·n)` / `O(2^n)` |
| Dijkstra | `O((V+E) log V)` / `O(V+E)` |
| Union-Find (DSU) | `O(α(n))` amortized per op / `O(n)` |

---

## Deck C — DP recurrences (the one line that matters)

| Q (pattern) | A (recurrence) |
|---|---|
| Fibonacci / stairs | `dp[i] = dp[i-1] + dp[i-2]` |
| Kadane | `cur = max(x, cur + x); best = max(best, cur)` |
| 0/1 Knapsack | `dp[w] = max(dp[w], dp[w-wt] + val)` — capacity **downward** |
| Unbounded Knapsack | same, capacity **upward** |
| LCS | match: `dp[i-1][j-1]+1`; else `max(dp[i-1][j], dp[i][j-1])` |
| Edit Distance | match: `dp[i-1][j-1]`; else `1 + min(3 neighbors)` |
| Palindromic Subseq | ends equal: `dp[i+1][j-1]+2`; else `max(dp[i+1][j], dp[i][j-1])` |
| Subset Sum | `dp[s] = dp[s] or dp[s-x]` |
| Count Ways (decode) | `dp[i] += dp[i-1] (1-digit) + dp[i-2] (2-digit)` |
| Catalan / unique BST | `dp[n] = Σ dp[i-1]·dp[n-i]` |
| Matrix Chain / interval | `dp[i][j] = min over k (dp[i][k]+dp[k+1][j]+cost)` |
| Grid path | `dp[r][c] = grid[r][c] + min/sum(dp[r-1][c], dp[r][c-1])` |
| Tree DP (rob) | `rob = val + skip(children); skip = max(child states)` |
| State machine (cooldown) | `sold=hold+p; hold=max(hold,rest-p); rest=max(rest,prev_sold)` |
| Catalan / unique BST (DP 11) | `dp[n] = Σ dp[i-1]·dp[n-i]` for each root |
| Matrix Chain / interval (DP 12) | `dp[i][j] = min over k (dp[i][k]+dp[k+1][j]+cost(i,k,j))` |
| Count Distinct Ways (DP 13) | `dp[i] += dp[i-1] (valid 1-digit) + dp[i-2] (valid 2-digit)` |
| Grid DP (DP 14) | `dp[r][c] = grid[r][c] + min(dp[r-1][c], dp[r][c-1])` |
| Tree DP (DP 15) | `rob = val + skip(children); skip = max(child_rob, child_skip)` |
| Graph DP / Bellman-Ford (DP 16) | `dist[v] = min(dist[v], snapshot[u] + w)` per round |
| Digit DP (DP 17) | `dp(pos, mask, tight, started)` → sum over valid digits `0..hi` |
| Bitmask DP / TSP (DP 18) | `dp[mask|bit][j] = min(dp[mask][i] + dist[i][j])` |
| Probability DP (DP 19) | `dp[k][r][c] = Σ dp[k-1][src_r][src_c] / num_moves` |
| State Machine DP (DP 20) | `sold=hold+p; hold=max(hold,rest-p); rest=max(rest,prev_sold)` |

---

## Deck D — Concept checks (say the full answer)

1. **Q:** Why iterate capacity *downward* in 0/1 knapsack but *upward* in unbounded?
   **A:** Downward prevents reusing the same item in one pass (each item once);
   upward intentionally allows reuse (infinite supply).

2. **Q:** Why does BFS give the shortest path in an *unweighted* graph but not weighted?
   **A:** BFS expands by edge-count layers, so the first time you reach a node is via
   the fewest edges. With weights, fewest edges ≠ least cost → use Dijkstra.

3. **Q:** What two properties must a problem have for DP to apply?
   **A:** Optimal substructure (optimal answer built from optimal sub-answers) and
   overlapping subproblems (same subproblems recur).

4. **Q:** Memoization vs tabulation?
   **A:** Memoization = top-down recursion + cache (computes only needed states).
   Tabulation = bottom-up loops filling a table (no recursion stack, easy to space-optimize).

5. **Q:** Min-heap or max-heap for the *K largest* elements, and what size?
   **A:** A **min-heap of size K**; its root is the smallest of the current winners,
   so a larger incoming value evicts it.

6. **Q:** How do you find a cycle's *entry* node with fast/slow pointers?
   **A:** After they collide, reset one pointer to the head; advance both one step at
   a time — they meet at the cycle entrance.

7. **Q:** What does an *inorder* traversal of a BST produce?
   **A:** Values in ascending sorted order.

8. **Q:** When is `O(n log n)` LIS used over the `O(n^2)` DP?
   **A:** When you only need the *length*; patience-sorting with binary search on
   `tails` gives `O(n log n)`. The `O(n^2)` DP is simpler when you must reconstruct it.

9. **Q:** Why a dummy head node when reversing a sublist of a linked list?
   **A:** It removes special-casing for reversing from position 1 (no null `prev`).

10. **Q:** What's the state in Digit DP and why "tight"?
    **A:** `(position, tight, ...)`. `tight` tracks whether the prefix still equals the
    bound's prefix, which caps the next digit's max value.

11. **Q:** Why does Dijkstra fail with negative edges?
    **A:** Dijkstra greedily locks the shortest distance when a node is popped. A
    later negative edge could have offered a shorter path, but the node is already
    finalized. Use Bellman-Ford for negative edges.

12. **Q:** What does "path compression" do in Union-Find?
    **A:** During `find(x)`, it re-points every node on the path directly to the root,
    flattening the tree. This makes future `find` calls near `O(1)` (amortized `O(α(n))`).

13. **Q:** In Bitmask DP, why is `n` limited to about 20?
    **A:** The state space is `2^n`. At `n=20`, that's ~1 million states — feasible.
    At `n=25` it's 33 million, and at `n=30` it's over 1 billion — too much memory and time.

14. **Q:** How do you count *ways* (combinatorial) vs find *best* (optimization) in DP?
    **A:** Ways: use `+=` (sum contributions). Best: use `max()` or `min()`. Same
    recurrence structure, different aggregation operator.

---

## Spaced-repetition schedule

The forgetting curve is steep — review at expanding intervals to flatten it.

```
Learn it ──▶ Day 1 ──▶ Day 3 ──▶ Day 7 ──▶ Day 16 ──▶ Day 35
            (recall)   (recall)  (recall)  (recall)   (mastered)

retention
 100% |●
      |  \        ● review resets the curve higher each time
      |   \●_     ●__
      |      \__     \___        ●____
      |         \________\___________\________
      +---------------------------------------------▶ time
```

| Session | Do this |
|---|---|
| Day 0 | Read the pattern, run the code, solve 1 problem. |
| Day 1 | Deck A + B from memory. Re-solve that problem from a blank file. |
| Day 3 | Deck C (recurrences). Solve a *second* problem for the pattern. |
| Day 7 | Deck D concept checks. Mixed review (random pattern, name it cold). |
| Day 16 | Full timed mock: 1 easy + 1 medium across patterns. |
| Day 35 | Final pass; anything you miss goes back to a Day-1 cycle. |

> **Active recall beats re-reading.** If you can write each template from an empty
> editor and state its complexity without looking, you've got it.
