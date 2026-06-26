# 01 — The 15 Core Patterns

Ordered for learning: **arrays/strings → linked lists → stacks/heaps/intervals →
binary search → trees → graphs → grids → backtracking → (bridge to DP)**.

Every section has the same shape so your brain learns *where to look*:

> **Mnemonic** · **Picture** · **When to use** · **Template** · **Worked example** · **Complexity** · **Practice**

**Recall sentence (read the bold letters):**
**P**lease **T**ell **S**ally **F**rank **L**oves **M**aking **T**asty **O**melettes,
**M**aybe **B**ake **B**read **M**onday **B**efore **B**reakfast.

| Jump to | | | |
|---|---|---|---|
| [1. Prefix Sum](#1-prefix-sum) | [2. Two Pointers](#2-two-pointers) | [3. Sliding Window](#3-sliding-window) | [4. Fast & Slow](#4-fast--slow-pointers) |
| [5. LL Reversal](#5-linkedlist-in-place-reversal) | [6. Monotonic Stack](#6-monotonic-stack) | [7. Top K / Heap](#7-top-k-elements-heap) | [8. Intervals](#8-overlapping-intervals) |
| [9. Binary Search](#9-modified-binary-search) | [10. Tree Traversal](#10-binary-tree-traversal) | [11. DFS](#11-depth-first-search-dfs) | [12. BFS](#12-breadth-first-search-bfs) |
| [13. Matrix](#13-matrix-traversal) | [14. Backtracking](#14-backtracking) | [15. Bridge to DP](#15-bridge-to-dynamic-programming) | |

---

## 1. Prefix Sum

> **Mnemonic:** *"Pre-cook the sums, serve ranges instantly."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second video, warm cozy kitchen, top-down then dolly-in. A chef pre-cooks a row of six glowing numbered soup pots; each pot pours its broth into the next so the totals keep accumulating (running totals). A customer's ticket reads "range 2 to 4"; the chef instantly subtracts one pot from another and slides out a single steaming bowl in a flash. Bold text overlay: "Pre-cook the sums, serve ranges instantly." Warm golden lighting, fast satisfying motion.
```

### Picture
Turn the array into running totals. A range sum becomes one subtraction.

```
nums  =  [ 1 , 2 , 3 , 4 , 5 , 6 ]
prefix=  [ 1 , 3 , 6 ,10 ,15 ,21 ]      prefix[i] = nums[0]+...+nums[i]

sum(i..j) = prefix[j] - prefix[i-1]
sum(1..3) = prefix[3] - prefix[0] = 10 - 1 = 9   ✔ (2+3+4)
```

### When to use
- Many **range-sum queries** on a static array.
- "Subarray that sums to K", "equal 0s and 1s", running balances.

### Template
```python
def build_prefix(nums):
    prefix = [0] * (len(nums) + 1)      # prefix[0] = 0 sentinel avoids i-1 edge cases
    for i, x in enumerate(nums):
        prefix[i + 1] = prefix[i] + x
    return prefix

def range_sum(prefix, i, j):            # inclusive sum of nums[i..j]
    return prefix[j + 1] - prefix[i]
```

### Worked example — Subarray Sum Equals K (LeetCode 560)
Count subarrays whose sum equals `k`. The trick: a running sum + a hash map of
*previously seen running sums*.

```python
from collections import defaultdict

def subarray_sum(nums, k):
    count = 0
    running = 0
    seen = defaultdict(int)
    seen[0] = 1                          # empty prefix
    for x in nums:
        running += x
        count += seen[running - k]       # how many earlier prefixes make (running - prev) == k
        seen[running] += 1
    return count

# subarray_sum([1, 1, 1], 2) -> 2
```

### Complexity
- Build: **`O(n)` time**, query: **`O(1)`**. Hash-map version: **`O(n)` time, `O(n)` space.**

### ⚠️ Watch out
- **Empty array:** handle `len(nums) == 0` before building the prefix.
- **Integer overflow:** large sums can overflow in C++/Java — Python handles big ints natively, but mention it in interviews.
- **Off-by-one on range boundaries:** the `prefix[0] = 0` sentinel avoids `i-1` going negative, but forgetting it causes wrong answers.
- **Subarray sum variant needs a hash map**, not raw prefix subtraction — don't confuse the two templates.

### Practice
- Range Sum Query – Immutable (303), Contiguous Array (525), Subarray Sum Equals K (560).

---

## 2. Two Pointers

> **Mnemonic:** *"Squeeze from both ends."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second clean minimalist 3D animation. A sorted left-to-right row of numbered blocks sits on a white table. Two glowing arrow-hands, one at the far left, one at the far right, slide inward toward each other, squeezing the row. They clamp onto a matching pair of blocks that flash bright green with a satisfying snap. Bold text overlay: "Squeeze from both ends." Snappy motion, soft studio lighting.
```

### Picture
On a **sorted** array, walk `left` up and `right` down based on the comparison.

```
target = 6
[ 1 , 2 , 3 , 4 , 6 ]
  L               R     1+6=7 > 6 -> move R left
  L           R         1+4=5 < 6 -> move L right
      L       R         2+4=6 == 6 -> found (indices 1,3)
```

### When to use
- **Sorted** input, find a pair/triplet meeting a condition.
- Palindrome checks, removing duplicates in place, partitioning.

### Template
```python
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return [left, right]
        elif s < target:
            left += 1                    # need bigger -> raise the floor
        else:
            right -= 1                   # need smaller -> lower the ceiling
    return [-1, -1]
```

### Worked example — 3Sum (LeetCode 15)
Fix one number, two-pointer the rest. Sorting enables both the scan and dedup.

```python
def three_sum(nums):
    nums.sort()
    res = []
    n = len(nums)
    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue                     # skip duplicate anchors
        left, right = i + 1, n - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                res.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1            # skip duplicate seconds
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1           # skip duplicate thirds
            elif total < 0:
                left += 1
            else:
                right -= 1
    return res

# three_sum([-1, 0, 1, 2, -1, -4]) -> [[-1, -1, 2], [-1, 0, 1]]
```

### Complexity
- Pair scan: **`O(n)`** time, **`O(1)`** space (plus `O(n log n)` if you must sort).
- 3Sum: **`O(n^2)`** time.

### ⚠️ Watch out
- **Input must be sorted** (or you sort first) — two pointers on unsorted data gives wrong answers.
- **All-same values:** e.g. `[2,2,2,2]` with target 4 — make sure you handle duplicate pairs correctly.
- **Single element or empty array:** `left < right` loop guard already handles this, but double-check.
- **3Sum dedup:** skipping `nums[i] == nums[i-1]` is essential — forgetting it produces duplicate triplets.

### Practice
- Two Sum II (167), 3Sum (15), Container With Most Water (11).

---

## 3. Sliding Window

> **Mnemonic:** *"Grow right, shrink left, keep the best."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second sleek 2D motion graphic. A glowing rectangular window frame slides across a long row of number tiles. Its right edge stretches to swallow new tiles, its left edge contracts to drop old ones. A floating "BEST" score counter ticks upward, then freezes and pulses gold when the window lands on the winning stretch. Bold text overlay: "Grow right, shrink left, keep the best." Neon-on-dark, smooth crisp motion.
```

### Picture
A window `[left, right]` slides across; expand to include, contract to stay valid.

```
nums = [2, 1, 5, 1, 3, 2], k = 3  (max sum of size-3 window)
[2  1  5] 1  3  2      sum=8
 2 [1  5  1] 3  2      sum=7
 2  1 [5  1  3] 2      sum=9  <- best
 2  1  5 [1  3  2]     sum=6
```

### When to use
- **Contiguous** subarray/substring asking for max/min/longest/shortest.
- Fixed window (size `k`) or variable window (grow/shrink on a condition).

### Template — fixed size
```python
def max_sum_subarray(nums, k):
    window = sum(nums[:k])
    best = window
    for right in range(k, len(nums)):
        window += nums[right] - nums[right - k]   # add new, drop old
        best = max(best, window)
    return best
```

### Template — variable size
```python
def longest_unique_substring(s):         # LeetCode 3
    seen = {}                            # char -> last index
    left = 0
    best = 0
    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1          # jump left past the duplicate
        seen[ch] = right
        best = max(best, right - left + 1)
    return best

# longest_unique_substring("abcabcbb") -> 3  ("abc")
```

### Complexity
- **`O(n)`** time (each element enters and leaves once), **`O(1)`–`O(k)`** space.

### ⚠️ Watch out
- **Window size > array length:** for fixed-size windows, check `k <= len(nums)` first.
- **Negative numbers:** sliding window for "subarray sum ≥ target" only works with non-negative values — with negatives, use prefix sum + binary search.
- **Empty string:** always guard `if not s: return 0`.
- **Variable window:** make sure `left` never passes `right` — use `while left <= right and <invalid>` to shrink.

### Practice
- Maximum Average Subarray I (643), Longest Substring Without Repeating (3), Minimum Window Substring (76).

---

## 4. Fast & Slow Pointers

> **Mnemonic:** *"Tortoise and Hare — the hare laps the loop."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second playful cartoon, top-down view. A racetrack shaped like a number "6" — a tail leading into a closed loop. A slow tortoise and a fast hare start together; the hare moves exactly twice as fast, races around the loop, and bumps into the tortoise from behind inside the loop with a comic collision and stars. Bold text overlay: "Tortoise & Hare — the hare laps the loop." Bright, bouncy, fun.
```

### Picture
`slow` moves 1 step, `fast` moves 2. In a cycle, `fast` eventually meets `slow`.

```
1 -> 2 -> 3 -> 4
          ^         |
          |_________|

slow: 1,2,3,4,3...   fast: 1,3,3...  -> they collide inside the loop
```

### When to use
- Detect a **cycle** in a linked list / functional graph.
- Find the **middle** node, or the cycle's entry point.

### Template
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
```

### Worked example — Find the Duplicate Number (LeetCode 287)
Treat the array as a linked list where `i -> nums[i]`. The duplicate is the cycle entry.

```python
def find_duplicate(nums):
    slow = fast = nums[0]
    while True:                          # phase 1: find collision
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = nums[0]                       # phase 2: find entrance
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow

# find_duplicate([1, 3, 4, 2, 2]) -> 2
```

### Complexity
- **`O(n)`** time, **`O(1)`** space.

### ⚠️ Watch out
- **Empty list / single node:** `while fast and fast.next` handles this — if you forget `fast.next`, you'll crash on single nodes.
- **No cycle exists:** fast reaches `None` and the loop exits — make sure you return `False`, not crash.
- **Finding the middle:** for even-length lists, `slow` ends at the *second* middle node — know which one the problem expects.
- **Phase 2 (cycle entry):** you must reset only *one* pointer to head, not both — a common mistake.

### Practice
- Linked List Cycle (141), Happy Number (202), Find the Duplicate Number (287).

---

## 5. LinkedList In-place Reversal

> **Mnemonic:** *"Three hands: prev, curr, next — flip and march."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second mechanical 3D animation. A chain of glowing boxes (linked-list nodes) connected by forward-pointing arrows. Three labeled robotic hands hover above them, tagged "prev", "curr", "next". In a steady rhythm the hands flip each arrow to point backward, one node at a time, then march one step to the right and repeat, leaving a fully reversed chain. Bold text overlay: "prev · curr · next — flip and march." Industrial, rhythmic, clean.
```

### Picture
Reverse pointers one node at a time without extra memory.

```
prev=None  curr=1 -> 2 -> 3 -> None

step: save nxt; curr.next = prev; prev = curr; curr = nxt
None <- 1    2 -> 3
None <- 1 <- 2    3
None <- 1 <- 2 <- 3   (prev is the new head)
```

### When to use
- Reverse a whole list or a **sublist**; reverse in **groups of k**.

### Template — full reversal
```python
def reverse_list(head):
    prev = None
    curr = head
    while curr:
        nxt = curr.next                  # 1) remember the rest
        curr.next = prev                 # 2) flip the pointer
        prev = curr                      # 3) advance prev
        curr = nxt                       # 4) advance curr
    return prev
```

### Worked example — Reverse Linked List II (LeetCode 92)
Reverse only positions `m..n` using a dummy head to simplify edge cases.

```python
def reverse_between(head, m, n):
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(m - 1):               # walk to node before position m
        prev = prev.next
    curr = prev.next
    for _ in range(n - m):               # head-insertion reversal of the sublist
        nxt = curr.next
        curr.next = nxt.next
        nxt.next = prev.next
        prev.next = nxt
    return dummy.next
```

### Complexity
- **`O(n)`** time, **`O(1)`** space.

### ⚠️ Watch out
- **Single node:** `curr.next` is `None`, so the loop body never executes — returns correctly, but verify.
- **Sublist reversal (m=1):** without a dummy head node, `prev` is `None` and you special-case the head — use a dummy to avoid this.
- **k-group reversal:** if remaining nodes < k, don't reverse — count first.
- **Losing the tail:** after reversal, the old head is now the tail — make sure it points to the right next segment.

### Practice
- Reverse Linked List (206), Reverse Linked List II (92), Swap Nodes in Pairs (24).

---

## 6. Monotonic Stack

> **Mnemonic:** *"Keep the stack tidy; pop the losers when a bigger one arrives."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second 3D animation. A neat vertical stack of blocks whose heights decrease toward the top. A new, much taller block slides in from the right; as it arrives it knocks the shorter blocks off the top one by one (they pop away and fade) until order is restored, then it settles cleanly on top. Bold text overlay: "Pop the losers when a bigger one arrives." Crisp, weighty motion, dark studio background.
```

### Picture
A stack kept increasing/decreasing. New element pops everything it beats —
those popped just found their "next greater".

```
nums = [2, 1, 2, 4, 3]   (next greater element)
i=0 push 2        stack(idx)=[0]
i=1 1<2 push      stack=[0,1]
i=2 2>1 pop1(ans=2); 2==2 push  stack=[0,2]
i=3 4>2 pop2(ans=4); 4>2 pop0(ans=4); push  stack=[3]
i=4 3<4 push      stack=[3,4]   leftovers -> -1
ans = [4, 2, 4, -1, -1]
```

### When to use
- **Next greater / next smaller** element; spans; largest rectangle; daily temperatures.

### Template
```python
def next_greater(nums):
    n = len(nums)
    res = [-1] * n
    stack = []                           # holds indices, values decreasing
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            res[stack.pop()] = x         # x is the next greater for popped index
        stack.append(i)
    return res

# next_greater([2, 1, 2, 4, 3]) -> [4, 2, 4, -1, -1]
```

### Worked example — Daily Temperatures (LeetCode 739)
How many days until a warmer temperature? Store indices, pop when warmer.

```python
def daily_temperatures(temps):
    res = [0] * len(temps)
    stack = []                           # decreasing temperatures (indices)
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            res[j] = i - j               # distance in days
        stack.append(i)
    return res

# daily_temperatures([73,74,75,71,69,72,76,73]) -> [1,1,4,2,1,1,0,0]
```

### Complexity
- **`O(n)`** time (each index pushed/popped once), **`O(n)`** space.

### ⚠️ Watch out
- **All ascending or all descending:** the stack might never pop (ascending) or pop everything immediately (descending) — both are valid but test them.
- **Single element:** result is `[-1]` — make sure your loop handles it.
- **Circular array (Next Greater Element II):** loop `2*n` and use `i % n` — don't forget the wraparound.
- **Indices vs values:** store *indices* on the stack, not values — you'll need the index to fill the result array.

### Practice
- Next Greater Element I (496), Daily Temperatures (739), Largest Rectangle in Histogram (84).

---

## 7. Top 'K' Elements (Heap)

> **Mnemonic:** *"Keep a heap of size K; kick out the weakest."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second cinematic 3D animation. A small velvet VIP pedestal holds exactly K=3 glowing gems. New gems keep arriving at a rope barrier; each time a brighter, bigger gem enters, a bouncer kicks the dimmest gem off the pedestal and out the door. The pedestal always holds the top 3 brightest. Bold text overlay: "Heap of size K — kick out the weakest." Moody club lighting, sparkle highlights.
```

### Picture
For the **K largest**, keep a **min-heap of size K**. The root is the weakest of
your current winners; anything bigger than it kicks it out.

```
k=2, stream = 3, 2, 1, 5, 6, 4
heap (min on top):
 3        -> [3]
 2        -> [2,3]
 1        -> 1<root(2) discard -> [2,3]
 5        -> push,pop -> [3,5]
 6        -> push,pop -> [5,6]
 4        -> 4<root(5) discard -> [5,6]
2nd largest = root = 5
```

### When to use
- "K largest / smallest / most frequent / closest." Streaming top-K.

### Template
```python
import heapq

def kth_largest(nums, k):
    heap = []                            # min-heap of the k largest so far
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)          # drop the smallest -> keep top k
    return heap[0]                       # root = kth largest

# kth_largest([3, 2, 1, 5, 6, 4], 2) -> 5
```

### Worked example — Top K Frequent Elements (LeetCode 347)
```python
from collections import Counter
import heapq

def top_k_frequent(nums, k):
    freq = Counter(nums)
    # nlargest by frequency: O(n log k)
    return [val for val, _ in heapq.nlargest(k, freq.items(), key=lambda kv: kv[1])]

# top_k_frequent([1,1,1,2,2,3], 2) -> [1, 2]
```

### Complexity
- **`O(n log k)`** time, **`O(k)`** space. (Full sort would be `O(n log n)`.)

### ⚠️ Watch out
- **k = 0:** return empty — don't push anything.
- **k ≥ n:** the answer is the whole array (or the smallest element for kth-largest) — guard for this.
- **All elements equal:** the heap works correctly but verify your answer is right (kth largest of `[5,5,5]` is `5`).
- **Max-heap in Python:** Python only has min-heap — push negated values `(-val, val)` for max-heap behavior.

### Practice
- Kth Largest Element (215), Top K Frequent Elements (347), Find K Pairs with Smallest Sums (373).

---

## 8. Overlapping Intervals

> **Mnemonic:** *"Sort by start, then stitch the overlaps."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second clean 2D motion graphic on a horizontal timeline. Several colored horizontal bars (time intervals) float in scattered, then snap into order aligned by their left starting edges. Bars that overlap merge together with a glowing zipper-stitch effect into single longer bars; non-overlapping bars stay separate with visible gaps. Bold text overlay: "Sort by start, stitch the overlaps." Flat design, smooth snappy transitions.
```

### Picture
Two intervals `[a,b]` and `[c,d]` (sorted by start) overlap when `b >= c`.

```
[1,3] [2,6] [8,10] [15,18]   (sorted by start)
[1,3]+[2,6]  -> 3>=2 overlap -> [1,6]
[1,6] vs [8,10] -> 6<8 gap   -> keep [1,6], start [8,10]
[8,10] vs [15,18] -> gap     -> [8,10], [15,18]
merged = [[1,6],[8,10],[15,18]]
```

### When to use
- **Merge**, insert, or count non-overlapping ranges; meeting rooms; calendars.

### Template
```python
def merge_intervals(intervals):
    intervals.sort(key=lambda iv: iv[0]) # sort by start
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)   # extend the last
        else:
            merged.append([start, end])               # disjoint -> new block
    return merged

# merge_intervals([[1,3],[2,6],[8,10],[15,18]]) -> [[1,6],[8,10],[15,18]]
```

### Worked example — Non-overlapping Intervals (LeetCode 435)
Minimum removals to make intervals non-overlapping → greedily keep earliest finishers.

```python
def erase_overlap_intervals(intervals):
    intervals.sort(key=lambda iv: iv[1]) # sort by END time
    removals = 0
    prev_end = float("-inf")
    for start, end in intervals:
        if start >= prev_end:
            prev_end = end               # keep it
        else:
            removals += 1                # overlaps -> drop it
    return removals

# erase_overlap_intervals([[1,2],[2,3],[3,4],[1,3]]) -> 1
```

### Complexity
- **`O(n log n)`** time (the sort dominates), **`O(n)`** space.

### ⚠️ Watch out
- **Single interval:** result is just that interval — make sure your loop still appends it.
- **Touching endpoints:** `[1,2]` and `[2,3]` — are these overlapping? Usually yes (`start <= merged[-1][1]`), but read the problem carefully.
- **Fully nested intervals:** `[1,10]` and `[2,3]` — the merge should keep `[1,10]`, not `[1,3]`. Use `max(end)` not just `end`.
- **Sorting by start vs end:** merge uses start-sort, but "minimum removals" uses end-sort (greedy earliest finish).

### Practice
- Merge Intervals (56), Insert Interval (57), Non-Overlapping Intervals (435).

---

## 9. Modified Binary Search

> **Mnemonic:** *"Halve and conquer — even when the array is twisted."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second dramatic 3D animation. A long glowing ruler of numbers, slightly bent and twisted (a rotated array). A samurai blade of light slices it cleanly in half; the wrong half dissolves away. The blade slices the remaining half again and again, halving each time, until a spotlight lands on the single target number that flashes gold. Bold text overlay: "Halve and conquer." Sharp, high-contrast, confident motion.
```

### Picture
Standard search halves the range. In a **rotated** array, one half is always sorted —
decide which, then check if the target lies in it.

```
[4, 5, 6, 7, 0, 1, 2]  target=0
lo=0 hi=6 mid=3 ->7. left [4..7] sorted. 0 not in [4,7] -> go right
lo=4 hi=6 mid=5 ->1. right? left [0..1] sorted. 0 in [0,1] -> go left
lo=4 hi=4 -> nums[4]=0 found at index 4
```

### When to use
- **Sorted / rotated** arrays; find target, boundary, first/last, or a peak.
- "Search space" problems (min capacity, smallest feasible value).

### Template — classic + boundary
```python
def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2             # in Python no overflow, but habit: lo + (hi-lo)//2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

### Worked example — Search in Rotated Sorted Array (LeetCode 33)
```python
def search_rotated(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:        # left half is sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                            # right half is sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1

# search_rotated([4,5,6,7,0,1,2], 0) -> 4
```

### Complexity
- **`O(log n)`** time, **`O(1)`** space.

### ⚠️ Watch out
- **Single element array:** `lo == hi == mid` — make sure you return it if it matches, not loop forever.
- **Target not present:** return `-1` or the insertion point — know which the problem asks for.
- **`lo + hi` overflow:** in Python this is safe, but in C++/Java use `lo + (hi - lo) // 2`. Mention this in interviews.
- **Rotated array:** always check which half is sorted *first* (`nums[lo] <= nums[mid]`), then decide.
- **Duplicates in rotated:** `[1,1,1,0,1]` breaks the sorted-half check — worst case degrades to `O(n)`.

### Practice
- Search in Rotated Sorted Array (33), Find Minimum in Rotated Sorted Array (153), Search a 2D Matrix II (240).

---

## 10. Binary Tree Traversal

> **Mnemonic:** *"PIP — **P**re (root first), **I**n (root middle), **P**ost (root last)."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second clean 3D animation. A glowing binary tree with a root and two children. A spotlight visits the nodes three times in three quick labeled passes: "PRE" lights the root first then children; "IN" lights left child, then root, then right; "POST" lights both children then the root last. A tracing line follows each order. Bold text overlay spelling: "PIP — Pre · In · Post." Soft glow, educational, smooth.
```

### Picture
Where you "visit" the root relative to its children defines the order.

```
        1
       / \
      2   3
     / \
    4   5

Preorder  (Root,L,R): 1 2 4 5 3
Inorder   (L,Root,R): 4 2 5 1 3   <- BST gives SORTED output
Postorder (L,R,Root): 4 5 2 3 1   <- bottom-up / delete safely
```

### When to use
- **Inorder** → sorted order in a BST. **Preorder** → copy/serialize.
  **Postorder** → aggregate from children up (sizes, heights, deletes).

### Template
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorder(root):
    res = []
    def dfs(node):
        if not node:
            return
        dfs(node.left)
        res.append(node.val)             # visit root between children
        dfs(node.right)
    dfs(root)
    return res
```

### Worked example — Kth Smallest in a BST (LeetCode 230)
Inorder yields ascending values; stop at the kth.

```python
def kth_smallest(root, k):
    stack = []
    curr = root
    while stack or curr:
        while curr:                      # dive left
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        k -= 1
        if k == 0:
            return curr.val              # kth visited = kth smallest
        curr = curr.right                # then go right
```

### Complexity
- **`O(n)`** time, **`O(h)`** space (`h` = height; `O(n)` worst, `O(log n)` balanced).

### ⚠️ Watch out
- **Empty tree (`root is None`):** return `[]` or `0` immediately — don't recurse into `None`.
- **Single node:** the traversal returns `[root.val]` — trivial but verify.
- **Skewed tree (all left or all right):** recursion depth = `n`, risking stack overflow — consider iterative for deep trees.
- **Confusing orders:** PRE = root *first*, IN = root *middle*, POST = root *last*. A BST inorder is *always sorted*.

### Practice
- Binary Tree Paths (257, pre), Kth Smallest in a BST (230, in), Binary Tree Maximum Path Sum (124, post).

---

## 11. Depth-First Search (DFS)

> **Mnemonic:** *"Go deep, hit a wall, back up, try the next door."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second atmospheric first-person-style animation. A torch-lit stone maze. The camera rushes deep down one corridor until it hits a dead-end wall, then quickly backs up to the last junction and turns into the next open doorway, diving deep again. Bold text overlay: "Go deep, hit a wall, back up, try the next door." Flickering warm torchlight, adventurous shadowy mood.
```

### Picture
Explore one branch fully before the next. Recursion (or an explicit stack) does this.

```
        A
       / \
      B   C
     / \
    D   E
visit order: A -> B -> D (deepest) -> back -> E -> back -> C
```

### When to use
- Enumerate **paths**, detect cycles, topological sort, connected components,
  tree aggregation.

### Template — graph DFS with visited set
```python
def dfs(graph, start):
    visited = set()
    order = []
    def explore(node):
        visited.add(node)
        order.append(node)
        for nxt in graph[node]:
            if nxt not in visited:
                explore(nxt)
    explore(start)
    return order
```

### Worked example — Course Schedule II / topological order (LeetCode 210)
Return an order to take courses given prerequisites, or `[]` if impossible (cycle).

```python
def find_order(num_courses, prerequisites):
    graph = {i: [] for i in range(num_courses)}
    for course, pre in prerequisites:
        graph[pre].append(course)        # pre -> course

    state = [0] * num_courses            # 0=unseen, 1=visiting, 2=done
    order = []
    ok = True

    def dfs(node):
        nonlocal ok
        state[node] = 1
        for nxt in graph[node]:
            if state[nxt] == 1:          # back-edge -> cycle
                ok = False
                return
            if state[nxt] == 0:
                dfs(nxt)
        state[node] = 2
        order.append(node)               # postorder = reverse topo order

    for c in range(num_courses):
        if state[c] == 0:
            dfs(c)
    return order[::-1] if ok else []

# find_order(2, [[1, 0]]) -> [0, 1]
```

### Complexity
- **`O(V + E)`** time, **`O(V)`** space (visited + recursion stack).

### ⚠️ Watch out
- **Disconnected graph:** a single `dfs(start)` won't visit all nodes — loop over all nodes and start DFS from unvisited ones.
- **Self-loops:** `if nxt not in visited` handles them, but forgetting `visited.add(node)` *before* exploring neighbors causes infinite recursion.
- **Recursion depth:** Python's default limit is ~1000 — for large graphs, use `sys.setrecursionlimit()` or switch to iterative DFS with a stack.
- **Topological sort cycle detection:** use a 3-state coloring (unseen/visiting/done) — a back-edge to a "visiting" node = cycle.

### Practice
- Clone Graph (133), Path Sum II (113), Course Schedule II (210).

---

## 12. Breadth-First Search (BFS)

> **Mnemonic:** *"Ripples in a pond — nearest first, level by level."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second serene top-down shot of a still dark pond at dawn. A single water drop hits the exact center; concentric glowing ripples expand outward ring by ring. Each ring lights up a circle of nodes at that distance, nearest first, level by level. Bold text overlay: "Ripples — nearest first, level by level." Calm, reflective, soft blue light.
```

### Picture
A queue processes everything at distance `d` before distance `d+1` → first time you
reach a node is via the **shortest path** (unweighted).

```
        A          level 0: A
       / \         level 1: B C
      B   C        level 2: D E
     / \
    D   E
queue: [A] -> [B,C] -> [C,D,E] -> ...
```

### When to use
- **Shortest path in unweighted** graphs; level-order tree traversal; "minimum steps".

### Template
```python
from collections import deque

def bfs_levels(root):
    if not root:
        return []
    res = []
    q = deque([root])
    while q:
        level = []
        for _ in range(len(q)):          # snapshot: process exactly this level
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        res.append(level)
    return res
```

### Worked example — Rotting Oranges (LeetCode 994)
Multi-source BFS: all rotten oranges spread simultaneously; count minutes.

```python
from collections import deque

def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    q = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                q.append((r, c))         # all initial sources
            elif grid[r][c] == 1:
                fresh += 1

    minutes = 0
    while q and fresh:
        minutes += 1
        for _ in range(len(q)):          # one minute = one level
            r, c = q.popleft()
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    q.append((nr, nc))
    return -1 if fresh else minutes

# oranges_rotting([[2,1,1],[1,1,0],[0,1,1]]) -> 4
```

### Complexity
- **`O(V + E)`** (grid: `O(m·n)`) time, **`O(V)`** space for the queue.

### ⚠️ Watch out
- **Source = destination:** return `0` (zero steps), not `-1` — a common off-by-one.
- **Disconnected components:** if the target is unreachable, BFS exhausts the queue — return `-1`.
- **Single-node graph:** BFS returns immediately with `[root]` — verify.
- **Forgetting `visited` at enqueue time:** if you mark visited only at *dequeue*, you'll enqueue duplicates and waste memory (or TLE).

### Practice
- Binary Tree Level Order (102), Rotting Oranges (994), Word Ladder (127).

---

## 13. Matrix Traversal

> **Mnemonic:** *"A grid is just a graph — each cell has 4 neighbors."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second 3D animation, top-down on a glowing square grid of cells. One cell pulses and shoots four connecting beams to its up, down, left, and right neighbors, revealing the grid as a node-and-edge graph network. A connected cluster of cells then lights up together as one "island." Bold text overlay: "A grid is just a graph — each cell has 4 neighbors." Techy neon-on-dark, clean.
```

### Picture
Flood fill / island counting = DFS or BFS where moves are up/down/left/right.

```
grid (1 = land):           visit (r,c) -> 4 neighbors
1 1 0                      (r-1,c) up
1 1 0       directions =   (r+1,c) down
0 0 1       [(-1,0),(1,0), (r,c-1) left
            (0,-1),(0,1)]  (r,c+1) right
```

### When to use
- Islands, flood fill, regions, shortest path on a grid, surrounded regions.

### Template — DFS flood fill
```python
def flood_fill(image, sr, sc, new_color):
    rows, cols = len(image), len(image[0])
    start = image[sr][sc]
    if start == new_color:
        return image                     # avoid infinite recursion
    def dfs(r, c):
        if 0 <= r < rows and 0 <= c < cols and image[r][c] == start:
            image[r][c] = new_color
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                dfs(r + dr, c + dc)
    dfs(sr, sc)
    return image

# flood_fill([[1,1,1],[1,1,0],[1,0,1]], 1, 1, 2) -> [[2,2,2],[2,2,0],[2,0,1]]
```

### Worked example — Number of Islands (LeetCode 200)
```python
def num_islands(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    count = 0
    def sink(r, c):
        if 0 <= r < rows and 0 <= c < cols and grid[r][c] == "1":
            grid[r][c] = "0"             # mark visited by sinking
            sink(r + 1, c); sink(r - 1, c)
            sink(r, c + 1); sink(r, c - 1)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                sink(r, c)               # remove the whole island
    return count

# num_islands([["1","1","0"],["1","1","0"],["0","0","1"]]) -> 2
```

### Complexity
- **`O(m·n)`** time, **`O(m·n)`** space (recursion / visited worst case).

### ⚠️ Watch out
- **Empty grid (0 rows or 0 cols):** guard with `if not grid or not grid[0]: return 0`.
- **Single cell:** the answer might be 1 island — make sure you still count it.
- **Modifying the grid as visited:** `grid[r][c] = "0"` works but mutates the input — if the problem says "don't modify", use a separate `visited` set.
- **Stack overflow on large grids:** `200 × 200` = 40,000 recursive calls — consider iterative BFS/DFS for safety.

### Practice
- Flood Fill (733), Number of Islands (200), Surrounded Regions (130).

---

## 14. Backtracking

> **Mnemonic:** *"Choose → Explore → Un-choose."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second 3D animation of a branching decision tree made of glowing paths. A bright token picks one branch (it lights up — "CHOOSE"), travels down to a leaf ("EXPLORE"), then rewinds back up the branch, un-lighting it ("UN-CHOOSE"), and takes a different branch. Loop the choose-explore-undo rhythm. Bold text overlay: "Choose -> Explore -> Un-choose." Elegant, glowing, rhythmic.
```

### Picture
A decision tree. At each node you make a choice, recurse, then **undo** it to try the next.

```
permutations of [1,2,3]
                ( )
        1/       2|       3\
      (1)        (2)        (3)
     2/ 3\      1/ 3\      1/ 2\
   (12)(13)   (21)(23)   (31)(32)
    |3  |2     |3  |1     |2  |1
  123 132    213 231    312 321
```

### When to use
- Generate **all** permutations / combinations / subsets / partitions; constraint
  puzzles (N-Queens, Sudoku, word search).

### Template
```python
def backtrack(choices):
    res = []
    path = []
    def explore(remaining):
        if not remaining:                # base case: a complete solution
            res.append(path[:])          # copy the path
            return
        for i, choice in enumerate(remaining):
            path.append(choice)                          # choose
            explore(remaining[:i] + remaining[i+1:])     # explore
            path.pop()                                   # un-choose
    explore(choices)
    return res
```

### Worked example — Subsets (LeetCode 78)
Every element is either in or out; recurse on the index.

```python
def subsets(nums):
    res = []
    path = []
    def explore(start):
        res.append(path[:])              # every node is a valid subset
        for i in range(start, len(nums)):
            path.append(nums[i])         # choose nums[i]
            explore(i + 1)               # explore with later elements
            path.pop()                   # un-choose
    explore(0)
    return res

# subsets([1, 2, 3]) -> [[],[1],[1,2],[1,2,3],[1,3],[2],[2,3],[3]]
```

### Complexity
- Permutations **`O(n·n!)`**, Subsets **`O(n·2^n)`**, general **`O(branch^depth)`**;
  space **`O(depth)`** for recursion (plus output).

### ⚠️ Watch out
- **Empty input:** `backtrack([])` should return `[[]]` (one empty subset) or `[]` (no permutations) — know the difference.
- **Duplicates producing duplicate results:** sort the input and skip `if i > start and nums[i] == nums[i-1]` in subsets/combinations.
- **Forgetting to copy `path`:** `res.append(path[:])` — if you append `path` directly, all entries share the same mutable list.
- **Pruning:** without early termination (e.g., sum exceeds target), backtracking can be extremely slow — always prune where possible.

### Practice
- Permutations (46), Subsets (78), N-Queens (51).

---

## 15. Bridge to Dynamic Programming

> **Mnemonic:** *"Backtracking that remembers = DP."*

**8-second memory video** — copy into your AI video generator:
```prompt
8-second split-concept 3D animation. Left: an explorer token in a tree wearily re-walks the same identical branches again and again (wasted, repetitive). Then a glowing memory notebook appears and stamps each solved branch "CACHED"; on the right the same tree now collapses fast as repeated branches are skipped instantly. Bold text overlay: "Backtracking that remembers = DP." Satisfying speed-up, glowing cache stamps.
```

Backtracking explores **all** paths. When those paths **overlap** (you recompute the
same subproblem) and the problem has **optimal substructure** (best answer built from
best sub-answers), cache the results → that's **Dynamic Programming**.

```
Naive Fibonacci recursion (overlapping subproblems!):
                fib(5)
              /        \
          fib(4)       fib(3)
         /     \       /    \
     fib(3)  fib(2) fib(2) fib(1)     <- fib(3), fib(2) recomputed
     ...

Add a cache -> each subproblem solved once -> O(n) instead of O(2^n).
```

```python
from functools import lru_cache

@lru_cache(maxsize=None)                 # memoization turns O(2^n) into O(n)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

**The two questions that unlock every DP problem:**
1. **What is the state?** (the minimal info that defines a subproblem, e.g. `dp[i]`, `dp[i][j]`)
2. **What is the transition/recurrence?** (how a state is built from smaller states)

### ⚠️ Watch out
- **Forgetting base cases:** every DP solution needs at least one base case — `dp[0]`, `dp[0][0]`, etc.
- **Off-by-one in state definition:** is `dp[i]` "first i items" or "item at index i"? Be precise.
- **Memoization dict vs array:** `@lru_cache` is convenient but slower than a hand-rolled array for large states — switch to bottom-up if you hit TLE.
- **Not recognizing overlapping subproblems:** if the recursion tree has no repeated nodes, DP doesn't help — it's just recursion.

Continue to the 20 DP patterns → [`02-dynamic-programming.md`](./02-dynamic-programming.md).
