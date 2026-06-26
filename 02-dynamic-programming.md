# 02 — The 20 Dynamic Programming Patterns

> DP = **recursion + memory**. For every pattern below, anchor on the two questions:
> **(1) What is the STATE?** and **(2) What is the RECURRENCE?**
> They are listed easy → hard, exactly the order to learn them.

**The DP recipe (works every time):**
```
1. Define the state:        dp[i] / dp[i][j] = "answer for this subproblem"
2. Write the recurrence:    dp[i] = f(smaller dp[...])
3. Set the base cases:      dp[0] = ...
4. Choose an order:         fill so dependencies come first (top-down memo OR bottom-up table)
5. Read the answer:         usually dp[n] or dp[n][m]
6. Optimize space:          keep only the rows/vars you still need
```

**Top-down vs bottom-up (same recurrence, two styles):**
```
TOP-DOWN (memoization)            BOTTOM-UP (tabulation)
- recursion + @lru_cache          - loops fill a dp[] array
- only computes needed states     - no recursion stack, often O(1) space
- easiest to write first          - usually fastest / interview-preferred
```

| Jump | | | |
|---|---|---|---|
| [1. Fibonacci](#1-fibonacci-sequence) | [2. Kadane](#2-kadanes-algorithm) | [3. 0/1 Knapsack](#3-01-knapsack) | [4. Unbounded Knapsack](#4-unbounded-knapsack) |
| [5. LCS](#5-longest-common-subsequence-lcs) | [6. LIS](#6-longest-increasing-subsequence-lis) | [7. Palindromic Subseq](#7-palindromic-subsequence) | [8. Edit Distance](#8-edit-distance) |
| [9. Subset Sum](#9-subset-sum) | [10. String Partition](#10-string-partition) | [11. Catalan](#11-catalan-numbers) | [12. Matrix Chain](#12-matrix-chain-multiplication) |
| [13. Count Ways](#13-count-distinct-ways) | [14. DP on Grids](#14-dp-on-grids) | [15. DP on Trees](#15-dp-on-trees) | [16. DP on Graphs](#16-dp-on-graphs) |
| [17. Digit DP](#17-digit-dp) | [18. Bitmask DP](#18-bitmask-dp) | [19. Probability DP](#19-probability-dp) | [20. State Machine DP](#20-state-machine-dp) |

---

## 1. Fibonacci Sequence

> **Mnemonic:** *"Today = yesterday + the day before."*  · **State:** `dp[i]` · **Recurrence:** `dp[i] = dp[i-1] + dp[i-2]`

**8-second memory video** — copy into your AI video generator:
```prompt
8-second 3D animation of a glowing staircase. Three steps are labeled "day before", "yesterday", and "today". The numbers on the two lower steps lift up, merge, and add together to light up "today's" step with its sum. The pattern marches up the staircase: 1, 1, 2, 3, 5, 8. Bold text overlay: "Today = yesterday + the day before." Bright, clean, satisfying upward motion.
```

### Picture
```
stairs, 1 or 2 steps at a time:
ways(n) = ways(n-1) + ways(n-2)
ways: 1, 1, 2, 3, 5, 8, ...
```

### Code — Climbing Stairs (LeetCode 70), O(1) space
```python
def climb_stairs(n):
    a, b = 1, 1                          # ways to reach step 0 and 1
    for _ in range(2, n + 1):
        a, b = b, a + b                  # slide the window of two
    return b

# climb_stairs(5) -> 8
```

### Complexity
**`O(n)`** time, **`O(1)`** space.

### ⚠️ Watch out
- **`n = 0`:** return `1` (there's 1 way to stand on the ground) or `0` depending on the problem — read carefully.
- **`n = 1`:** both `a` and `b` are `1` — the loop doesn't execute — make sure you return the right variable.
- **Forgetting to initialize both `a` and `b`:** uninitialized values produce garbage.

### Practice
Climbing Stairs (70), Fibonacci Number (509), Min Cost Climbing Stairs (746).

---

## 2. Kadane's Algorithm

> **Mnemonic:** *"Carry the streak only if it helps."*  · **State:** best subarray ending at `i` · **Recurrence:** `cur = max(x, cur + x)`

**8-second memory video** — copy into your AI video generator:
```prompt
8-second cinematic animation. A runner crosses a landscape of glowing green hills (positive numbers) and red valleys (negative numbers), carrying a glowing "momentum" bar above their head. The bar grows on hills; when it would drop below zero in a deep valley, the runner drops it and instantly starts a fresh one. A golden flag marks the highest peak the bar ever reached. Bold text overlay: "Carry the streak only if it helps." Energetic, side-scrolling.
```

### Picture
```
nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
running best-ending-here resets when it turns negative:
                      [4, -1, 2, 1] = 6  <- max subarray
```

### Code — Maximum Subarray (LeetCode 53)
```python
def max_subarray(nums):
    cur = best = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)            # extend or restart
        best = max(best, cur)
    return best

# max_subarray([-2,1,-3,4,-1,2,1,-5,4]) -> 6
```

### Complexity
**`O(n)`** time, **`O(1)`** space.

### ⚠️ Watch out
- **All-negative array:** Kadane still works (`cur = max(x, cur + x)` picks the least-negative) — but if you initialize `best = 0` instead of `nums[0]`, you'll return `0` incorrectly.
- **Single element:** return that element — `cur = best = nums[0]` handles this.
- **Maximum Product variant (LC 152):** track both max and min (a negative × negative = positive) — don't reuse the sum template blindly.

### Practice
Maximum Subarray (53), Maximum Sum Circular Subarray (918), Maximum Product Subarray (152).

---

## 3. 0/1 Knapsack

> **Mnemonic:** *"Take it or leave it — each item once."*  · **State:** `dp[w]` best value at capacity `w` · **Recurrence:** `dp[w] = max(dp[w], dp[w-wt]+val)`

**8-second memory video** — copy into your AI video generator:
```prompt
8-second 3D animation. An open backpack with a glowing capacity meter sits beside a row of treasure items, each showing a weight and a value. A hand moves down the row making one decisive choice per item: toss it into the pack, or wave it away — each item touched exactly once. The value score climbs as the capacity meter fills. Bold text overlay: "Take it or leave it — each item once." Adventurous, warm lighting.
```

### Picture
```
items (wt,val): (1,1) (3,4) (4,5) (5,7)   capacity W=7
for each item, iterate capacity DOWNWARD so each item used at most once.
best value = 9   (items wt3+wt4 -> 4+5)
```

### Code — 1-D rolling array
```python
def knapsack_01(weights, values, W):
    dp = [0] * (W + 1)                   # dp[w] = best value with capacity w
    for i in range(len(weights)):
        for w in range(W, weights[i] - 1, -1):   # DOWNWARD -> item used once
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[W]

# knapsack_01([1,3,4,5], [1,4,5,7], 7) -> 9
```

### Worked example — Partition Equal Subset Sum (LeetCode 416)
Can we split into two equal-sum halves? = subset summing to `total/2`.

```python
def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    dp = [False] * (target + 1)          # dp[s] = can we reach sum s
    dp[0] = True
    for x in nums:
        for s in range(target, x - 1, -1):   # downward: each num once
            dp[s] = dp[s] or dp[s - x]
    return dp[target]

# can_partition([1, 5, 11, 5]) -> True
```

### Complexity
**`O(n·W)`** time, **`O(W)`** space.

### ⚠️ Watch out
- **Iterating capacity UPWARD instead of DOWNWARD:** this turns 0/1 into unbounded (each item reused) — the #1 knapsack bug.
- **Weight > capacity:** the inner loop's `range(W, weights[i]-1, -1)` handles this, but if you write `range(W, -1, -1)` you'll index `dp[w - weights[i]]` out of bounds.
- **Items with weight 0:** infinite items fit — usually not a valid input, but guard if needed.

### Practice
Partition Equal Subset Sum (416), Target Sum (494), Last Stone Weight II (1049).

---

## 4. Unbounded Knapsack

> **Mnemonic:** *"Infinite supply — reuse freely."*  · **Recurrence:** `dp[w] = max/min(dp[w], dp[w-wt]+val)` — iterate capacity **upward**.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second 3D animation. A backpack sits next to a glowing magic crate that instantly refills the same golden coin every time one is removed — an endless supply. A hand grabs the same coin type again and again, dropping copies into the pack to fill the capacity meter. Bold text overlay: "Infinite supply — reuse freely." Sparkly, magical, looping motion.
```

### Picture
```
0/1 knapsack:  iterate capacity DOWNWARD (each item once)
Unbounded:     iterate capacity UPWARD    (item reusable)
```

### Code — Coin Change (LeetCode 322), fewest coins
```python
def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount            # dp[a] = fewest coins to make a
    for coin in coins:
        for a in range(coin, amount + 1):    # UPWARD -> reuse coin
            dp[a] = min(dp[a], dp[a - coin] + 1)
    return dp[amount] if dp[amount] != INF else -1

# coin_change([1, 2, 5], 11) -> 3   (5 + 5 + 1)
```

### Complexity
**`O(n·amount)`** time, **`O(amount)`** space.

### ⚠️ Watch out
- **Iterating capacity DOWNWARD by mistake:** that makes it 0/1 knapsack (each coin used once).
- **`amount = 0`:** the answer is `0` coins, not impossible — `dp[0] = 0`.
- **No valid combination:** check `dp[amount] != INF` before returning.

### Practice
Coin Change (322), Coin Change II (518), Perfect Squares (279).

---

## 5. Longest Common Subsequence (LCS)

> **Mnemonic:** *"Match → diagonal +1; mismatch → best of dropping one."*  · **State:** `dp[i][j]` LCS of prefixes · **Recurrence:** below.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second clean 2D animation of a glowing grid with one word spelled down the left edge and another across the top. A bright token walks the grid: when the row letter and column letter match, it jumps diagonally down-right with a "+1" sparkle; when they mismatch, it slides to the better of the cell above or the cell to the left. Bold text overlay: "Match -> diagonal +1; mismatch -> drop one." Crisp, educational, neon-on-dark.
```

### Picture
```
        ""  a  c  e
    ""   0  0  0  0
     a   0  1  1  1
     b   0  1  1  1
     c   0  1  2  2
     d   0  1  2  2
     e   0  1  2  3   -> LCS("abcde","ace") = 3

match:    dp[i][j] = dp[i-1][j-1] + 1
mismatch: dp[i][j] = max(dp[i-1][j], dp[i][j-1])
```

### Code — Longest Common Subsequence (LeetCode 1143)
```python
def lcs(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]

# lcs("abcde", "ace") -> 3
```

### Space optimization — rolling row
Only two rows of the table are ever needed at once. Replace the 2D array with two 1D arrays:

```python
def lcs_optimized(a, b):
    n, m = len(a), len(b)
    prev = [0] * (m + 1)
    for i in range(1, n + 1):
        curr = [0] * (m + 1)
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[m]

# lcs_optimized("abcde", "ace") -> 3
```

> This is a common interview follow-up: "Can you do it in `O(m)` space?" The answer is always: keep only the previous row.

### ⚠️ Watch out
- **Empty strings:** `lcs("", anything)` = 0 — the `range(1, n+1)` loop simply doesn't execute.
- **Both strings identical:** LCS = the string itself — every cell takes the diagonal path.
- **Rolling-row indexing:** `curr[j]` uses `prev[j-1]` (diagonal), `prev[j]` (above), and `curr[j-1]` (left) — get these right or the answer is wrong.

### Practice
Longest Common Subsequence (1143), Delete Operation for Two Strings (583), Shortest Common Supersequence (1092).

---

## 6. Longest Increasing Subsequence (LIS)

> **Mnemonic:** *"Patience sorting — place each card on the leftmost taller pile."*  · **State:** `tails[k]` = smallest tail of an increasing subseq of length `k+1`.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second top-down animation of a card dealer at a green felt table. Numbered playing cards arrive one at a time; the dealer places each new card onto the leftmost pile whose top card is greater-or-equal, otherwise starts a new pile to the right. The piles grow; a counter showing the number of piles glows as the final answer. Bold text overlay: "Place each card on the leftmost taller pile." Calm, precise, casino lighting.
```

### Picture
```
nums = [10, 9, 2, 5, 3, 7, 101, 18]
tails grows: [2] -> [2,5] -> [2,3] -> [2,3,7] -> [2,3,7,18] (len 4)
each new x replaces the first tail >= x (binary search)
```

### Code — Longest Increasing Subsequence (LeetCode 300), O(n log n)
```python
import bisect

def length_of_lis(nums):
    tails = []                           # tails[k] = smallest possible tail of LIS length k+1
    for x in nums:
        i = bisect.bisect_left(tails, x) # first tail >= x
        if i == len(tails):
            tails.append(x)              # x extends the longest pile
        else:
            tails[i] = x                 # x improves an existing pile's tail
    return len(tails)

# length_of_lis([10,9,2,5,3,7,101,18]) -> 4
```

### Complexity
**`O(n log n)`** time, **`O(n)`** space. (The `O(n^2)` DP variant: `dp[i]=max(dp[j]+1)`.)

### ⚠️ Watch out
- **All-decreasing input:** LIS = 1 (just one element) — `tails` only ever has one entry.
- **Duplicate values:** `bisect_left` finds the first `>=` position — duplicates replace existing tails, they don't extend.
- **Reconstructing the actual subsequence:** the `tails` array does NOT store the actual LIS — you need a separate parent-tracking array.
- **`bisect_left` vs `bisect_right`:** for *strictly* increasing, use `bisect_left`; for *non-decreasing*, use `bisect_right`.

### Practice
Longest Increasing Subsequence (300), Number of LIS (673), Russian Doll Envelopes (354).

---

## 7. Palindromic Subsequence

> **Mnemonic:** *"Ends match → reach inward +2; else shrink a side."*  · **State:** `dp[i][j]` on substring `i..j`.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second elegant animation. A row of glowing letter tiles with two hands hovering at the far left and far right ends. When the two end letters match, the hands clasp them together with a "+2" sparkle and reach one tile inward on each side; when they differ, one side shrinks inward alone. They work toward the center. Bold text overlay: "Ends match -> reach inward +2; else shrink a side." Symmetric, smooth, glowing.
```

### Picture
```
s = "bbbab"   longest palindromic subsequence = "bbbb" (len 4)
ends equal: dp[i][j] = dp[i+1][j-1] + 2
ends differ: dp[i][j] = max(dp[i+1][j], dp[i][j-1])
fill by increasing length / decreasing i.
```

### Code — Longest Palindromic Subsequence (LeetCode 516)
```python
def longest_palindrome_subseq(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1                     # single char is a palindrome
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1] + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]

# longest_palindrome_subseq("bbbab") -> 4
```

### Complexity
**`O(n^2)`** time, **`O(n^2)`** space.

### ⚠️ Watch out
- **Single character:** always a palindrome of length 1 — `dp[i][i] = 1` base case.
- **Entire string is a palindrome:** every cell `dp[i][j]` takes the `+2` diagonal path — result = `n`.
- **Fill order:** iterate `i` from `n-1` down to `0` so that `dp[i+1][...]` is already filled — filling upward causes wrong answers.
- **Palindromic *substring* vs *subsequence*:** different problems! Substring requires contiguity (expand from center); subsequence allows gaps (this DP).

### Practice
Longest Palindromic Subsequence (516), Palindromic Substrings (647), Min Insertions to Make Palindrome (1312).

---

## 8. Edit Distance

> **Mnemonic:** *"Insert, Delete, Replace — pick the cheapest fix."*  · **State:** `dp[i][j]` edits to turn `a[:i]` into `b[:j]`.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second workshop animation. A word sits on a workbench with three glowing tool buttons labeled "INSERT", "DELETE", "REPLACE". A mechanic taps the cheapest tool to transform one word into a target word letter by letter — adding a letter, removing one, or swapping one — while a cost meter ticks up by one each fix. Bold text overlay: "Insert, Delete, Replace — pick the cheapest fix." Hands-on, tactile, warm light.
```

### Picture
```
        ""  r  o  s
    ""   0  1  2  3
     h   1  1  2  3
     o   2  2  1  2
     r   3  2  2  2
     s   4  3  3  2
     e   5  4  4  3   -> editDistance("horse","ros") = 3

match: dp[i][j] = dp[i-1][j-1]
else : 1 + min(replace dp[i-1][j-1], delete dp[i-1][j], insert dp[i][j-1])
```

### Code — Edit Distance (LeetCode 72)
```python
def edit_distance(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i                     # delete all
    for j in range(m + 1):
        dp[0][j] = j                     # insert all
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]

# edit_distance("horse", "ros") -> 3
```

### Space optimization — rolling row
Just like LCS, only two rows are needed. Use `prev` and `curr`:

```python
def edit_distance_optimized(a, b):
    n, m = len(a), len(b)
    prev = list(range(m + 1))            # base: edit "" into b[:j] = j inserts
    for i in range(1, n + 1):
        curr = [i] + [0] * m             # base: edit a[:i] into "" = i deletes
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j - 1], prev[j], curr[j - 1])
        prev = curr
    return prev[m]

# edit_distance_optimized("horse", "ros") -> 3
```

> Interview follow-up: "Optimize to `O(m)` space." Same rolling-row technique as LCS.

### ⚠️ Watch out
- **One string empty:** `edit_distance("", "abc")` = 3 (insert all) — the base-case row/column handles this.
- **Both strings identical:** every cell takes the diagonal `dp[i-1][j-1]` path — result = 0.
- **Confusing insert/delete/replace:** insert adds to `a`, delete removes from `a`, replace swaps in `a` — the three neighbors are `dp[i][j-1]`, `dp[i-1][j]`, `dp[i-1][j-1]`.
- **Rolling-row: `curr[0] = i`** — forgetting this base case for each row gives wrong answers.

### Practice
Edit Distance (72), Delete Operation for Two Strings (583), Minimum ASCII Delete Sum (712).

---

## 9. Subset Sum

> **Mnemonic:** *"Can these numbers hit the target?"*  · A boolean 0/1-knapsack twin.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second animation of a glowing dartboard whose bullseye shows a target number. Numbered chips fly in; a few of them combine mid-air and land exactly on the bullseye, summing to the target, which flashes bright green and stamps "TRUE". Bold text overlay: "Can these numbers hit the target?" Punchy, arcade-style, satisfying hit.
```

### Picture
```
nums = [3, 34, 4, 12, 5, 2], target = 9
reachable sums via include/exclude: ... {4,5} -> 9  -> True
```

### Code — Subset Sum (equivalent to Partition / Target Sum core)
```python
def subset_sum(nums, target):
    dp = [False] * (target + 1)          # dp[s] = is sum s achievable?
    dp[0] = True
    for x in nums:
        for s in range(target, x - 1, -1):
            dp[s] = dp[s] or dp[s - x]
    return dp[target]

# subset_sum([3, 34, 4, 12, 5, 2], 9) -> True
```

### Worked example — Target Sum (LeetCode 494)
Assign `+`/`-` to each number to reach `target`. Reduces to: subset with sum
`P = (total + target) / 2`, then count ways.

```python
def find_target_sum_ways(nums, target):
    total = sum(nums)
    if (total + target) % 2 or abs(target) > total:
        return 0
    P = (total + target) // 2
    dp = [0] * (P + 1)                    # dp[s] = number of subsets summing to s
    dp[0] = 1
    for x in nums:
        for s in range(P, x - 1, -1):
            dp[s] += dp[s - x]
    return dp[P]

# find_target_sum_ways([1, 1, 1, 1, 1], 3) -> 5
```

### Complexity
**`O(n·target)`** time, **`O(target)`** space.

### ⚠️ Watch out
- **Target = 0:** always `True` (the empty subset sums to 0) — `dp[0] = True` handles this.
- **Negative numbers:** standard subset sum assumes non-negative values — with negatives, the target range shifts and you need offset indexing.
- **Large target:** `O(n·target)` can be slow if `target` is huge — check constraints.
- **Target Sum reduction:** `(total + target)` must be even and `abs(target) ≤ total` — otherwise return 0 immediately.

### Practice
Partition Equal Subset Sum (416), Target Sum (494), Partition to K Equal Sum Subsets (698).

---

## 10. String Partition

> **Mnemonic:** *"Cut the string where a piece is valid, recurse on the rest."*  · **State:** `dp[i]` over the first `i` chars.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second animation. A long ribbon of letters stretches across the screen. Glowing scissors snip it at a point where the leading chunk lights up green as a valid dictionary word; the remaining ribbon then gets snipped again the same way, recursively, until the whole ribbon is cut into valid words. Bold text overlay: "Cut where a piece is valid, recurse on the rest." Clean, crafty, paper-cut style.
```

### Picture
```
s = "leetcode", words = {leet, code}
dp[i] = True if s[:i] can be segmented
dp[0]=T ... dp[4]=T (leet) ... dp[8]=T (leet|code) -> True
```

### Code — Word Break (LeetCode 139)
```python
def word_break(s, word_dict):
    words = set(word_dict)
    n = len(s)
    dp = [False] * (n + 1)               # dp[i] = s[:i] is segmentable
    dp[0] = True
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words: # valid split point at j
                dp[i] = True
                break
    return dp[n]

# word_break("leetcode", ["leet", "code"]) -> True
```

### Complexity
**`O(n^2)`** (substring hashing aside) time, **`O(n)`** space.

### ⚠️ Watch out
- **No valid segmentation:** `dp[n]` stays `False` — make sure you return `False`, not crash.
- **Single-character words:** every character might be a valid word — the inner loop checks all split points.
- **Very long strings:** the `O(n²)` inner loop can be slow — optimize with a Trie or limit `j` to `max(word_length)`.
- **Palindrome Partitioning II:** different problem (min cuts) — don't confuse with Word Break.

### Practice
Word Break (139), Palindrome Partitioning II (132), Concatenated Words (472).

---

## 11. Catalan Numbers

> **Mnemonic:** *"Pick a root/pivot, multiply left × right, sum over all pivots."*  · `C(n) = Σ C(i)·C(n-1-i)`.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second animation. A row of numbered nodes. One at a time, each node rises up to become a tree's root, splitting the rest into a left subtree and a right subtree; a "x" symbol multiplies the two subtree counts, and a running "+" counter sums the results across every choice of root. Bold text overlay: "Pick a pivot: left x right, summed over all pivots." Elegant, mathematical, glowing trees.
```

### Picture
```
Unique BSTs with n nodes:
C0=1, C1=1, C2=2, C3=5, C4=14, ...
choose each value as root: left subtree from smaller, right from larger.
```

### Code — Unique Binary Search Trees (LeetCode 96)
```python
def num_trees(n):
    dp = [0] * (n + 1)                   # dp[k] = #BSTs with k nodes
    dp[0] = dp[1] = 1
    for nodes in range(2, n + 1):
        for root in range(1, nodes + 1): # root splits into left/right sizes
            dp[nodes] += dp[root - 1] * dp[nodes - root]
    return dp[n]

# num_trees(3) -> 5
```

### Complexity
**`O(n^2)`** time, **`O(n)`** space.

### ⚠️ Watch out
- **`n = 0`:** C(0) = 1 (the empty structure is valid) — don't return 0.
- **Confusing Catalan with Fibonacci:** Catalan multiplies left × right subtree counts; Fibonacci adds.
- **Generate Parentheses:** the *count* is Catalan, but *generating* all strings requires backtracking, not DP.

### Practice
Unique Binary Search Trees (96), Generate Parentheses (22).

---

## 12. Matrix Chain Multiplication

> **Mnemonic:** *"Try every split point on the interval; combine the best."*  · **State:** `dp[i][j]` on interval `i..j` (interval DP).

**8-second memory video** — copy into your AI video generator:
```prompt
8-second animation. A glowing bracket spans a sequence of blocks. A vertical split marker slides to every possible position inside the bracket, each time showing a combine-cost number for splitting there. The cheapest split flashes gold and locks in, then the same happens on smaller sub-brackets. Bold text overlay: "Try every split point; combine the best." Precise, architectural, neon-on-dark.
```

### Picture
```
For interval [i..j], try each k as the last operation:
dp[i][j] = min over k of ( dp[i][k] + dp[k+1][j] + cost(i,k,j) )
fill by increasing interval length.
```

### Code — Burst Balloons (LeetCode 312)
Burst balloons last-to-first on each interval; `k` is the **last** balloon burst.

```python
def max_coins(nums):
    balloons = [1] + nums + [1]          # padding for boundaries
    n = len(balloons)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n):           # interval length between the two pads
        for left in range(0, n - length):
            right = left + length
            for k in range(left + 1, right):     # k = last balloon burst in (left,right)
                dp[left][right] = max(
                    dp[left][right],
                    dp[left][k] + balloons[left] * balloons[k] * balloons[right] + dp[k][right]
                )
    return dp[0][n - 1]

# max_coins([3, 1, 5, 8]) -> 167
```

### Complexity
**`O(n^3)`** time, **`O(n^2)`** space.

### ⚠️ Watch out
- **Interval length starts at 2, not 1:** single-element intervals are base cases (cost = 0).
- **Off-by-one on `k` range:** `k` iterates *inside* `(left, right)`, not inclusive of the boundaries.
- **Fill order:** you must fill by increasing interval length — filling row-by-row gives wrong answers.
- **Boundary padding (Burst Balloons):** the `[1] + nums + [1]` trick avoids messy boundary checks.

### Practice
Min Score Triangulation (1039), Burst Balloons (312), Minimum Cost to Merge Stones (1000).

---

## 13. Count Distinct Ways

> **Mnemonic:** *"Sum the ways from every state that can reach me."*  · Add (not max) over choices.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second animation. A glowing destination node with several incoming arrows, each arrow carrying a number of paths printed on it. The numbers flow along the arrows and pour into the node, where a big "+" ADDS them all into the node's total counter, which lights up. Bold text overlay: "Sum the ways from every state that can reach me." Flowing, additive, bright particles.
```

### Picture
```
Decode "226": dp[i] = #ways to decode s[:i]
'2'->dp1, '22'->dp2 (2,2 | 22), '226'->dp3 (2,2,6 | 22,6 | 2,26) = 3
dp[i] += dp[i-1] if s[i-1] valid; dp[i] += dp[i-2] if s[i-2:i] in 10..26
```

### Code — Decode Ways (LeetCode 91)
```python
def num_decodings(s):
    if not s or s[0] == "0":
        return 0
    n = len(s)
    prev2, prev1 = 1, 1                   # dp[i-2], dp[i-1]
    for i in range(1, n):
        cur = 0
        if s[i] != "0":                  # single-digit decode
            cur += prev1
        if "10" <= s[i - 1:i + 1] <= "26":   # two-digit decode
            cur += prev2
        prev2, prev1 = prev1, cur
    return prev1

# num_decodings("226") -> 3
```

### Complexity
**`O(n)`** time, **`O(1)`** space.

### ⚠️ Watch out
- **Leading zeros:** `"0"` is invalid as a single-digit decode — `if s[i] == "0": cur += 0` (skip).
- **`"10"` and `"20"`:** valid as two-digit, but `"0"` alone is invalid — the `"10" <= s[i-1:i+1] <= "26"` check catches this.
- **`"30"`, `"40"`, etc.:** invalid — no single-digit and no valid two-digit → `cur = 0` → return 0.
- **Counting ways (add) vs best value (max/min):** this is additive DP, not optimization DP.

### Practice
Decode Ways (91), Count Number of Texts (2266).

---

## 14. DP on Grids

> **Mnemonic:** *"Each cell sums/min's from its top and left neighbor."*  · **State:** `dp[r][c]`.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second top-down animation of a grid filling in from the top-left corner toward the bottom-right. Each cell lights up by pulling glowing values from the cell directly above it and the cell directly to its left, combining them (sum or min). A wave of illuminated cells sweeps diagonally across the grid. Bold text overlay: "Each cell comes from its top and left neighbor." Clean, techy, wave-like motion.
```

### Picture
```
unique paths (move right/down only):
1 1 1
1 2 3
1 3 6   -> dp[r][c] = dp[r-1][c] + dp[r][c-1]
```

### Code — Minimum Path Sum (LeetCode 64), O(n) space
```python
def min_path_sum(grid):
    cols = len(grid[0])
    dp = [float("inf")] * cols
    dp[0] = 0
    for r in range(len(grid)):
        dp[0] += grid[r][0]              # first column: only from above
        for c in range(1, cols):
            dp[c] = grid[r][c] + min(dp[c], dp[c - 1])   # min(top, left)
    return dp[-1]

# min_path_sum([[1,3,1],[1,5,1],[4,2,1]]) -> 7
```

### Complexity
**`O(m·n)`** time, **`O(n)`** space (rolling row).

### ⚠️ Watch out
- **Single-row or single-column grid:** only one path exists (all right or all down) — the loop still works, but verify.
- **Obstacles:** set `dp[r][c] = INF` (or 0 for counting) when a cell is blocked — don't forget to skip it.
- **Rolling-row space optimization:** only keep `dp[c]` for the current row — `dp[c] = grid[r][c] + min(dp[c], dp[c-1])`.
- **Longest Increasing Path (LC 329):** this is NOT simple grid DP — it requires DFS + memoization because you can move in all 4 directions.

### Practice
Unique Paths (62), Minimum Path Sum (64), Longest Increasing Path in a Matrix (329).

---

## 15. DP on Trees

> **Mnemonic:** *"Post-order: each node returns a small summary to its parent."*  · Often returns a tuple of states.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second animation of a glowing tree. The leaves compute first and float small glowing "summary" tokens upward to their parent nodes; each parent merges its children's tokens into a new token and passes it up, level by level, until the root collects the final summary. Bold text overlay: "Post-order: each node summarizes up to its parent." Organic, bottom-up glow, calm.
```

### Picture
```
House Robber III: at each node return (rob_this, skip_this)
rob_this  = node.val + skip(left) + skip(right)
skip_this = max(left states) + max(right states)
```

### Code — House Robber III (LeetCode 337)
```python
def rob(root):
    def dfs(node):
        if not node:
            return (0, 0)                # (rob this node, skip this node)
        l = dfs(node.left)
        r = dfs(node.right)
        rob_node = node.val + l[1] + r[1]    # rob node -> must skip children
        skip_node = max(l) + max(r)          # skip node -> children free to choose
        return (rob_node, skip_node)
    return max(dfs(root))

# tree [3,2,3,null,3,null,1] -> 7
```

### Complexity
**`O(n)`** time, **`O(h)`** space (recursion depth = tree height).

### ⚠️ Watch out
- **Leaf nodes (no children):** `dfs(None)` returns `(0, 0)` — make sure this base case is correct.
- **Root-only tree:** `dfs` returns `(root.val, 0)` — answer is `root.val`.
- **Returning a tuple, not a single value:** Tree DP almost always returns multiple states per node.
- **Binary Tree Maximum Path Sum (LC 124):** the "path" can span left-root-right, but a node can only contribute one branch upward — tricky.

### Practice
House Robber III (337), Binary Tree Maximum Path Sum (124), Binary Tree Cameras (968).

---

## 16. DP on Graphs

> **Mnemonic:** *"Relax edges in a valid order; track best-to-reach."*  · DAG DP / bounded Bellman-Ford.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second animation of a glowing node-and-edge graph. In rounds, the edges pulse one by one ("relaxing"); whenever a cheaper route is found, the destination node's cost label drops to a smaller glowing number. Over a few rounds the best-known costs settle. Bold text overlay: "Relax edges in order; track best-to-reach." Techy, network-like, pulses of light.
```

### Picture
```
Cheapest flight with <= K stops: do K+1 rounds of edge relaxation
dist[v] = min(dist[v], dist[u] + price(u,v)) using last round's snapshot.
```

### Code — Cheapest Flights Within K Stops (LeetCode 787)
```python
def find_cheapest_price(n, flights, src, dst, k):
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    for _ in range(k + 1):               # at most k stops => k+1 edges
        snapshot = dist[:]               # use previous round only (Bellman-Ford bounded)
        for u, v, price in flights:
            if snapshot[u] + price < dist[v]:
                dist[v] = snapshot[u] + price
    return dist[dst] if dist[dst] != INF else -1

# find_cheapest_price(3, [[0,1,100],[1,2,100],[0,2,500]], 0, 2, 1) -> 200
```

### Complexity
**`O(K·E)`** time, **`O(V)`** space.

### ⚠️ Watch out
- **Unreachable destination:** `dist[dst]` stays `INF` — return `-1`.
- **Forgetting the snapshot:** without `snapshot = dist[:]`, you use freshly-updated values in the same round, which violates the bounded-stops constraint.
- **Negative edges:** Bellman-Ford handles negatives, but not *negative cycles* — detect them with an extra round.
- **K = 0:** only direct flights from `src` — check if there's a direct edge.

### Practice
Cheapest Flights Within K Stops (787), Find the City With Smallest Number of Neighbors (1334).

---

## 17. Digit DP

> **Mnemonic:** *"Build the number digit by digit, hugging the upper bound."*  · State carries `(position, tight, ...)`.

**8-second memory video** — copy into your AI video generator:
```prompt
8-second animation. A row of empty digit slots fills in left to right, one digit at a time, like an odometer. A glowing horizontal "ceiling" line (the upper bound number) hovers above; each chosen digit rises to hug just under that ceiling, staying "tight" to the bound. Bold text overlay: "Build the number digit by digit, hugging the upper bound." Mechanical, precise, neon ceiling glow.
```

### Picture
```
Count numbers in [0..N] with some digit property:
state = (index, tight, started, accumulated_property)
'tight' = are we still equal to N's prefix? (limits the next digit)
```

### Code — Count Numbers with Unique Digits (LeetCode 357)
Equivalent digit-DP-style count of numbers in `[0, 10^n)` with all-distinct digits.

```python
from functools import lru_cache

def count_unique_digits(n):
    digits = [int(c) for c in str(10 ** n - 1)]   # upper bound 10^n - 1
    L = len(digits)

    @lru_cache(maxsize=None)
    def dp(pos, mask, tight, started):
        if pos == L:
            return 1                     # one valid number formed
        total = 0
        hi = digits[pos] if tight else 9
        for d in range(0, hi + 1):
            if started and (mask >> d) & 1:
                continue                 # digit already used -> not unique
            new_started = started or d > 0
            new_mask = mask | (1 << d) if new_started else 0
            total += dp(pos + 1, new_mask, tight and d == hi, new_started)
        return total

    return dp(0, 0, True, False)

# count_unique_digits(2) -> 91   (0..99 minus 11,22,...,99)
```

### Complexity
**`O(L · 2^10 · 2 · 2 · 10)`** ≈ states × transitions; effectively constant in `L`.

### ⚠️ Watch out
- **Leading zeros (the `started` flag):** `007` is not a valid 3-digit number — skip digit 0 until you've placed a non-zero digit.
- **`n = 0`:** usually means the range is `[0, 0]` — return 1 (just the number 0).
- **`tight` propagation:** `tight and d == hi` — if you forget `and d == hi`, subsequent digits won't be constrained.
- **Large digit counts:** Digit DP is efficient (`O(digits × states × 10)`), but make sure your `@lru_cache` can handle the state space.

### Practice
Count Numbers with Unique Digits (357), Number of Digit One (233), Numbers At Most N Given Digit Set (902).

---

## 18. Bitmask DP

> **Mnemonic:** *"The set of chosen items IS the state — store it in bits."*  · For small `n` (≤ ~20).

**8-second memory video** — copy into your AI video generator:
```prompt
8-second macro animation of a row of physical light switches mounted on a dark panel. The switches flip on and off; the on-switches glow and, below them, the pattern reads out as a binary number (like 1011) that represents exactly which items are chosen. Different switch patterns light up in sequence. Bold text overlay: "The chosen set IS the state — store it in bits." Sleek, tactile, glowing toggles.
```

### Picture
```
mask bits = which elements are used.   n=3:
000 () 001 {0} 010 {1} 011 {0,1} ... 111 {0,1,2}
dp[mask] = best result having used exactly the set 'mask'.
```

### Code — Travelling Salesman (Held-Karp) — equivalent to Shortest Path Visiting All Nodes (LeetCode 847 family)
```python
def shortest_tour(dist):
    n = len(dist)
    FULL = (1 << n) - 1
    INF = float("inf")
    # dp[mask][i] = min cost to have visited 'mask' ending at city i
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0                         # start at city 0
    for mask in range(1 << n):
        for i in range(n):
            if dp[mask][i] == INF or not (mask >> i) & 1:
                continue
            for j in range(n):
                if (mask >> j) & 1:
                    continue             # j already visited
                nmask = mask | (1 << j)
                dp[nmask][j] = min(dp[nmask][j], dp[mask][i] + dist[i][j])
    return min(dp[FULL][i] + dist[i][0] for i in range(n))   # return to start

# shortest_tour([[0,10,15,20],[10,0,35,25],[15,35,0,30],[20,25,30,0]]) -> 80
```

### Complexity
**`O(2^n · n^2)`** time, **`O(2^n · n)`** space.

### ⚠️ Watch out
- **n > 20:** `2^20` = 1M states — already at the limit. `n > 20` means > 1M states × n transitions — too slow.
- **Forgetting to check `(mask >> j) & 1`:** processing an already-visited city produces wrong answers.
- **Return to start:** TSP requires adding `dist[i][0]` at the end — don't forget the return leg.
- **Subset vs permutation:** Bitmask DP over subsets is `O(2^n · n)` — don't confuse with `O(n!)` permutation enumeration.

### Practice
Min Work Sessions to Finish Tasks (1986), Fair Distribution of Cookies (2305), Shortest Path Visiting All Nodes (847).

---

## 19. Probability DP

> **Mnemonic:** *"A state's probability = sum of (parent prob × transition prob)."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second animation of glowing liquid probability flowing through a network of pipes. At each branch the stream splits and is multiplied by a fraction label; downstream, several streams pool together and SUM into a reservoir representing a state's probability, which fills up and glows. Bold text overlay: "State probability = sum of (parent x transition)." Fluid, luminous, elegant.
```

### Picture
```
Knight on a board: prob_alive after k moves
each move splits into up to 8 equally-likely jumps (1/8 each).
dp[k][r][c] = sum over 8 sources of dp[k-1][src] / 8
```

### Code — Knight Probability in Chessboard (LeetCode 688)
```python
def knight_probability(n, k, row, col):
    moves = [(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1),(-2,1),(-1,2)]
    dp = [[0.0] * n for _ in range(n)]
    dp[row][col] = 1.0
    for _ in range(k):
        nxt = [[0.0] * n for _ in range(n)]
        for r in range(n):
            for c in range(n):
                if dp[r][c]:
                    for dr, dc in moves:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < n and 0 <= nc < n:
                            nxt[nr][nc] += dp[r][c] / 8.0   # each move 1/8
        dp = nxt
    return sum(map(sum, dp))             # total prob still on the board

# knight_probability(3, 2, 0, 0) -> 0.0625
```

### Complexity
**`O(k · n^2 · 8)`** time, **`O(n^2)`** space.

### ⚠️ Watch out
- **Floating-point precision:** probabilities can get very small — accumulated floating-point error may matter. Usually fine for LeetCode.
- **Absorbing states (off-board):** once the knight leaves the board, it stays gone — don't add probability back.
- **Summing probabilities > 1:** each move divides by 8, so the total stays ≤ 1 — if your answer > 1, there's a bug.

### Practice
Knight Probability in Chessboard (688), Soup Servings (808), New 21 Game (837).

---

## 20. State Machine DP

> **Mnemonic:** *"You're always in one of a few modes; transitions move you between them."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second animation of a neon state-machine diagram with a few labeled mode-bubbles ("HOLD", "SOLD", "REST") connected by glowing transition arrows labeled buy / sell / rest. A bright token hops from bubble to bubble along the arrows, always sitting in exactly one mode at a time. Bold text overlay: "Always in one of a few modes; transitions move you." Synthwave neon, clean diagram, rhythmic hops.
```

### Picture
```
Stock with cooldown — three states per day:
   HOLD  ---- sell ---->  COOLDOWN ---- rest ----> READY
   ^  |                                            |
   |  +------------------ rest --------------------+
   +-------------------- buy --------------------- (from READY)
```

### Code — Best Time to Buy and Sell Stock with Cooldown (LeetCode 309)
```python
def max_profit_cooldown(prices):
    if not prices:
        return 0
    hold = float("-inf")                 # holding a stock
    sold = 0                             # just sold today (then cooldown)
    rest = 0                             # idle / past cooldown
    for p in prices:
        prev_sold = sold
        sold = hold + p                  # sell what we held
        hold = max(hold, rest - p)       # keep holding, or buy from rest
        rest = max(rest, prev_sold)      # stay resting, or come off cooldown
    return max(sold, rest)               # never end while holding

# max_profit_cooldown([1, 2, 3, 0, 2]) -> 3
```

### Complexity
**`O(n)`** time, **`O(1)`** space.

### ⚠️ Watch out
- **Ending in the wrong state:** `return max(sold, rest)` — never end while holding stock (that's unrealized value).
- **Initial `hold = -inf`:** you can't sell what you don't own — starting `hold = 0` is a bug.
- **Multiple transaction variants (LC 123, 188):** add a `k` dimension for max transactions — the state machine generalizes.
- **Fee variant (LC 714):** subtract `fee` on sell, not on buy — either works but be consistent.

### Practice
Best Time to Buy/Sell with Cooldown (309), Best Time to Buy/Sell Stock III (123).

---

## DP pattern selector (use when stuck)

```
Is it a sequence with f(n)=f(n-1)+...?           -> Fibonacci / Count Ways
Max/min contiguous run?                          -> Kadane
Pick items, capacity limit, each once?           -> 0/1 Knapsack / Subset Sum
...items reusable?                               -> Unbounded Knapsack
Two strings, align them?                         -> LCS / Edit Distance
One sequence, increasing order?                  -> LIS
Palindrome on substring i..j?                    -> Palindromic Subsequence
Split a string into valid pieces?                -> String Partition
Count BSTs / parenthesizations?                  -> Catalan
Best split of an interval, combine cost?         -> Matrix Chain (interval DP)
Path/cost on a 2D grid?                           -> DP on Grids
Aggregate over a tree, children->parent?         -> DP on Trees
Optimal cost over edges with bounded steps?      -> DP on Graphs
Count numbers in [0..N] with digit property?     -> Digit DP
Small n (<=20), subset as state?                 -> Bitmask DP
Expected value / probability over steps?         -> Probability DP
A few discrete "modes" with transitions?         -> State Machine DP
```

Test yourself next → [`03-flashcards.md`](./03-flashcards.md).
