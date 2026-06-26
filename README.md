# DSA Mastery — The Pattern Playbook

> A memorization-first study guide for the **15 core LeetCode patterns** and the
> **20 Dynamic Programming patterns**, in Python, with diagrams, mnemonics,
> complexity tables, and worked examples.
>
> Sources distilled and expanded from AlgoMaster's
> [15 LeetCode Patterns](https://blog.algomaster.io/p/15-leetcode-patterns) and
> [20 Patterns to Master Dynamic Programming](https://blog.algomaster.io/p/20-patterns-to-master-dynamic-programming).

---

## Read it as a website (recommended)

Open [`site/index.html`](./site/index.html) in your browser for a styled, navigable
version: syntax-highlighted Python, a chapter sidebar, an on-page table of contents,
copy-code buttons, and a light/dark toggle. It runs **fully offline**.

> Edited the Markdown? Regenerate the HTML with `python3 build_site.py`.

---

## How to use this folder

| File | What it gives you |
|------|-------------------|
| [`00-complexity-foundations.md`](./00-complexity-foundations.md) | Big-O intuition, the complexity ladder, and a data-structure cheat sheet. **Read this first.** |
| [`01-core-patterns.md`](./01-core-patterns.md) | The 15 core patterns (arrays → trees → graphs → backtracking). Each with diagram + code + complexity. |
| [`02-dynamic-programming.md`](./02-dynamic-programming.md) | The 20 DP patterns, easy → hard, each with the recurrence and Python. |
| [`03-flashcards.md`](./03-flashcards.md) | Rapid-recall Q&A + a spaced-repetition schedule. Use this to *test* yourself. |

**Recommended loop:** Read a pattern → cover the code and re-derive it → run it →
do 2 LeetCode problems → answer its flashcards 1 day, 3 days, and 7 days later.

---

## The Big Picture — one mental map

Almost every problem reduces to: **"what shape is my data, and what am I looking for?"**
This map turns the question into a pattern.

```
                              WHAT SHAPE IS THE INPUT?
                                       |
        +------------------+-----------+-----------+------------------+
        |                  |                       |                  |
     ARRAY / STRING     LINKED LIST            TREE / GRAPH        OPTIMIZATION /
        |                  |                       |               COUNTING
        |                  |                       |                  |
  +-----+-----+        +---+----+           +------+------+      "best / number of
  |     |     |        |        |           |      |      |       ways / min / max
 sum  pair  window   cycle?  reverse?     levels  paths  grid    over choices"
  |     |     |        |        |           |      |      |           |
Prefix  Two  Sliding  Fast &  In-place    BFS    DFS   Matrix    DYNAMIC
 Sum  Pointers Window  Slow   Reversal             Traversal   PROGRAMMING
                                                                     |
  sorted? -> Modified Binary Search          all combinations? -> Backtracking
  next greater/smaller? -> Monotonic Stack   top k? -> Heap
  merge ranges? -> Overlapping Intervals
```

---

## Master Mnemonic — "**PT-SF-LM-TO-MB-BD-BM-B**"

A single sentence to recall all 15 core patterns in order. Read the bold letters:

> **P**lease **T**ell **S**ally **F**rank **L**oves **M**aking **T**asty **O**melettes,
> **M**aybe **B**ake **B**read **M**onday **B**efore **B**reakfast.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second warm storybook animation. A cheerful couple, Sally and Frank, in a sunny cottage kitchen on a Monday morning: they whisk eggs and flip a golden omelette, then slide a fresh loaf of bread out of the oven, all before a breakfast table set at sunrise. Across the top, 15 glowing letter tiles light up one by one spelling P T S F L M T O M B B M B B B. Bold text overlay: "Please Tell Sally Frank Loves Making Tasty Omelettes, Maybe Bake Bread Monday Before Breakfast." Cozy, whimsical, golden morning light.
```

| # | Letter | Pattern | One-line trigger |
|---|--------|---------|------------------|
| 1 | **P** | Prefix Sum | "Sum of a range, asked many times" |
| 2 | **T** | Two Pointers | "Sorted array, find a pair" |
| 3 | **S** | Sliding Window | "Best contiguous subarray/substring" |
| 4 | **F** | Fast & Slow Pointers | "Cycle / middle of a sequence" |
| 5 | **L** | LinkedList In-place Reversal | "Flip pointers, no extra memory" |
| 6 | **M** | Monotonic Stack | "Next greater / smaller element" |
| 7 | **T** | Top K Elements (Heap) | "K largest / most frequent" |
| 8 | **O** | Overlapping Intervals | "Merge / schedule ranges" |
| 9 | **M** | Modified Binary Search | "Sorted or rotated, find target/boundary" |
| 10 | **B** | Binary Tree Traversal | "Pre / In / Post order" |
| 11 | **D** | DFS | "Explore every path deeply" |
| 12 | **B** | BFS | "Shortest path / level by level" |
| 13 | **M** | Matrix Traversal | "Flood fill / islands on a grid" |
| 14 | **B** | Backtracking | "All permutations/combinations/subsets" |
| 15 | **B** | (Bridge to) DP | "Optimal substructure + overlap" |

---

## Complexity at a glance (memorize this ladder)

From fastest to slowest — chant it: **"one, log, root-n, n, n-log-n, n-squared, two-to-the-n, n-factorial."**

```
O(1)  <  O(log n)  <  O(sqrt n)  <  O(n)  <  O(n log n)  <  O(n^2)  <  O(2^n)  <  O(n!)
 ▁          ▂            ▃           ▄          ▅              ▆          ▇          █
hash      binary       jump        single     sort /        nested    subsets   permutations
lookup    search       search       loop      heap-build     loops    / bitmask
```

Full tables live in [`00-complexity-foundations.md`](./00-complexity-foundations.md).

---

## Pattern → Complexity quick reference

### Core patterns
| Pattern | Typical Time | Typical Space |
|---------|--------------|---------------|
| Prefix Sum | `O(n)` build, `O(1)` query | `O(n)` |
| Two Pointers | `O(n)` (after `O(n log n)` sort if needed) | `O(1)` |
| Sliding Window | `O(n)` | `O(1)`–`O(k)` |
| Fast & Slow Pointers | `O(n)` | `O(1)` |
| LinkedList Reversal | `O(n)` | `O(1)` |
| Monotonic Stack | `O(n)` | `O(n)` |
| Top K (Heap) | `O(n log k)` | `O(k)` |
| Overlapping Intervals | `O(n log n)` | `O(n)` |
| Modified Binary Search | `O(log n)` | `O(1)` |
| Tree Traversal | `O(n)` | `O(h)` recursion |
| DFS | `O(V + E)` | `O(V)` |
| BFS | `O(V + E)` | `O(V)` |
| Matrix Traversal | `O(m·n)` | `O(m·n)` |
| Backtracking | `O(branch^depth)` | `O(depth)` |

### DP patterns
| Pattern | Typical Time | Typical Space |
|---------|--------------|---------------|
| Fibonacci / 1-D | `O(n)` | `O(1)`–`O(n)` |
| Kadane | `O(n)` | `O(1)` |
| 0/1 Knapsack | `O(n·W)` | `O(W)` |
| Unbounded Knapsack | `O(n·W)` | `O(W)` |
| LCS | `O(n·m)` | `O(n·m)`→`O(m)` |
| LIS | `O(n log n)` | `O(n)` |
| Palindromic Subseq | `O(n^2)` | `O(n^2)` |
| Edit Distance | `O(n·m)` | `O(n·m)` |
| Subset Sum | `O(n·S)` | `O(S)` |
| String Partition | `O(n^2)`–`O(n^3)` | `O(n)`–`O(n^2)` |
| Catalan | `O(n^2)` | `O(n)` |
| Matrix Chain | `O(n^3)` | `O(n^2)` |
| Count Distinct Ways | `O(n·k)` | `O(n)` |
| DP on Grids | `O(m·n)` | `O(m·n)`→`O(n)` |
| DP on Trees | `O(n)` | `O(h)` |
| DP on Graphs | `O(V·E)` etc. | `O(V)` |
| Digit DP | `O(digits·states)` | `O(digits·states)` |
| Bitmask DP | `O(2^n · n)` | `O(2^n)` |
| Probability DP | `O(states)` | `O(states)` |
| State Machine DP | `O(n·states)` | `O(states)` |

---

## A 4-week study plan

- **Week 1 — Arrays/Strings/Lists:** Patterns 1–9. Two problems each.
- **Week 2 — Trees/Graphs/Backtracking:** Patterns 10–15. Two problems each.
- **Week 3 — DP foundations:** DP patterns 1–10.
- **Week 4 — DP advanced + review:** DP patterns 11–20, then re-test all flashcards.

> **Golden rule:** You don't *memorize solutions*, you *internalize templates*. For each
> pattern, be able to write the skeleton from a blank screen before moving on.
