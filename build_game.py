#!/usr/bin/env python3
"""
Build "Pattern Forge" — an offline, mobile-first puzzle game that gamifies
memorizing the DSA templates, examples, complexities, mnemonics and recurrences.

Run:
    python3 build_game.py

Output:
    game/index.html  +  game/assets/{game.css, game.js, game-data.js}

The Python code (template + worked-example snippets and mnemonics) is pulled
straight out of the Markdown study guide so the game never drifts from the
source of truth. The lighter facts (clue / complexity / recurrence / which
patterns are "confusable") live in the curated REGISTRY below.

Re-run this whenever you edit the .md files to refresh the game data.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
GAME = HERE / "site" / "game"   # lives inside the site so it's a "full game mode" tab
ASSETS = GAME / "assets"

# ---------------------------------------------------------------------------
# Curated registry: the lightweight, hand-authored facts per pattern.
# Code + mnemonics are auto-extracted from the markdown (see parse helpers).
#   id        : stable slug used by the game
#   name      : display name
#   cat        : 'core' | 'dp' | 'advanced'
#   file      : which markdown file the section lives in
#   section   : substring that uniquely identifies the "## ..." heading
#   clue      : the "trigger" a problem gives you (Deck A flavour)
#   time/space: complexity (Deck B)
#   rec       : the one-line recurrence (DP only, Deck C); optional
#   confus    : ids of confusable patterns (good wrong-answer distractors)
# ---------------------------------------------------------------------------
CORE = "01-core-patterns.md"
DP = "02-dynamic-programming.md"
ADV = "04-advanced-patterns.md"

REGISTRY = [
    dict(id="prefix-sum", name="Prefix Sum", cat="core", file=CORE, section="Prefix Sum",
         clue="Many range-sum queries on a fixed array", time="O(n)", space="O(n)",
         confus=["sliding-window", "two-pointers", "kadane"]),
    dict(id="two-pointers", name="Two Pointers", cat="core", file=CORE, section="Two Pointers",
         clue="Sorted array — find a pair/triplet meeting a condition", time="O(n)", space="O(1)",
         confus=["sliding-window", "binary-search", "prefix-sum"]),
    dict(id="sliding-window", name="Sliding Window", cat="core", file=CORE, section="Sliding Window",
         clue="Longest / shortest CONTIGUOUS subarray or substring", time="O(n)", space="O(k)",
         confus=["two-pointers", "prefix-sum", "kadane"]),
    dict(id="fast-slow", name="Fast & Slow Pointers", cat="core", file=CORE, section="Fast & Slow Pointers",
         clue="Detect a cycle in a linked list / find the middle node", time="O(n)", space="O(1)",
         confus=["ll-reversal", "two-pointers", "binary-search"]),
    dict(id="ll-reversal", name="LinkedList In-place Reversal", cat="core", file=CORE, section="LinkedList In-place Reversal",
         clue="Reverse a list (or sublist) using O(1) extra space", time="O(n)", space="O(1)",
         confus=["fast-slow", "two-pointers", "tree-traversal"]),
    dict(id="monotonic-stack", name="Monotonic Stack", cat="core", file=CORE, section="Monotonic Stack",
         clue="Next greater / next smaller element", time="O(n)", space="O(n)",
         confus=["top-k", "sliding-window", "binary-search"]),
    dict(id="top-k", name="Top K Elements (Heap)", cat="core", file=CORE, section="Top 'K' Elements (Heap)",
         clue="K largest / smallest / most frequent", time="O(n log k)", space="O(k)",
         confus=["monotonic-stack", "binary-search", "intervals"]),
    dict(id="intervals", name="Overlapping Intervals", cat="core", file=CORE, section="Overlapping Intervals",
         clue="Merge / insert / schedule overlapping ranges", time="O(n log n)", space="O(n)",
         confus=["two-pointers", "binary-search", "top-k"]),
    dict(id="binary-search", name="Modified Binary Search", cat="core", file=CORE, section="Modified Binary Search",
         clue="Sorted or rotated array — find target / boundary / peak", time="O(log n)", space="O(1)",
         confus=["two-pointers", "intervals", "lis"]),
    dict(id="tree-traversal", name="Binary Tree Traversal", cat="core", file=CORE, section="Binary Tree Traversal",
         clue="Pre / In / Post order — sorted output from a BST (inorder)", time="O(n)", space="O(h)",
         confus=["dfs", "bfs", "tree-dp"]),
    dict(id="dfs", name="Depth-First Search (DFS)", cat="core", file=CORE, section="Depth-First Search (DFS)",
         clue="Enumerate paths / detect cycle / topological sort", time="O(V + E)", space="O(V)",
         confus=["bfs", "backtracking", "matrix"]),
    dict(id="bfs", name="Breadth-First Search (BFS)", cat="core", file=CORE, section="Breadth-First Search (BFS)",
         clue="Fewest steps / shortest path in an UNWEIGHTED graph", time="O(V + E)", space="O(V)",
         confus=["dfs", "dijkstra", "matrix"]),
    dict(id="matrix", name="Matrix Traversal", cat="core", file=CORE, section="Matrix Traversal",
         clue="Islands / flood fill / regions on a grid", time="O(m·n)", space="O(m·n)",
         confus=["dfs", "bfs", "grid-dp"]),
    dict(id="backtracking", name="Backtracking", cat="core", file=CORE, section="Backtracking",
         clue="Generate ALL permutations / combinations / subsets", time="O(branch^depth)", space="O(depth)",
         confus=["dfs", "dp-bridge", "bitmask-dp"]),
    dict(id="dp-bridge", name="Bridge to Dynamic Programming", cat="core", file=CORE, section="Bridge to Dynamic Programming",
         clue="Overlapping subproblems + optimal substructure → cache it", time="O(n)", space="O(n)",
         rec="dp[i] = f(smaller dp[...])", confus=["backtracking", "fibonacci", "dfs"]),

    dict(id="fibonacci", name="Fibonacci / 1-D DP", cat="dp", file=DP, section="Fibonacci Sequence",
         clue="Sequence where today = sum of the previous few", time="O(n)", space="O(1)",
         rec="dp[i] = dp[i-1] + dp[i-2]", confus=["count-ways", "kadane", "dp-bridge"]),
    dict(id="kadane", name="Kadane's Algorithm", cat="dp", file=DP, section="Kadane's Algorithm",
         clue="Maximum / minimum contiguous subarray run", time="O(n)", space="O(1)",
         rec="cur = max(x, cur + x); best = max(best, cur)", confus=["sliding-window", "prefix-sum", "fibonacci"]),
    dict(id="knapsack-01", name="0/1 Knapsack", cat="dp", file=DP, section="0/1 Knapsack",
         clue="Pick items under a capacity limit — each item once", time="O(n·W)", space="O(W)",
         rec="dp[w] = max(dp[w], dp[w-wt] + val)  — capacity DOWNWARD", confus=["unbounded-knapsack", "subset-sum", "count-ways"]),
    dict(id="unbounded-knapsack", name="Unbounded Knapsack", cat="dp", file=DP, section="Unbounded Knapsack",
         clue="Pick items under a capacity limit — items reusable", time="O(n·W)", space="O(W)",
         rec="dp[w] = max/min(dp[w], dp[w-wt] + val)  — capacity UPWARD", confus=["knapsack-01", "subset-sum", "count-ways"]),
    dict(id="lcs", name="Longest Common Subsequence", cat="dp", file=DP, section="Longest Common Subsequence (LCS)",
         clue="Two strings — align them / longest shared subsequence", time="O(n·m)", space="O(n·m)",
         rec="match: dp[i-1][j-1]+1; else max(dp[i-1][j], dp[i][j-1])", confus=["edit-distance", "palindrome-subseq", "lis"]),
    dict(id="lis", name="Longest Increasing Subsequence", cat="dp", file=DP, section="Longest Increasing Subsequence (LIS)",
         clue="One sequence — longest strictly increasing run", time="O(n log n)", space="O(n)",
         rec="patience: replace first tail >= x, else append", confus=["lcs", "binary-search", "kadane"]),
    dict(id="palindrome-subseq", name="Palindromic Subsequence", cat="dp", file=DP, section="Palindromic Subsequence",
         clue="Palindrome problem over a substring i..j", time="O(n²)", space="O(n²)",
         rec="ends ==: dp[i+1][j-1]+2; else max(dp[i+1][j], dp[i][j-1])", confus=["lcs", "edit-distance", "matrix-chain"]),
    dict(id="edit-distance", name="Edit Distance", cat="dp", file=DP, section="Edit Distance",
         clue="Two strings — fewest insert/delete/replace to transform", time="O(n·m)", space="O(n·m)",
         rec="match: dp[i-1][j-1]; else 1 + min(3 neighbours)", confus=["lcs", "palindrome-subseq", "string-partition"]),
    dict(id="subset-sum", name="Subset Sum", cat="dp", file=DP, section="Subset Sum",
         clue="Can a subset of numbers hit an exact target?", time="O(n·target)", space="O(target)",
         rec="dp[s] = dp[s] or dp[s-x]", confus=["knapsack-01", "count-ways", "unbounded-knapsack"]),
    dict(id="string-partition", name="String Partition", cat="dp", file=DP, section="String Partition",
         clue="Split a string into valid pieces (word break)", time="O(n²)", space="O(n)",
         rec="dp[i] = any(dp[j] and s[j:i] valid)", confus=["edit-distance", "count-ways", "matrix-chain"]),
    dict(id="catalan", name="Catalan Numbers", cat="dp", file=DP, section="Catalan Numbers",
         clue="Count BSTs / balanced parenthesizations", time="O(n²)", space="O(n)",
         rec="dp[n] = Σ dp[i-1]·dp[n-i]", confus=["count-ways", "fibonacci", "matrix-chain"]),
    dict(id="matrix-chain", name="Matrix Chain (Interval DP)", cat="dp", file=DP, section="Matrix Chain Multiplication",
         clue="Best split of an interval, combine the two halves", time="O(n³)", space="O(n²)",
         rec="dp[i][j] = min over k (dp[i][k]+dp[k+1][j]+cost)", confus=["palindrome-subseq", "catalan", "string-partition"]),
    dict(id="count-ways", name="Count Distinct Ways", cat="dp", file=DP, section="Count Distinct Ways",
         clue="Count the NUMBER OF WAYS to reach a state", time="O(n)", space="O(1)",
         rec="dp[i] += dp[i-1] (1-digit) + dp[i-2] (2-digit)", confus=["fibonacci", "subset-sum", "catalan"]),
    dict(id="grid-dp", name="DP on Grids", cat="dp", file=DP, section="DP on Grids",
         clue="Best path / cost on a 2D grid (right/down moves)", time="O(m·n)", space="O(n)",
         rec="dp[r][c] = grid[r][c] + min/sum(dp[r-1][c], dp[r][c-1])", confus=["matrix", "lcs", "edit-distance"]),
    dict(id="tree-dp", name="DP on Trees", cat="dp", file=DP, section="DP on Trees",
         clue="Aggregate over a tree, children → parent (post-order)", time="O(n)", space="O(h)",
         rec="rob = val + skip(children); skip = max(child states)", confus=["tree-traversal", "dfs", "graph-dp"]),
    dict(id="graph-dp", name="DP on Graphs", cat="dp", file=DP, section="DP on Graphs",
         clue="Optimal cost over edges with bounded steps", time="O(K·E)", space="O(V)",
         rec="dist[v] = min(dist[v], snapshot[u] + w)", confus=["dijkstra", "bfs", "tree-dp"]),
    dict(id="digit-dp", name="Digit DP", cat="dp", file=DP, section="Digit DP",
         clue="Count numbers in [0..N] with a digit property", time="O(digits·states)", space="O(digits·states)",
         rec="dp(pos, tight, ...) → sum over digits 0..hi", confus=["bitmask-dp", "count-ways", "probability-dp"]),
    dict(id="bitmask-dp", name="Bitmask DP", cat="dp", file=DP, section="Bitmask DP",
         clue="Small n (≤20) — the chosen SET is the state", time="O(2^n·n)", space="O(2^n)",
         rec="dp[mask|bit][j] = min(dp[mask][i] + cost)", confus=["backtracking", "digit-dp", "subset-sum"]),
    dict(id="probability-dp", name="Probability DP", cat="dp", file=DP, section="Probability DP",
         clue="Expected value / survival probability over steps", time="O(states)", space="O(states)",
         rec="dp[state] = Σ parent_prob × transition_prob", confus=["count-ways", "digit-dp", "state-machine-dp"]),
    dict(id="state-machine-dp", name="State Machine DP", cat="dp", file=DP, section="State Machine DP",
         clue="A few discrete modes with transitions (buy/sell/hold)", time="O(n)", space="O(1)",
         rec="sold=hold+p; hold=max(hold,rest-p); rest=max(rest,prev_sold)", confus=["kadane", "fibonacci", "probability-dp"]),

    dict(id="dijkstra", name="Dijkstra's Algorithm", cat="advanced", file=ADV, section="Dijkstra's Algorithm",
         clue="Shortest path — weighted graph, non-negative edges", time="O((V+E) log V)", space="O(V+E)",
         confus=["bfs", "graph-dp", "top-k"]),
    dict(id="union-find", name="Union-Find (DSU)", cat="advanced", file=ADV, section="Union-Find (Disjoint Set Union)",
         clue="Are X and Y connected? / merge groups dynamically", time="O(α(n))", space="O(n)",
         confus=["dfs", "bfs", "graph-dp"]),
]


# ---------------------------------------------------------------------------
# Markdown parsing helpers
# ---------------------------------------------------------------------------
def split_sections(text):
    """Return list of (heading_text, body) for every '## ' section."""
    parts = re.split(r'(?m)^##\s+(.+?)\s*$', text)
    # parts = [pre, head1, body1, head2, body2, ...]
    out = []
    for i in range(1, len(parts), 2):
        out.append((parts[i].strip(), parts[i + 1]))
    return out


def find_section_body(sections, needle):
    needle_l = needle.lower()
    for head, body in sections:
        if needle_l in head.lower():
            return body
    return None


def extract_code_blocks(body):
    """Return list of (subheading, lang, code) python/code blocks in order."""
    blocks = []
    current_sub = ""
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        sub = re.match(r'^###\s+(.+?)\s*$', line)
        if sub:
            current_sub = sub.group(1)
            i += 1
            continue
        fence = re.match(r'^```(\w*)\s*$', line)
        if fence:
            lang = fence.group(1)
            code_lines = []
            i += 1
            while i < len(lines) and not re.match(r'^```\s*$', lines[i]):
                code_lines.append(lines[i])
                i += 1
            blocks.append((current_sub, lang, "\n".join(code_lines)))
        i += 1
    return blocks


def clean_code(code):
    """Drop trailing result-comment lines + blank lines; return list of lines."""
    lines = code.split("\n")
    cleaned = []
    for ln in lines:
        if ln.strip() == "":
            continue  # remove blank lines (logic-irrelevant for the puzzle)
        # drop demo lines like "# func(...) -> 9"
        if ln.strip().startswith("#") and "->" in ln:
            continue
        cleaned.append(ln.rstrip())
    return cleaned


def pick_template(blocks):
    """First python block under a 'Template' or 'Code' subheading; else first python block."""
    for sub, lang, code in blocks:
        if lang == "python" and ("template" in sub.lower() or sub.lower().startswith("code")):
            return code
    for sub, lang, code in blocks:
        if lang == "python":
            return code
    return None


def pick_example(blocks):
    for sub, lang, code in blocks:
        if lang == "python" and "worked example" in sub.lower():
            return code
    return None


def extract_mnemonic(body):
    m = re.search(r'\*\*Mnemonic:\*\*\s*\*"(.+?)"\*', body)
    return m.group(1).strip() if m else ""


def build_patterns():
    cache = {}
    patterns = []
    for entry in REGISTRY:
        fname = entry["file"]
        if fname not in cache:
            cache[fname] = split_sections((HERE / fname).read_text(encoding="utf-8"))
        sections = cache[fname]
        body = find_section_body(sections, entry["section"])
        if body is None:
            raise SystemExit(f"!! Could not find section '{entry['section']}' in {fname}")
        blocks = extract_code_blocks(body)
        template = pick_template(blocks)
        example = pick_example(blocks)
        patterns.append({
            "id": entry["id"],
            "name": entry["name"],
            "cat": entry["cat"],
            "clue": entry["clue"],
            "time": entry["time"],
            "space": entry["space"],
            "rec": entry.get("rec", ""),
            "mnemonic": extract_mnemonic(body),
            "confus": entry.get("confus", []),
            "template": clean_code(template) if template else None,
            "example": clean_code(example) if example else None,
        })
    return patterns


GAME_CSS = r""":root{
  --bg:#0d1117; --bg2:#161b22; --panel:#10151c; --card:#161b22;
  --text:#c9d1d9; --dim:#8b949e; --head:#f0f6fc; --border:#2a3038;
  --accent:#a371f7; --accent2:#f778ba; --accent3:#ffa657;
  --good:#3fb950; --good2:#2ea043; --bad:#f85149; --warn:#d29922;
  --code:#0b0f14; --chip:#1b222c; --shadow:rgba(0,0,0,.45);
  --grad:linear-gradient(135deg,#a371f7 0%,#f778ba 55%,#ffa657 100%);
}
html[data-theme="light"]{
  --bg:#f3f1fa; --bg2:#ffffff; --panel:#ffffff; --card:#ffffff;
  --text:#1f2328; --dim:#656d76; --head:#161b22; --border:#e2dcf0;
  --accent:#8250df; --accent2:#bf3989; --accent3:#bc4c00;
  --good:#1a7f37; --good2:#1a7f37; --bad:#cf222e; --warn:#9a6700;
  --code:#f6f8fa; --chip:#efeafc; --shadow:rgba(110,90,160,.18);
  --grad:linear-gradient(135deg,#8250df 0%,#bf3989 55%,#bc4c00 100%);
}
*{box-sizing:border-box; -webkit-tap-highlight-color:transparent}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--bg); color:var(--text); overflow-x:hidden;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  font-size:16px; line-height:1.5; padding-bottom:env(safe-area-inset-bottom);
}
code,pre,.mono{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace}
button{font-family:inherit}

