import nltk
import re
import heapq
import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
for pkg in ("punkt", "punkt_tab", "stopwords", "wordnet"):
    nltk.download(pkg, quiet=True)

with open(r"D:\IIITV\D1.txt", encoding='utf-8')as f:
    t1=f.read().lower()
with open(r"D:\IIITV\D2.txt", encoding='utf-8')as f:
    t2=f.read().lower()

negation={"no", "not", "nor", "never", "none", "nobody", "nothing",
            "neither", "nowhere", "cannot", "without"}
stop_words=set(stopwords.words('english'))-negation
lemm=WordNetLemmatizer()


def expand_contractions(text):
    text = text.replace("’", "'")
    text = text.replace("can't", "cannot").replace("won't", "will not")
    return re.sub(r"n't\b", " not", text)  

def preprocess(text):
    text=expand_contractions(text)
    token=word_tokenize(text)
    token=["not" if w=="n't" else w for w in token]    
    token=[w for w in token if not w in stop_words and w.isalpha()]
    token=[lemm.lemmatize(w, pos='n') for w in token]
    token=[lemm.lemmatize(w, pos='v') for w in token]
    return " ".join(token)

original_A=sent_tokenize(t1)
cleaned_A=[preprocess(s) for s in original_A]

original_B=sent_tokenize(t2)
cleaned_B=[preprocess(s) for s in original_B]

m=len(cleaned_A)
n=len(cleaned_B)

print("Document A:", m, "sentences")
print("Document B:", n, "sentences")

tv=TfidfVectorizer(ngram_range=(1, 3))
matrix=tv.fit_transform(cleaned_A + cleaned_B)

sim=cosine_similarity(matrix[:m], matrix[m:])
feature_names = tv.get_feature_names_out()
df = pd.DataFrame(sim.round(2),
                  index=([f"A{i}" for i in range(m)]),
                  columns=([f"B{j}" for j in range(n)]))
print("\nCosine similarity (higher = more similar):")
print(df)

def dp(a, b):
    m=len(a)
    n=len(b)
    table=[[0]*(n+1) for _ in range(m+1)]

    for i in range(m+1):
        table[i][0]=i

    for j in range(n+1):
        table[0][j]=j

    for i in range(1, m+1):
        for j in range(1, n+1):
            if a[i-1]==b[j-1]:
                cost=0
            else:
                cost=1
            table[i][j]=min(table[i-1][j]+1, table[i][j-1]+1, table[i-1][j-1]+cost)

    return table[m][n]


def norm_dp(a, b):
    if not a or not b:            
        return 1.0
    return dp(a, b) / max(len(a), len(b))

lev_table=[[norm_dp(cleaned_A[i], cleaned_B[j]) for j in range(n)] for i in range(m)]
df_lev=pd.DataFrame(lev_table,
                    index=([f"A{i}" for i in range(m)]),
                    columns=([f"B{j}" for j in range(n)]))
print("\nNormalized Levenshtein (lower = more similar):")
print(df_lev.round(2))

def jaccard(a, b):
    sa, sb = set(a.split()), set(b.split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

jac_table = [[jaccard(cleaned_A[i], cleaned_B[j]) for j in range(n)] for i in range(m)]

df_jac = pd.DataFrame(jac_table,
                      index=[f"A{i}" for i in range(m)],
                      columns=[f"B{j}" for j in range(n)])
print("\nJaccard (higher = more similar):")
print(df_jac.round(2))

w1, w2, w3 = 0.5, 0.25, 0.25

cost = [[w1 * lev_table[i][j]
         + w2 * (1 - jac_table[i][j])
         + w3 * (1 - sim[i][j])
         for j in range(n)] for i in range(m)]

df_cost = pd.DataFrame(cost,
                       index=[f"A{i}" for i in range(m)],
                       columns=[f"B{j}" for j in range(n)])
print("\nBlended cost (lower = more similar):")
print(df_cost.round(2))

SKIP_COST = 0.6    
C0, J0 = 0.2, 0.2   
THRESHOLD = 0.45   

def is_candidate(i, j):
    return sim[i][j] >= C0 or jac_table[i][j] >= J0

def astar(m, n):
    def h(i, j):                               
        return abs((m - i) - (n - j)) * SKIP_COST

    start, goal = (0, 0), (m, n)
    pq = [(h(*start), 0.0, start)]            
    best_g = {start: 0.0}                      
    parent = {start: None}                     
    expanded = 0

    while pq:
        f, g, (i, j) = heapq.heappop(pq)
        if (i, j) == goal:
            break
        if g > best_g[(i, j)]:                
            continue
        expanded += 1

        moves = []                        
        if i < m and j < n and is_candidate(i, j):
            moves.append(((i + 1, j + 1), cost[i][j], True)) 
        if i < m:
            moves.append(((i + 1, j), SKIP_COST, False))       
        if j < n:
            moves.append(((i, j + 1), SKIP_COST, False))       

        for nxt, c, is_align in moves:
            new_g = g + c
            if new_g < best_g.get(nxt, float("inf")):
                best_g[nxt] = new_g
                parent[nxt] = ((i, j), is_align)
                heapq.heappush(pq, (new_g + h(*nxt), new_g, nxt))


    pairs, cur = [], goal
    while parent[cur] is not None:
        prev, is_align = parent[cur]
        if is_align:
            pairs.append(prev)                    
        cur = prev
    pairs.reverse()

    return best_g[goal], pairs, expanded


total_cost, pairs, expanded = astar(m, n)
print(f"\nA* total cost: {total_cost:.2f}   nodes expanded: {expanded}")

flagged = 0
for i, j in pairs:
    c = cost[i][j]
    verdict = "FLAGGED" if c <= THRESHOLD else "not flagged"
    flagged += c <= THRESHOLD
    print(f"\nA{i} <-> B{j}   cost {c:.2f}   {verdict}")
    print("  A:", original_A[i])
    print("  B:", original_B[j])

print(f"\nPlagiarism score: {flagged / n:.0%}  ({flagged} of {n} sentences in B)")

if pairs:
    mean_sim = 1 - sum(cost[i][j] for i, j in pairs) / len(pairs)
    print(f"Average similarity of aligned pairs: {mean_sim:.0%}")
else:
    print("Average similarity of aligned pairs: 0% (no pairs aligned)")