/* top bar */
.pf-top{
  position:sticky; top:0; z-index:50; display:flex; align-items:center; gap:10px;
  height:56px; padding:0 12px; background:var(--panel);
  border-bottom:1px solid var(--border); box-shadow:0 1px 0 var(--shadow);
  padding-top:env(safe-area-inset-top);
}
.pf-brand{display:flex; align-items:center; gap:8px; text-decoration:none; color:var(--head); font-weight:800}
.pf-mark{font-family:monospace; font-weight:900; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; font-size:20px}
.pf-brandtxt{font-size:16px; letter-spacing:.2px}
.pf-rank{
  font-size:12px; font-weight:700; color:var(--head); padding:5px 10px; border-radius:999px;
  background:var(--chip); border:1px solid var(--border); white-space:nowrap;
}
.pf-spacer{flex:1}
.pf-icon{
  width:40px; height:40px; border-radius:10px; border:1px solid var(--border);
  background:transparent; color:var(--text); font-size:18px; cursor:pointer; line-height:1;
}
.pf-icon:hover{border-color:var(--accent)}
.pf-icon.off{opacity:.38}
@media (max-width:420px){ .pf-brandtxt{display:none} }

.screen{max-width:780px; margin:0 auto; padding:18px 14px 90px}
.hidden{display:none !important}

/* ---------- home ---------- */
.hero{text-align:center; padding:14px 6px 6px}
.hero h1{font-size:clamp(28px,7vw,44px); margin:.1em 0; line-height:1.05; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent}
.hero p{color:var(--dim); margin:.3em auto; max-width:520px; font-size:15px}
.statbar{display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin:16px 0 4px}
.stat{background:var(--card); border:1px solid var(--border); border-radius:14px; padding:10px 16px; min-width:88px; text-align:center; box-shadow:0 2px 10px var(--shadow)}
.stat b{display:block; font-size:22px; color:var(--head); font-variant-numeric:tabular-nums}
.stat span{font-size:11px; color:var(--dim); text-transform:uppercase; letter-spacing:.06em}

.section-label{font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:var(--dim); margin:22px 4px 10px; font-weight:700}
.scope{display:flex; gap:8px; flex-wrap:wrap}
.scope button{
  flex:1 1 auto; padding:9px 12px; border-radius:999px; border:1px solid var(--border);
  background:var(--card); color:var(--text); font-weight:600; font-size:14px; cursor:pointer;
}
.scope button.active{background:var(--grad); color:#fff; border-color:transparent; box-shadow:0 4px 14px var(--shadow)}

.modes{display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:12px}
.mode-card{
  text-align:left; background:var(--card); border:1px solid var(--border); border-radius:16px;
  padding:14px; cursor:pointer; transition:transform .08s ease, border-color .15s; position:relative; overflow:hidden;
}
.mode-card:hover{border-color:var(--accent); transform:translateY(-2px)}
.mode-card:active{transform:translateY(0) scale(.99)}
.mode-card .emoji{font-size:26px}
.mode-card h3{margin:6px 0 4px; font-size:16px; color:var(--head)}
.mode-card p{margin:0; font-size:12.5px; color:var(--dim); line-height:1.4}
.mode-card.boss{border-color:var(--accent2); background:linear-gradient(160deg,var(--card),rgba(247,120,186,.10))}
.mode-card.boss::after{content:"3 LIVES"; position:absolute; top:10px; right:10px; font-size:9px; font-weight:800; letter-spacing:.1em; color:var(--accent2); border:1px solid var(--accent2); border-radius:6px; padding:2px 5px}

/* mastery grid */
.mastery{display:grid; grid-template-columns:repeat(auto-fill,minmax(112px,1fr)); gap:8px}
.mtile{background:var(--card); border:1px solid var(--border); border-radius:12px; padding:9px 10px}
.mtile .mn{font-size:12px; color:var(--head); font-weight:600; line-height:1.25; min-height:30px}
.mtile .ms{font-size:13px; letter-spacing:1px; margin-top:4px}
.mtile .cat{font-size:9px; text-transform:uppercase; letter-spacing:.08em; color:var(--dim)}
.star-on{color:var(--accent3)} .star-off{color:var(--border)}

.howto{background:var(--card); border:1px solid var(--border); border-radius:14px; padding:12px 16px; color:var(--dim); font-size:13.5px}
.howto b{color:var(--text)}

.focus-banner{display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin:6px 0 2px; padding:11px 14px;
  border-radius:14px; border:1px solid var(--accent); background:rgba(163,113,247,.12); color:var(--head); font-size:15px}
.focus-banner b{color:var(--accent)}
.focus-exit{margin-left:auto; background:transparent; border:1px solid var(--border); color:var(--text);
  border-radius:999px; padding:6px 12px; font-weight:600; font-size:13px; cursor:pointer}
.focus-exit:hover{border-color:var(--accent)}

/* ---------- game ---------- */
.hud{display:flex; align-items:center; gap:8px; margin-bottom:10px; flex-wrap:wrap}
.hud .btn-back{padding:8px 12px; border-radius:10px; border:1px solid var(--border); background:var(--card); color:var(--text); cursor:pointer; font-weight:600}
.hud .hud-score{font-weight:800; color:var(--head); font-size:20px; font-variant-numeric:tabular-nums}
.hud .hud-score small{font-size:11px; color:var(--dim); font-weight:600; display:block; line-height:1; text-transform:uppercase; letter-spacing:.05em}
.hud .streak{font-weight:700; color:var(--accent3)}
.hud .lives{margin-left:auto; font-size:18px; letter-spacing:2px}
.hud .qcount{margin-left:auto; color:var(--dim); font-weight:600; font-size:13px}
.combo-flag{display:inline-block; padding:3px 8px; border-radius:999px; background:var(--grad); color:#fff; font-weight:800; font-size:12px}

.timer-wrap{height:8px; border-radius:999px; background:var(--chip); overflow:hidden; margin-bottom:14px}
.timer-bar{height:100%; width:100%; background:var(--grad); transition:width .12s linear}
.timer-bar.warn{background:linear-gradient(90deg,var(--warn),var(--bad))}

.qcard{background:var(--card); border:1px solid var(--border); border-radius:18px; padding:16px; box-shadow:0 6px 24px var(--shadow); animation:pop .22s ease}
.qmode{font-size:11px; text-transform:uppercase; letter-spacing:.1em; font-weight:800; color:var(--accent)}
.qinstr{margin:4px 0 12px; color:var(--dim); font-size:14px}
.qbig{font-size:clamp(18px,4.5vw,24px); font-weight:700; color:var(--head); margin:6px 0 14px; line-height:1.3}
.qclue{background:var(--code); border:1px dashed var(--border); border-left:4px solid var(--accent); border-radius:10px; padding:12px 14px; color:var(--text); font-size:16px; margin:6px 0 14px}

/* code rows */
.code-list{display:flex; flex-direction:column; gap:6px; margin:8px 0}
.code-row{
  display:flex; align-items:flex-start; gap:8px; width:100%; text-align:left; cursor:pointer;
  background:var(--code); border:1px solid var(--border); border-radius:10px; padding:9px 11px;
  color:var(--text); font-size:13px; white-space:pre; overflow-x:auto; transition:border-color .12s, background .12s; line-height:1.45;
}
.code-row .num{color:var(--dim); min-width:18px; text-align:right; user-select:none; font-size:12px}
.code-row .txt{white-space:pre}
.code-row:hover{border-color:var(--accent)}
.code-row.picked{border-color:var(--accent); background:rgba(163,113,247,.10)}
.code-row.correct{border-color:var(--good); background:rgba(63,185,80,.12)}
.code-row.wrong{border-color:var(--bad); background:rgba(248,81,73,.12)}
.code-row.shake{animation:shake .35s}
.empty-hint{color:var(--dim); font-size:13px; text-align:center; padding:14px; border:1px dashed var(--border); border-radius:10px}

.pool-label{font-size:12px; color:var(--dim); margin:14px 0 6px; font-weight:700; text-transform:uppercase; letter-spacing:.06em}

/* difficulty note under the selector */
.diff-note{color:var(--dim); font-size:13px; margin:8px 2px 2px}

/* token forge (Medium / Hard): chips of natural width, uniform height, wrapping into lines */
.forge-lines{display:flex; flex-direction:column; gap:6px; margin:8px 0; background:var(--code); border:1px solid var(--border); border-radius:12px; padding:12px 12px}
.forge-row{display:flex; flex-wrap:wrap; gap:6px; align-items:center; min-height:36px}
.tok-bank{display:flex; flex-wrap:wrap; gap:8px; margin:6px 0 2px; padding:12px; background:var(--code); border:1px dashed var(--border); border-radius:12px; min-height:52px}
.tok{
  display:inline-flex; align-items:center; justify-content:center; height:34px; padding:0 11px;
  border-radius:9px; border:1px solid var(--border); background:var(--bg2); color:var(--text);
  font-family:"SFMono-Regular",Consolas,Menlo,monospace; font-size:13.5px; line-height:1;
  cursor:pointer; white-space:pre; transition:border-color .12s, background .12s, transform .06s;
}
.tok:hover{border-color:var(--accent)}
.tok:active{transform:scale(.95)}
.tok.picked{border-color:var(--accent); background:rgba(163,113,247,.14)}
.tok.nl{min-width:34px; padding:0 8px; border-style:dashed; color:var(--dim); font-size:13px}
.tok.correct{border-color:var(--good); background:rgba(63,185,80,.16); color:var(--head)}
.tok.wrong{border-color:var(--bad); background:rgba(248,81,73,.16)}
.tok.shake{animation:shake .35s}
.tok-hint{color:var(--dim); font-size:13px; font-style:italic}

/* cloze code block */
.cloze{background:var(--code); border:1px solid var(--border); border-radius:12px; padding:14px; overflow-x:auto; font-size:13px; line-height:1.8; white-space:pre}
.blank{
  display:inline-block; min-width:46px; text-align:center; border:1px solid var(--accent); border-radius:7px;
  background:var(--bg2); color:var(--head); font-family:inherit; font-size:12.5px; padding:1px 6px; margin:0 1px; cursor:pointer;
}
.blank:focus{outline:2px solid var(--accent)}
.blank.ok{border-color:var(--good); background:rgba(63,185,80,.16)}
.blank.no{border-color:var(--bad); background:rgba(248,81,73,.16)}

/* option chips */
.opts{display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:14px}
.opts.one{grid-template-columns:1fr}
.opt{
  text-align:left; background:var(--bg2); border:1px solid var(--border); border-radius:12px; padding:13px 14px;
  color:var(--text); font-size:15px; cursor:pointer; transition:transform .07s, border-color .12s; line-height:1.35;
}
.opt:hover{border-color:var(--accent)}
.opt:active{transform:scale(.98)}
.opt.mono{font-family:"SFMono-Regular",Consolas,Menlo,monospace; font-size:13.5px; white-space:pre-wrap}
.opt.correct{border-color:var(--good); background:rgba(63,185,80,.16); color:var(--head)}
.opt.wrong{border-color:var(--bad); background:rgba(248,81,73,.16)}
.opt.disabled{pointer-events:none; opacity:.65}

/* action buttons */
.actions{display:flex; gap:10px; margin-top:16px; flex-wrap:wrap}
.btn{flex:1 1 120px; padding:14px; border-radius:12px; border:1px solid var(--border); background:var(--card); color:var(--text); font-weight:700; font-size:15px; cursor:pointer}
.btn:active{transform:scale(.99)}
.btn-primary{background:var(--grad); color:#fff; border-color:transparent; box-shadow:0 4px 16px var(--shadow)}
.btn-ghost{flex:0 0 auto}
.btn[disabled]{opacity:.45; pointer-events:none}

/* feedback */
.feedback{margin-top:14px; border-radius:14px; padding:13px 15px; border:1px solid var(--border); animation:pop .2s ease}
.feedback.good{background:rgba(63,185,80,.12); border-color:var(--good)}
.feedback.bad{background:rgba(248,81,73,.10); border-color:var(--bad)}
.feedback .fb-head{font-weight:800; font-size:16px; display:flex; align-items:center; gap:8px}
.feedback.good .fb-head{color:var(--good)}
.feedback.bad .fb-head{color:var(--bad)}
.feedback .fb-body{margin-top:6px; font-size:13.5px; color:var(--text)}
.feedback .fb-body code{background:var(--code); border:1px solid var(--border); padding:1px 5px; border-radius:5px; font-size:12.5px}
.points{margin-left:auto; font-weight:800; color:var(--accent3)}

/* ---------- summary ---------- */
.sum-wrap{text-align:center; padding-top:10px}
.sum-wrap h2{font-size:30px; margin:.2em 0; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent}
.sum-score{font-size:54px; font-weight:900; color:var(--head); font-variant-numeric:tabular-nums; line-height:1.1}
.sum-grid{display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin:16px 0}
.sum-grid .stat b{font-size:20px}
.new-best{display:inline-block; margin-top:6px; padding:5px 12px; border-radius:999px; background:var(--grad); color:#fff; font-weight:800; font-size:13px; animation:heartbeat 1s ease infinite}

#fx{position:fixed; inset:0; width:100%; height:100%; pointer-events:none; z-index:60}

/* animations */
@keyframes pop{from{transform:scale(.96); opacity:0} to{transform:scale(1); opacity:1}}
@keyframes shake{0%,100%{transform:translateX(0)} 20%{transform:translateX(-7px)} 40%{transform:translateX(6px)} 60%{transform:translateX(-4px)} 80%{transform:translateX(3px)}}
@keyframes heartbeat{0%,100%{transform:scale(1)} 50%{transform:scale(1.08)}}
@keyframes floatup{from{transform:translateY(0); opacity:1} to{transform:translateY(-40px); opacity:0}}
.floatpts{position:fixed; font-weight:900; font-size:22px; color:var(--accent3); pointer-events:none; z-index:61; animation:floatup .9s ease forwards}
@media (prefers-reduced-motion:reduce){*{animation:none !important; transition:none !important}}

@media (max-width:520px){
  .opts{grid-template-columns:1fr}
  .modes{grid-template-columns:1fr 1fr}
  .code-row{font-size:12px}
  .cloze{font-size:12px}
}
"""


GAME_JS = r'''(function(){
"use strict";

var PATTERNS = (window.GAME_DATA && window.GAME_DATA.patterns) || [];
var BY_ID = {};
PATTERNS.forEach(function(p){ BY_ID[p.id] = p; });

/* ============================ utils ============================ */
function $(sel, root){ return (root||document).querySelector(sel); }
function ce(tag, cls, html){ var e=document.createElement(tag); if(cls) e.className=cls; if(html!=null) e.innerHTML=html; return e; }
function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
function randInt(n){ return Math.floor(Math.random()*n); }
function choice(arr){ return arr[randInt(arr.length)]; }
function shuffle(arr){ var a=arr.slice(); for(var i=a.length-1;i>0;i--){ var j=randInt(i+1); var t=a[i]; a[i]=a[j]; a[j]=t; } return a; }
function uniq(arr){ var seen={}, out=[]; arr.forEach(function(x){ if(!seen[x]){ seen[x]=1; out.push(x); } }); return out; }
function sample(arr, n){ return shuffle(arr).slice(0, n); }

/* ============================ persistence ============================ */
var LS_KEY = "pf-save-v1";
var save = (function(){
  var d = { xp:0, high:0, bestStreak:0, mastery:{}, sound:true, haptics:true };
  try{ var raw=localStorage.getItem(LS_KEY); if(raw){ var p=JSON.parse(raw); for(var k in p) d[k]=p[k]; } }catch(e){}
  return d;
})();
function persist(){ try{ localStorage.setItem(LS_KEY, JSON.stringify(save)); }catch(e){} }

var RANKS = [
  {n:"White Belt",min:0},{n:"Yellow Belt",min:300},{n:"Orange Belt",min:800},
  {n:"Green Belt",min:1700},{n:"Blue Belt",min:3000},{n:"Purple Belt",min:4800},
  {n:"Brown Belt",min:7200},{n:"Black Belt",min:10500},{n:"Grandmaster",min:15000}
];
function rankFor(xp){ var r=RANKS[0]; for(var i=0;i<RANKS.length;i++){ if(xp>=RANKS[i].min) r=RANKS[i]; } return r.n; }
function masteryCount(id){ return save.mastery[id]||0; }
function masteryStars(id){ var c=masteryCount(id); return c>=15?3:c>=7?2:c>=3?1:0; }

/* ============================ poison: line mutation engine ============================ */
/* Each rule turns a correct line into a plausible-but-buggy one — exactly the
   off-by-one / operator / direction mistakes the guide's "watch out" boxes warn about. */
var LINE_RULES = [
  [/<=/, "<"], [/>=/, ">"],
  [/ \+ 2\b/, " - 2"], [/ \+ 1\b/, " - 1"], [/ - 1\b/, " + 1"],
  [/\+= /, "-= "], [/-= /, "+= "],
  [/\bmin\(/, "max("], [/\bmax\(/, "min("],
  [/\bleft\b/, "right"], [/\bright\b/, "left"],
  [/\bslow\b/, "fast"], [/\bfast\b/, "slow"],
  [/\bprev1\b/, "prev2"], [/\bprev2\b/, "prev1"],
  [/\bprev\b/, "curr"], [/\bcurr\b/, "prev"],
  [/ or /, " and "], [/ and /, " or "],
  [/\bi - 1\b/, "i + 1"], [/\bi \+ 1\b/, "i - 1"],
  [/\bj - 1\b/, "j + 1"], [/\bj \+ 1\b/, "j - 1"],
  [/, -1\)/, ", 1)"],
  [/\bTrue\b/, "False"], [/\bFalse\b/, "True"],
  [/ < /, " > "], [/ > /, " < "]
];
function mutateLine(line){
  var out = [];
  for(var i=0;i<LINE_RULES.length;i++){
    var r=LINE_RULES[i];
    if(r[0].test(line)){
      var m=line.replace(r[0], r[1]);
      if(m!==line) out.push(m);
    }
  }
  return uniq(out);
}

/* token-level distractors for cloze blanks */
var TOKEN_MUT = {
  "<=":["<",">="], ">=":[">","<="], "==":["!=","<="], "!=":["==",">="],
  "<":[">","<="], ">":["<",">="],
  "min":["max"], "max":["min"], "left":["right"], "right":["left"],
  "slow":["fast"], "fast":["slow"], "prev":["curr"], "curr":["prev"],
  "and":["or"], "or":["and"], "True":["False"], "False":["True"]
};
var TOKEN_RE = /(<=|>=|==|!=|\bmin\b|\bmax\b|\bleft\b|\bright\b|\bslow\b|\bfast\b|\bprev\b|\bcurr\b|\band\b|\bor\b|\bTrue\b|\bFalse\b|<|>)/g;

function findBlanks(lines){
  var cands=[];
  lines.forEach(function(line, li){
    TOKEN_RE.lastIndex=0; var m;
    while((m=TOKEN_RE.exec(line))!==null){
      var tok=m[0];
      if(TOKEN_MUT[tok]){ cands.push({li:li, start:m.index, tok:tok}); }
    }
  });
  return cands;
}

/* ============================ audio (synth, no files) ============================ */
var AC=null;
function actx(){ if(!save.sound) return null; try{ if(!AC) AC=new (window.AudioContext||window.webkitAudioContext)(); if(AC.state==="suspended") AC.resume(); return AC; }catch(e){ return null; } }
function tone(freq, dur, type, vol, delay){
  var ac=actx(); if(!ac) return;
  var t=ac.currentTime+(delay||0);
  var o=ac.createOscillator(), g=ac.createGain();
  o.type=type||"sine"; o.frequency.setValueAtTime(freq, t);
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(vol||0.18, t+0.012);
  g.gain.exponentialRampToValueAtTime(0.0001, t+dur);
  o.connect(g); g.connect(ac.destination); o.start(t); o.stop(t+dur+0.02);
}
var SFX={
  click:function(){ tone(420,0.05,"square",0.06); },
  correct:function(){ tone(660,0.10,"sine",0.16,0); tone(990,0.14,"sine",0.16,0.08); },
  combo:function(n){ var b=520+Math.min(n,10)*60; tone(b,0.08,"triangle",0.14,0); tone(b*1.5,0.12,"triangle",0.13,0.06); },
  wrong:function(){ tone(200,0.18,"sawtooth",0.14,0); tone(150,0.22,"sawtooth",0.12,0.06); },
  level:function(){ [523,659,784,1046].forEach(function(f,i){ tone(f,0.16,"triangle",0.16,i*0.09); }); },
  over:function(){ [392,330,262,196].forEach(function(f,i){ tone(f,0.22,"sawtooth",0.14,i*0.12); }); },
  win:function(){ [523,659,784,1046,1318].forEach(function(f,i){ tone(f,0.18,"sine",0.17,i*0.08); }); }
};

/* ============================ haptics ============================ */
function buzz(p){ if(save.haptics && navigator.vibrate){ try{ navigator.vibrate(p); }catch(e){} } }

/* ============================ confetti ============================ */
var fx=$("#fx"), fxctx=fx?fx.getContext("2d"):null, parts=[], fxRAF=null;
function sizeFx(){ if(!fx) return; fx.width=innerWidth; fx.height=innerHeight; }
window.addEventListener("resize", sizeFx); sizeFx();
function confetti(n){
  if(!fxctx) return; sizeFx();
  var colors=["#a371f7","#f778ba","#ffa657","#3fb950","#58a6ff"];
  for(var i=0;i<(n||80);i++){
    parts.push({x:innerWidth/2,y:innerHeight*0.3,vx:(Math.random()-0.5)*9,vy:Math.random()*-9-3,g:0.28,
      s:4+Math.random()*6, c:colors[randInt(colors.length)], a:1, rot:Math.random()*6, vr:(Math.random()-0.5)*0.4});
  }
  if(!fxRAF) fxRAF=requestAnimationFrame(stepFx);
}
function stepFx(){
  fxctx.clearRect(0,0,fx.width,fx.height);
  for(var i=parts.length-1;i>=0;i--){
    var p=parts[i]; p.vy+=p.g; p.x+=p.vx; p.y+=p.vy; p.rot+=p.vr; p.a-=0.012;
    if(p.a<=0||p.y>fx.height+30){ parts.splice(i,1); continue; }
    fxctx.save(); fxctx.globalAlpha=Math.max(p.a,0); fxctx.translate(p.x,p.y); fxctx.rotate(p.rot);
    fxctx.fillStyle=p.c; fxctx.fillRect(-p.s/2,-p.s/2,p.s,p.s*0.6); fxctx.restore();
  }
  if(parts.length){ fxRAF=requestAnimationFrame(stepFx); } else { fxRAF=null; }
}
function floatPoints(txt){
  var e=ce("div","floatpts",esc(txt)); e.style.left=(innerWidth/2-20)+"px"; e.style.top="38%";
  document.body.appendChild(e); setTimeout(function(){ e.remove(); }, 900);
}

/* ============================ game state ============================ */
var G={};
var MODES=[
  {id:"forge",  emoji:"&#128296;", name:"Code Forge",        desc:"Rebuild the code. Easy lines &rarr; Hard tokens."},
  {id:"cloze",  emoji:"&#129513;", name:"Fill the Gap",      desc:"Drop the right token into every blank."},
  {id:"bug",    emoji:"&#128030;", name:"Bug Hunt",          desc:"One line was poisoned. Hunt it down."},
  {id:"name",   emoji:"&#128373;", name:"Name That Pattern", desc:"Match the clue to its pattern."},
  {id:"bigo",   emoji:"&#128200;", name:"Big-O Climb",       desc:"Recall time & space complexity."},
  {id:"mnemo",  emoji:"&#129504;", name:"Mnemonic Match",    desc:"Match the pattern to its memory hook."},
  {id:"survival",emoji:"&#128128;",name:"The Gauntlet",      desc:"All modes. 3 lives. A ticking clock. How far?"}
];
var SCOPES=[{id:"all",n:"All 37"},{id:"core",n:"Core 15"},{id:"dp",n:"DP 20"},{id:"advanced",n:"Advanced"}];
var DIFFS=[{id:"easy",n:"Easy"},{id:"medium",n:"Medium"},{id:"hard",n:"Hard"}];
var DIFF_DESC={
  easy:"Reorder whole lines &mdash; dodge the poison lines.",
  medium:"Rebuild from jumbled code chunks &mdash; order matters.",
  hard:"Rebuild from single tokens &mdash; some are poison."
};
var scope="all";
var diff="easy";    /* difficulty for Code Forge: easy | medium | hard */
var forgeSrc="template"; /* which snippet Code Forge rebuilds: template | example */
var focusId=null;   /* when set (via ?pattern=...), every "main" question targets this one pattern */

function pool(){
  if(focusId) return [BY_ID[focusId]];
  return scope==="all" ? PATTERNS : PATTERNS.filter(function(p){ return p.cat===scope; });
}
function withTemplate(maxLines){ return pool().filter(function(p){ return p.template && p.template.length>=3 && p.template.length<=(maxLines||13); }); }
function clearFocus(){ focusId=null; try{ history.replaceState(null,"",location.pathname); }catch(e){} renderHome(); show(homeEl); }

/* ============================ screens ============================ */
var homeEl=$("#home"), gameEl=$("#game"), sumEl=$("#summary");

function show(which){
  [homeEl,gameEl,sumEl].forEach(function(s){ s.classList.add("hidden"); });
  which.classList.remove("hidden");
  window.scrollTo(0,0);
}

function renderHome(){
  var stars=0, total=0; pool().forEach(function(p){ stars+=masteryStars(p.id); total+=3; });
  var h="";
  h+='<div class="hero"><h1>Pattern Forge</h1>'+
     '<p>Forge the 37 DSA templates into muscle memory. Reorder code, fill the gaps, hunt the poison, and survive the gauntlet.</p></div>';
  if(focusId){
    h+='<div class="focus-banner">&#127919; Drilling <b>'+esc(BY_ID[focusId].name)+'</b>'+
       '<button id="clearFocus" class="focus-exit">&#10005; all patterns</button></div>';
  }
  h+='<div class="statbar">'+
     '<div class="stat"><b>'+save.high+'</b><span>High score</span></div>'+
     '<div class="stat"><b>'+save.bestStreak+'</b><span>Best streak</span></div>'+
     '<div class="stat"><b>'+save.xp+'</b><span>Total XP</span></div>'+
     '<div class="stat"><b>'+stars+'/'+total+'</b><span>Mastery &#9733;</span></div>'+
     '</div>';
  if(!focusId){ h+='<div class="section-label">Pattern pack</div><div class="scope" id="scope"></div>'; }
  h+='<div class="section-label">Code Forge difficulty</div><div class="scope" id="diffSel"></div>'+
     '<div class="diff-note" id="diffNote">'+DIFF_DESC[diff]+'</div>';
  h+='<div class="section-label">'+(focusId?'Pick a drill for this pattern':'Choose your trial')+'</div><div class="modes" id="modeGrid"></div>';
  h+='<div class="section-label">How it works</div><div class="howto">'+
     '<b>Memorize by doing.</b> Each mode quizzes the real templates &amp; examples from your study guide. '+
     'Wrong answers are <b>poisoned</b> with the exact off-by-one, operator and direction bugs the guide warns about &mdash; '+
     'so you learn to spot them. Build streaks for combo multipliers, earn XP to climb belts, and chase mastery stars on every pattern. '+
     'Sound &amp; vibration give you instant feedback (toggle them up top).</div>';
  h+='<div class="section-label">Mastery board</div><div class="mastery" id="masteryGrid"></div>';
  homeEl.innerHTML=h;

  var cf=$("#clearFocus"); if(cf) cf.onclick=function(){ SFX.click(); clearFocus(); };
  var sc=$("#scope");
  if(sc) SCOPES.forEach(function(s){
    var b=ce("button", s.id===scope?"active":"", s.n);
    b.onclick=function(){ scope=s.id; SFX.click(); renderHome(); };
    sc.appendChild(b);
  });
  var ds=$("#diffSel");
  if(ds) DIFFS.forEach(function(d){
    var b=ce("button", d.id===diff?"active":"", d.n);
    b.onclick=function(){ diff=d.id; SFX.click(); renderHome(); };
    ds.appendChild(b);
  });
  var mg=$("#modeGrid");
  MODES.forEach(function(m){
    var c=ce("button","mode-card"+(m.id==="survival"?" boss":""));
    c.innerHTML='<div class="emoji">'+m.emoji+'</div><h3>'+m.name+'</h3><p>'+m.desc+'</p>';
    c.onclick=function(){ SFX.click(); startSession(m.id); };
    mg.appendChild(c);
  });
  var bd=$("#masteryGrid");
  pool().forEach(function(p){
    var st=masteryStars(p.id);
    var stars5=""; for(var i=0;i<3;i++){ stars5+='<span class="'+(i<st?"star-on":"star-off")+'">&#9733;</span>'; }
    var t=ce("div","mtile");
    t.innerHTML='<div class="cat">'+p.cat+'</div><div class="mn">'+esc(p.name)+'</div><div class="ms">'+stars5+'</div>';
    bd.appendChild(t);
  });
  updateChips();
}

/* ============================ session flow ============================ */
function startSession(mode, opts){
  opts=opts||{};
  G={ mode:mode, survival:(mode==="survival"),
      diff:opts.diff||diff, src:(opts.src==="example"?"example":"template"),
      score:0, streak:0, combo:0,
      lives:(mode==="survival"?3:0), qIndex:0, qTotal:(mode==="survival"?Infinity:10),
      correct:0, answered:false, curId:null, timer:null, timeLeft:0, timeMax:0 };
  show(gameEl); nextQuestion();
}

function timeForMode(mode){
  var forgeBase=(G.diff==="hard")?60:(G.diff==="medium")?46:34;
  var base={forge:forgeBase,cloze:28,bug:20,name:13,bigo:15,mnemo:13}[mode]||16;
  return Math.max(7, base - Math.floor(G.qIndex/4));
}

function nextQuestion(){
  if(!G.survival && G.qIndex>=G.qTotal){ return endSession(); }
  G.qIndex++; G.answered=false; stopTimer();
  var primary = G.survival ? choice(["forge","cloze","bug","name","bigo","mnemo"]) : G.mode;
  var order=[primary];
  /* when drilling one pattern, gracefully fall back to whatever builds for it */
  if(focusId) order=order.concat(["cloze","bug","forge","name","bigo","mnemo"]);
  var mode=primary, built=null;
  for(var oi=0; oi<order.length && !built; oi++){
    var tries=0; while(!built && tries<25){ tries++; built=BUILDERS[order[oi]](); }
    if(built) mode=order[oi];
  }
  if(!built){ mode="name"; built=BUILDERS.name(); }   /* name mode always works */
  G.curId=built.patternId;
  renderQuestion(mode, built);
  if(G.survival){ startTimer(timeForMode(mode)); }
}

function renderQuestion(mode, built){
  var modeName=(function(){ for(var i=0;i<MODES.length;i++) if(MODES[i].id===mode) return MODES[i].name; return mode; })();
  var hud='<div class="hud">'+
    '<button class="btn-back" id="quitBtn">&#8592; Quit</button>'+
    '<div class="hud-score"><small>Score</small>'+G.score+'</div>'+
    (G.combo>1?'<span class="combo-flag">&#128293; x'+comboMult().toFixed(2)+'</span>':'<span class="streak">'+(G.streak>0?("&#128293; "+G.streak):"")+'</span>')+
    (G.survival?('<div class="lives">'+livesHTML()+'</div>'):('<div class="qcount">'+G.qIndex+' / '+G.qTotal+'</div>'))+
    '</div>';
  var timer=G.survival?'<div class="timer-wrap"><div class="timer-bar" id="timerBar"></div></div>':'';
  var card='<div class="qcard"><div class="qmode">'+modeName+'</div>'+
           '<div class="qinstr">'+built.instr+'</div>'+
           '<div id="qbody"></div>'+
           '<div id="qactions"></div>'+
           '<div id="qfeedback"></div></div>';
  gameEl.innerHTML=hud+timer+card;
  $("#quitBtn").onclick=function(){ SFX.click(); stopTimer(); renderHome(); show(homeEl); };
  built.mount($("#qbody"), $("#qactions"), finishQuestion);
}

function comboMult(){ return 1 + Math.min(Math.max(G.combo-1,0),9)*0.15; }
function livesHTML(){ var s=""; for(var i=0;i<3;i++){ s+= (i<G.lives)?"&#10084;&#65039;":"&#128420;"; } return s; }

function finishQuestion(correct, revealHTML){
  if(G.answered) return; G.answered=true; stopTimer();
  var pts=0;
  if(correct){
    G.correct++; G.streak++; G.combo++;
    var speed=1;
    if(G.survival && G.timeMax>0){ speed=0.6+0.4*(G.timeLeft/G.timeMax); }
    pts=Math.round(100*comboMult()*speed);
    G.score+=pts; save.xp+=Math.round(pts/8);
    save.mastery[G.curId]=(save.mastery[G.curId]||0)+1;
    if(G.streak>save.bestStreak) save.bestStreak=G.streak;
    persist(); updateChips();
    if(G.combo>=2){ SFX.combo(G.combo); } else { SFX.correct(); }
    buzz(G.combo>=5?[18,40,18]:30);
    if(G.combo>0 && G.combo%5===0){ confetti(90); SFX.level(); buzz([20,30,20,30,40]); }
    floatPoints("+"+pts);
  } else {
    G.streak=0; G.combo=0;
    if(G.survival) G.lives--;
    SFX.wrong(); buzz([60,40,90]);
  }
  showFeedback(correct, pts, revealHTML);
}

function showFeedback(correct, pts, revealHTML){
  var fb=$("#qfeedback");
  var head=correct?("&#9989; Forged!"):("&#10060; Poisoned!");
  var ptsHTML=correct?('<span class="points">+'+pts+'</span>'):"";
  fb.innerHTML='<div class="feedback '+(correct?"good":"bad")+'">'+
    '<div class="fb-head">'+head+ptsHTML+'</div>'+
    (revealHTML?('<div class="fb-body">'+revealHTML+'</div>'):'')+'</div>';
  var act=$("#qactions"); act.innerHTML="";
  var gameOver = G.survival && G.lives<=0;
  var b=ce("button","btn btn-primary", gameOver?"See results &#8594;":(!G.survival && G.qIndex>=G.qTotal?"Finish &#8594;":"Next &#8594;"));
  b.onclick=function(){ SFX.click(); gameOver?endSession():nextQuestion(); };
  act.appendChild(b);
  if(gameOver){ setTimeout(endSession, 1400); }
  else if(G.survival){ /* keep manual to let players read the reveal */ }
}

function endSession(){
  stopTimer();
  var newHigh = G.score>save.high;
  if(newHigh) save.high=G.score; persist();
  var acc = G.qIndex>0 ? Math.round(100*G.correct/Math.max(G.qIndex - (G.survival?0:0),1)) : 0;
  if(G.survival && G.lives<=0){ SFX.over(); } else if(acc>=80){ SFX.win(); confetti(160); } else { SFX.correct(); }
  buzz(newHigh?[30,40,30,40,60]:[40]);
  var ranked=rankFor(save.xp);
  var h='<div class="sum-wrap">';
  h+='<h2>'+(G.survival?"Gauntlet over":"Round complete")+'</h2>';
  h+='<div class="sum-score">'+G.score+'</div>';
  if(newHigh) h+='<div class="new-best">&#127881; New high score!</div>';
  h+='<div class="sum-grid">'+
     '<div class="stat"><b>'+G.correct+'</b><span>Correct</span></div>'+
     '<div class="stat"><b>'+acc+'%</b><span>Accuracy</span></div>'+
     '<div class="stat"><b>'+save.bestStreak+'</b><span>Best streak</span></div>'+
     '<div class="stat"><b>'+ranked+'</b><span>Belt</span></div>'+
     '</div>';
  h+='<div class="actions">'+
     '<button class="btn btn-primary" id="againBtn">Play again</button>'+
     '<button class="btn" id="homeBtn">Home</button></div>';
  h+='</div>';
  sumEl.innerHTML=h; show(sumEl);
  $("#againBtn").onclick=function(){ SFX.click(); startSession(G.mode,{diff:G.diff, src:G.src}); };
  $("#homeBtn").onclick=function(){ SFX.click(); renderHome(); show(homeEl); };
}

/* ============================ timer ============================ */
function startTimer(secs){
  G.timeMax=secs; G.timeLeft=secs;
  var bar=$("#timerBar"); if(bar) bar.style.width="100%";
  var tick=80; 
  G.timer=setInterval(function(){
    G.timeLeft-=tick/1000;
    var frac=Math.max(0,G.timeLeft/G.timeMax);
    if(bar){ bar.style.width=(frac*100)+"%"; bar.classList.toggle("warn", frac<0.33); }
    if(G.timeLeft<=0){ stopTimer(); if(!G.answered){ finishQuestion(false, "&#9203; Time ran out."); } }
  }, tick);
}
function stopTimer(){ if(G.timer){ clearInterval(G.timer); G.timer=null; } }

/* ============================ option helper ============================ */
function renderOptions(host, options, correctVal, isMono, finish, revealFn){
  var grid=ce("div","opts"+(isMono?"":" "));
  if(options.length<=3 && isMono) grid.className="opts one";
  options.forEach(function(opt){
    var b=ce("button","opt"+(isMono?" mono":""), esc(opt.label!=null?opt.label:opt));
    var val=opt.val!=null?opt.val:opt;
    b.onclick=function(){
      if(G.answered) return;
      var ok = (val===correctVal);
      Array.prototype.forEach.call(grid.children,function(c){ c.classList.add("disabled"); });
      b.classList.add(ok?"correct":"wrong");
      if(!ok){ b.classList.add("shake");
        Array.prototype.forEach.call(grid.children,function(c){
          if(c.getAttribute("data-val")===String(correctVal)) c.classList.add("correct");
        });
      }
      finish(ok, revealFn?revealFn(ok):"");
    };
    b.setAttribute("data-val", String(val));
    grid.appendChild(b);
  });
  host.appendChild(grid);
}

/* ============================ builders ============================ */
var BUILDERS={};

/* --- token helpers (Medium / Hard forge) --- */
function tokenizeLine(line, fine){
  var t=line.trim();
  if(!fine){ return t.split(/\s+/).filter(function(x){ return x.length; }); }
  var re=/(<=|>=|==|!=|\/\/|\*\*|->|"[^"]*"|'[^']*'|\w+|[^\s\w])/g;
  var out=[], m; while((m=re.exec(t))!==null){ out.push(m[0]); }
  return out;
}
function mutateToken(tok){
  var out=(TOKEN_MUT[tok]||[]).slice();
  if(/^\d+$/.test(tok)){ var n=parseInt(tok,10); out.push(String(n+1)); if(n>0) out.push(String(n-1)); }
  return uniq(out);
}
function indentUnits(line){
  var s=(line&&(line.match(/^[ \t]*/)||[""])[0])||"";
  return s.replace(/\t/g,"    ").length;
}
/* strip a trailing "# ..." comment (respecting quotes) so puzzles don't tokenize prose */
function stripComment(line){
  var inS=false, q="";
  for(var i=0;i<line.length;i++){
    var ch=line.charAt(i);
    if(inS){ if(ch===q && line.charAt(i-1)!=="\\") inS=false; }
    else if(ch==='"'||ch==="'"){ inS=true; q=ch; }
    else if(ch==="#"){ return line.slice(0,i); }
  }
  return line;
}
/* code with inline + full-line comments removed (blank lines dropped) */
function codeNoComments(code){
  var out=[];
  code.forEach(function(line){
    var s=stripComment(line).replace(/\s+$/,"");
    if(s.trim().length) out.push(s);
  });
  return out.length>=2 ? out : code.slice();
}

/* --- Code Forge: three difficulties, over the template OR the worked example --- */
BUILDERS.forge=function(){
  var src=(G.src==="example")?"example":"template";
  var dff=G.diff||"easy";
  var maxLines=(dff==="easy")?13:9;
  if(focusId){
    var fp=BY_ID[focusId];
    var fcode=fp[src]||fp.template||fp.example;
    if(!fcode || fcode.length<2) return null;
    return (dff==="easy")?forgeEasy(fp,fcode,src):forgeTokens(fp,fcode,dff,src);
  }
  var cands=pool().filter(function(p){ var c=p[src]; return c && c.length>=3 && c.length<=maxLines; });
  if(!cands.length && src==="example"){
    src="template";
    cands=pool().filter(function(p){ return p.template && p.template.length>=3 && p.template.length<=maxLines; });
  }
  if(!cands.length) return null;
  var p=choice(cands);
  var code=p[src]||p.template;
  return (dff==="easy")?forgeEasy(p,code,src):forgeTokens(p,code,dff,src);
};

/* Easy: reorder whole lines, avoid poison decoy lines (the classic mode) */
function forgeEasy(p, correctSrc, src){
  var correct=correctSrc.slice();
  var decoys=[];
  var attempts=0;
  while(decoys.length<3 && attempts<30){
    attempts++;
    var base=choice(correct);
    var muts=mutateLine(base);
    if(muts.length){
      var d=choice(muts);
      if(correct.indexOf(d)===-1 && decoys.indexOf(d)===-1) decoys.push(d);
    }
  }
  /* nasty cross-pattern decoy */
  var others=pool().filter(function(q){ return q.template && q.id!==p.id; });
  if(others.length){
    var ol=choice(choice(others).template);
    if(correct.indexOf(ol)===-1 && decoys.indexOf(ol)===-1) decoys.push(ol);
  }
  decoys=decoys.slice(0,3);
  var poolLines=shuffle(correct.concat(decoys));
  var picked=[]; /* array of line strings in chosen order */

  return {
    patternId:p.id,
    instr:'<b>Easy.</b> Tap the lines in the right order to rebuild the <b>'+esc(p.name)+'</b> '+(src==="example"?"example":"template")+'. Some lines are <b>poison</b> &mdash; leave them out.',
    mount:function(body, actions, finish){
      var sol=ce("div","code-list"); var solEmpty=ce("div","empty-hint","Tap lines below to start building&hellip;");
      body.appendChild(ce("div","pool-label","Your build"));
      body.appendChild(sol); sol.appendChild(solEmpty);
      body.appendChild(ce("div","pool-label","Line bank"));
      var bank=ce("div","code-list"); body.appendChild(bank);

      function draw(){
        sol.innerHTML=""; 
        if(!picked.length){ sol.appendChild(solEmpty); }
        picked.forEach(function(line,idx){
          var row=ce("button","code-row picked");
          row.innerHTML='<span class="num">'+(idx+1)+'</span><span class="txt">'+esc(line)+'</span>';
          row.onclick=function(){ if(G.answered) return; picked.splice(idx,1); SFX.click(); draw(); };
          sol.appendChild(row);
        });
        bank.innerHTML="";
        /* render bank as remaining (account for duplicates) */
        var remaining=poolLines.slice();
        picked.forEach(function(l){ var i=remaining.indexOf(l); if(i>=0) remaining.splice(i,1); });
        remaining.forEach(function(line){
          var row=ce("button","code-row");
          row.innerHTML='<span class="num">+</span><span class="txt">'+esc(line)+'</span>';
          row.onclick=function(){ if(G.answered) return; picked.push(line); SFX.click(); draw(); };
          bank.appendChild(row);
        });
      }
      draw();

      var check=ce("button","btn btn-primary","Check build");
      check.onclick=function(){
        if(G.answered) return;
        var ok = picked.length===correct.length && picked.every(function(l,i){ return l===correct[i]; });
        /* visual diff */
        Array.prototype.forEach.call(sol.querySelectorAll(".code-row"),function(row,i){
          row.classList.remove("picked");
          row.classList.add(picked[i]===correct[i]?"correct":"wrong");
          if(picked[i]!==correct[i]) row.classList.add("shake");
        });
        var reveal='The correct '+(src==="example"?"example":"template")+':<br><br><span class="mono" style="white-space:pre-wrap">'+esc(correct.join("\n"))+'</span>';
        finish(ok, reveal);
      };
      actions.appendChild(check);
    }
  };
}

/* Medium (chunks) / Hard (single tokens + poison): assemble tokens into wrapping lines.
   Each token is a chip of natural width but uniform height; a ↵ chip ends a line. */
function forgeTokens(p, rawCode, dff, src){
  var fine=(dff==="hard");
  var code=codeNoComments(rawCode);  /* puzzle uses code w/o comments; reveal keeps them */
  var stripped=code.length!==rawCode.length || code.some(function(l,i){ return l!==rawCode[i]; });
  var target=[]; /* ordered cells: {kind:'tok',val} | {kind:'nl'} */
  code.forEach(function(line, li){
    tokenizeLine(line, fine).forEach(function(tk){ target.push({kind:"tok", val:tk}); });
    if(li<code.length-1) target.push({kind:"nl"});
  });
  var chips=[]; var cid=0;
  target.forEach(function(cell){
    chips.push(cell.kind==="nl" ? {id:cid++, kind:"nl"} : {id:cid++, kind:"tok", val:cell.val});
  });
  if(dff==="hard"){
    var toks=target.filter(function(c){ return c.kind==="tok"; });
    var added=0, tries=0;
    while(added<3 && tries<50 && toks.length){
      tries++;
      var muts=mutateToken(choice(toks).val);
      if(muts.length){ chips.push({id:cid++, kind:"tok", val:choice(muts), poison:true}); added++; }
    }
  }
  var bank=shuffle(chips);
  var byId={}; bank.forEach(function(c){ byId[c.id]=c; });
  var picked=[]; /* chip ids in chosen order */

  return {
    patternId:p.id,
    instr:(fine
      ? '<b>Hard.</b> This <b>'+esc(p.name)+'</b> '+(src==="example"?"example":"template")+' is smashed into single <b>tokens</b> &mdash; a few are <b>poison</b>. Tap them in order; use <b>&#8629;</b> to end each line.'
      : '<b>Medium.</b> This <b>'+esc(p.name)+'</b> '+(src==="example"?"example":"template")+' is broken into <b>chunks</b>. Tap them in the right order; use <b>&#8629;</b> to end each line.'),
    mount:function(body, actions, finish){
      body.appendChild(ce("div","pool-label","Your build"));
      var build=ce("div","forge-lines"); body.appendChild(build);
      body.appendChild(ce("div","pool-label","Token bank"));
      var bankEl=ce("div","tok-bank"); body.appendChild(bankEl);

      function newRow(lineIdx){
        var row=ce("div","forge-row");
        row.style.paddingLeft=(indentUnits(code[lineIdx])*0.55)+"em";
        build.appendChild(row);
        return row;
      }
      function draw(){
        build.innerHTML="";
        var lineIdx=0, row=newRow(0);
        if(!picked.length){ row.appendChild(ce("span","tok-hint","Tap tokens below to start building&hellip;")); }
        picked.forEach(function(id, pos){
          var chip=byId[id];
          var b=ce("button","tok picked"+(chip.kind==="nl"?" nl":""), chip.kind==="nl"?"&#8629;":esc(chip.val));
          b.onclick=(function(pp){ return function(){ if(G.answered) return; picked.splice(pp,1); SFX.click(); draw(); }; })(pos);
          row.appendChild(b);
          if(chip.kind==="nl"){ lineIdx++; row=newRow(lineIdx); }
        });
        bankEl.innerHTML="";
        bank.forEach(function(chip){
          if(picked.indexOf(chip.id)>=0) return;
          var b=ce("button","tok"+(chip.kind==="nl"?" nl":""), chip.kind==="nl"?"&#8629;":esc(chip.val));
          b.onclick=function(){ if(G.answered) return; picked.push(chip.id); SFX.click(); draw(); };
          bankEl.appendChild(b);
        });
      }
      draw();

      var check=ce("button","btn btn-primary","Check build");
      check.onclick=function(){
        if(G.answered) return;
        var cells=picked.map(function(id){ return byId[id]; });
        var ok = cells.length===target.length && cells.every(function(c,i){
          var t=target[i]; if(!t||t.kind!==c.kind) return false;
          return t.kind==="tok" ? (c.val===t.val) : true;
        });
        Array.prototype.forEach.call(build.querySelectorAll(".tok"),function(el,i){
          el.classList.remove("picked");
          var t=target[i], c=cells[i];
          var good = !!t && t.kind===c.kind && (t.kind!=="tok" || t.val===c.val);
          el.classList.add(good?"correct":"wrong");
          if(!good) el.classList.add("shake");
        });
        var reveal='The correct '+(src==="example"?"example":"template")+':<br><br><span class="mono" style="white-space:pre-wrap">'+esc(rawCode.join("\n"))+'</span>'+
          (stripped?'<br><br><span style="color:var(--dim)">Comments are shown for reference &mdash; the puzzle leaves them out.</span>':'');
        finish(ok, reveal);
      };
      actions.appendChild(check);
    }
  };
}

/* --- Fill the Gap (cloze) --- */
BUILDERS.cloze=function(){
  var cands=pool().filter(function(p){ return p.template && p.template.length<=16; });
  cands=shuffle(cands);
  for(var c=0;c<cands.length;c++){
    var p=cands[c];
    var lines=(p.example&&p.example.length<=16)? (Math.random()<0.5?p.example:p.template) : p.template;
    var blanks=findBlanks(lines);
    if(blanks.length<1) continue;
    var chosen=sample(blanks, Math.min(3,blanks.length));
    /* avoid two blanks on same position */
    return makeCloze(p, lines, chosen);
  }
  return null;
};
function makeCloze(p, lines, chosen){
  /* group chosen by line, build HTML with selects */
  var byLine={}; chosen.forEach(function(b){ (byLine[b.li]=byLine[b.li]||[]).push(b); });
  var slots=[]; /* {id, correct} */
  var sid=0;
  var htmlLines=lines.map(function(line, li){
    var marks=(byLine[li]||[]).slice().sort(function(a,b){ return b.start-a.start; });
    var s=line;
    marks.forEach(function(b){
      var id="b"+(sid++);
      slots.push({id:id, correct:b.tok});
      s = s.slice(0,b.start) + "\u0001"+id+"\u0001" + s.slice(b.start+b.tok.length);
    });
    return s;
  });
  var joined=esc(htmlLines.join("\n"));
  slots.forEach(function(sl){
    var opts=uniq([sl.correct].concat(TOKEN_MUT[sl.correct]||[]));
    opts=shuffle(opts);
    var sel='<select class="blank" data-correct="'+esc(sl.correct)+'" id="'+sl.id+'"><option value="">?</option>'+
      opts.map(function(o){ return '<option value="'+esc(o)+'">'+esc(o)+'</option>'; }).join("")+'</select>';
    joined=joined.replace("\u0001"+sl.id+"\u0001", sel);
  });
  return {
    patternId:p.id,
    instr:'Fill every blank in this <b>'+esc(p.name)+'</b> snippet. Watch for sneaky look-alikes.',
    mount:function(body, actions, finish){
      var pre=ce("div","cloze"); pre.innerHTML=joined; body.appendChild(pre);
      var check=ce("button","btn btn-primary","Check");
      check.onclick=function(){
        if(G.answered) return;
        var all=true;
        slots.forEach(function(sl){
          var el=$("#"+sl.id, pre); var ok=el.value===el.getAttribute("data-correct");
          el.classList.add(ok?"ok":"no"); el.disabled=true; if(!ok) all=false;
        });
        var reveal = all? "Clean code &mdash; every token correct." :
          ('Correct tokens: '+slots.map(function(s){ return '<code>'+esc(s.correct)+'</code>'; }).join(", "));
        finish(all, reveal);
      };
      actions.appendChild(check);
    }
  };
}

/* --- Bug Hunt: one poisoned line --- */
BUILDERS.bug=function(){
  var cands=withTemplate(14).filter(function(p){ return p.template.length>=4; });
  cands=shuffle(cands);
  for(var c=0;c<cands.length;c++){
    var p=cands[c];
    var idxs=shuffle(p.template.map(function(_,i){ return i; }));
    for(var k=0;k<idxs.length;k++){
      var i=idxs[k]; var muts=mutateLine(p.template[i]);
      if(muts.length){
        var bug=choice(muts);
        var lines=p.template.slice(); var orig=lines[i]; lines[i]=bug;
        return makeBug(p, lines, i, orig, bug);
      }
    }
  }
  return null;
};
function makeBug(p, lines, bugIdx, orig, bug){
  return {
    patternId:p.id,
    instr:'Exactly one line of this <b>'+esc(p.name)+'</b> template was poisoned. Tap the buggy line.',
    mount:function(body, actions, finish){
      var list=ce("div","code-list");
      lines.forEach(function(line, idx){
        var row=ce("button","code-row");
        row.innerHTML='<span class="num">'+(idx+1)+'</span><span class="txt">'+esc(line)+'</span>';
        row.onclick=function(){
          if(G.answered) return;
          var ok=(idx===bugIdx);
          Array.prototype.forEach.call(list.children,function(r){ r.classList.add("disabled"); });
          list.children[bugIdx].classList.add("correct");
          if(!ok){ row.classList.add("wrong","shake"); }
          var reveal='Line '+(bugIdx+1)+' should be:<br><span class="mono">'+esc(orig)+'</span>';
          finish(ok, reveal);
        };
        list.appendChild(row);
      });
      body.appendChild(list);
    }
  };
}

/* --- Name That Pattern --- */
BUILDERS.name=function(){
  var p = focusId ? BY_ID[focusId] : choice(pool());
  var distract=(p.confus||[]).map(function(id){ return BY_ID[id]; }).filter(Boolean);
  var others=shuffle(PATTERNS.filter(function(q){ return q.id!==p.id && distract.indexOf(q)===-1; }));
  var opts=[p].concat(sample(distract,2));
  while(opts.length<4 && others.length) opts.push(others.pop());
  opts=shuffle(uniq(opts.map(function(x){return x.id;}))).map(function(id){ return BY_ID[id]; });
  return {
    patternId:p.id,
    instr:'A problem gives you this hint. Which pattern do you reach for?',
    mount:function(body, actions, finish){
      body.appendChild(ce("div","qclue","&ldquo;"+esc(p.clue)+"&rdquo;"));
      var grid=ce("div","opts");
      opts.forEach(function(o){
        var b=ce("button","opt",esc(o.name));
        b.setAttribute("data-val",o.id);
        b.onclick=function(){
          if(G.answered) return;
          var ok=o.id===p.id;
          Array.prototype.forEach.call(grid.children,function(c){ c.classList.add("disabled");
            if(c.getAttribute("data-val")===p.id) c.classList.add("correct"); });
          if(!ok) b.classList.add("wrong","shake");
          finish(ok, ok?"":("It was <b>"+esc(p.name)+"</b> &mdash; "+esc(p.mnemonic||"")));
        };
        grid.appendChild(b);
      });
      body.appendChild(grid);
    }
  };
};

/* --- Big-O Climb --- */
var TIME_LADDER=["O(1)","O(log n)","O(n)","O(n log n)","O(n²)","O(n³)","O(2^n)","O(n!)"];
BUILDERS.bigo=function(){
  var p=choice(pool());
  var askSpace=Math.random()<0.5;
  var correct=askSpace?p.space:p.time;
  var poolVals=uniq(PATTERNS.map(function(q){ return askSpace?q.space:q.time; }));
  poolVals=poolVals.filter(function(v){ return v!==correct; });
  var opts=uniq([correct].concat(sample(poolVals,3))).slice(0,4);
  opts=shuffle(opts).map(function(v){ return {label:v, val:v}; });
  return {
    patternId:p.id,
    instr:'What is the typical <b>'+(askSpace?"space":"time")+'</b> complexity of this pattern?',
    mount:function(body, actions, finish){
      body.appendChild(ce("div","qbig",esc(p.name)));
      if(p.mnemonic) body.appendChild(ce("div","qclue","&ldquo;"+esc(p.mnemonic)+"&rdquo;"));
      renderOptions(body, opts, correct, false, finish, function(ok){
        return ok?"":("Correct: <code>"+esc(correct)+"</code> (the other is <code>"+esc(askSpace?p.time:p.space)+"</code>).");
      });
    }
  };
};

/* --- Mnemonic Match --- */
BUILDERS.mnemo=function(){
  var allM=PATTERNS.filter(function(p){ return p.mnemonic; });
  if(allM.length<4) return null;
  var p = focusId ? BY_ID[focusId] : choice(pool().filter(function(q){ return q.mnemonic; }));
  if(!p || !p.mnemonic) return null;
  var others=shuffle(allM.filter(function(q){ return q.id!==p.id; })).slice(0,3);
  var opts=shuffle([p].concat(others)).map(function(x){ return {label:x.mnemonic, val:x.id}; });
  return {
    patternId:p.id,
    instr:'Which memory hook belongs to this pattern?',
    mount:function(body, actions, finish){
      body.appendChild(ce("div","qbig",esc(p.name)));
      renderOptions(body, opts, p.id, true, finish, function(ok){
        return ok?"":("Its hook: &ldquo;"+esc(p.mnemonic)+"&rdquo;");
      });
    }
  };
};

/* ============================ settings + chrome ============================ */
function updateChips(){
  var rc=$("#rankChip"); if(rc) rc.textContent=rankFor(save.xp);
  var sb=$("#soundBtn"), hb=$("#hapticBtn");
  if(sb){ sb.classList.toggle("off",!save.sound); sb.innerHTML=save.sound?"&#128266;":"&#128263;"; }
  if(hb){ hb.classList.toggle("off",!save.haptics); }
}
function applyTheme(t){ document.documentElement.setAttribute("data-theme",t); localStorage.setItem("dsa-theme",t);
  var tb=$("#themeBtn"); if(tb) tb.innerHTML=(t==="dark")?"&#9789;":"&#9728;"; }

$("#soundBtn").onclick=function(){ save.sound=!save.sound; persist(); updateChips(); if(save.sound){ actx(); SFX.correct(); } };
$("#hapticBtn").onclick=function(){ save.haptics=!save.haptics; persist(); updateChips(); buzz(40); };
$("#themeBtn").onclick=function(){ applyTheme(document.documentElement.getAttribute("data-theme")==="dark"?"light":"dark"); };

applyTheme(localStorage.getItem("dsa-theme")||"dark");
updateChips();

/* deep-link: ?pattern=<id>&mode=<mode>&src=template|example&diff=easy|medium|hard */
(function initFromURL(){
  try{
    var params=new URLSearchParams(location.search);
    var fp=params.get("pattern"), fm=params.get("mode");
    var fd=params.get("diff"), fs=params.get("src");
    if(fd==="easy"||fd==="medium"||fd==="hard") diff=fd;
    if(fs==="example"||fs==="template") forgeSrc=fs;
    if(fp && BY_ID[fp]){
      focusId=fp;
      if(fm && BUILDERS[fm]){ startSession(fm,{diff:diff, src:forgeSrc}); return; }
    }
  }catch(e){}
  renderHome();
})();
})();
'''


INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0d1117">
<title>Pattern Forge · DSA Mastery</title>
<link rel="stylesheet" href="assets/game.css">
</head>
<body>
<header class="pf-top">
  <a class="pf-brand" href="../index.html" title="Back to the study guide">
    <span class="pf-mark">{ }</span><span class="pf-brandtxt">Pattern Forge</span>
  </a>
  <div class="pf-rank" id="rankChip" title="Your belt — earn XP to rank up">White Belt</div>
  <div class="pf-spacer"></div>
  <button id="soundBtn" class="pf-icon" title="Sound on/off" aria-label="Toggle sound">&#128266;</button>
  <button id="hapticBtn" class="pf-icon" title="Vibration on/off" aria-label="Toggle vibration">&#128243;</button>
  <button id="themeBtn" class="pf-icon" title="Light / dark" aria-label="Toggle theme">&#9789;</button>
</header>

<main id="screens">
  <section id="home" class="screen"></section>
  <section id="game" class="screen hidden"></section>
  <section id="summary" class="screen hidden"></section>
</main>

<canvas id="fx" aria-hidden="true"></canvas>

<script src="assets/game-data.js"></script>
<script src="assets/game.js"></script>
</body>
</html>
"""


def main():
    patterns = build_patterns()
    GAME.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    data = {"patterns": patterns}
    (ASSETS / "game-data.js").write_text(
        "window.GAME_DATA = " + json.dumps(data, ensure_ascii=False, indent=0) + ";\n",
        encoding="utf-8",
    )
    (ASSETS / "game.css").write_text(GAME_CSS, encoding="utf-8")
    (ASSETS / "game.js").write_text(GAME_JS, encoding="utf-8")
    (GAME / "index.html").write_text(INDEX_HTML, encoding="utf-8")

    # quick console report
    miss_t = [p["id"] for p in patterns if not p["template"]]
    print(f"patterns: {len(patterns)}")
    print(f"missing template: {miss_t or 'none'}")
    print(f"with example: {sum(1 for p in patterns if p['example'])}")
    print("wrote", (ASSETS / 'game-data.js').relative_to(HERE))
    print("wrote", (ASSETS / 'game.css').relative_to(HERE))
    print("wrote", (ASSETS / 'game.js').relative_to(HERE))
    print("wrote", (GAME / 'index.html').relative_to(HERE))
    print("\nDone. Open:", (GAME / "index.html"))


if __name__ == "__main__":
    main()
