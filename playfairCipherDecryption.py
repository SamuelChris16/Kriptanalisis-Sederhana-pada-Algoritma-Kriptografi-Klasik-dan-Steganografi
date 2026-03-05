import random
import math
import time
from collections import Counter

ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"


# =========================
# CLEAN TEXT
# =========================

def clean_text(text):
    text = text.upper().replace("J","I")
    return ''.join(c for c in text if c in ALPHABET)


# =========================
# CHARACTER DISTRIBUTION
# =========================

def character_distribution(text):

    counter = Counter(text)

    print("\nTop Character Distribution:")
    for c,n in counter.most_common(10):
        print(c,n)

    return counter


# =========================
# BIGRAM ANALYSIS
# =========================

def bigram_analysis(text):

    bigrams = [text[i:i+2] for i in range(0,len(text)-1,2)]

    counter = Counter(bigrams)

    print("\nTop Bigrams:")
    for b,n in counter.most_common(15):
        print(b,n)

    return counter


# =========================
# BUILD QUADGRAM MODEL
# =========================

def build_quadgrams():

    corpus = """
    THEPROJECTGUTENBERGEBOOKOFTHESHERLOCKHOLMES
    ITWASTHEBESTOFTIMESITWASTHEWORSTOFTIMES
    CALLMEISHMAELSOMEYEARSAGONEVERMINDHOWLONG
    INTHEBEGINNINGGODCREATEDTHEHEAVENANDTHEEARTH
    THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG
    """

    corpus = clean_text(corpus)

    counts = Counter(corpus[i:i+4] for i in range(len(corpus)-3))

    total = sum(counts.values())

    quad = {}

    for q in counts:
        quad[q] = math.log10(counts[q]/total)

    floor = math.log10(0.01/total)

    return quad,floor


# =========================
# PLAYFAIR DECRYPT
# =========================

def decrypt(ciphertext,key):

    pos = {key[i]:(i//5,i%5) for i in range(25)}

    plaintext = []

    for i in range(0,len(ciphertext),2):

        if i+1 >= len(ciphertext):
            break

        a = ciphertext[i]
        b = ciphertext[i+1]

        r1,c1 = pos[a]
        r2,c2 = pos[b]

        if r1==r2:

            plaintext.append(key[r1*5 + (c1-1)%5])
            plaintext.append(key[r2*5 + (c2-1)%5])

        elif c1==c2:

            plaintext.append(key[((r1-1)%5)*5 + c1])
            plaintext.append(key[((r2-1)%5)*5 + c2])

        else:

            plaintext.append(key[r1*5 + c2])
            plaintext.append(key[r2*5 + c1])

    return ''.join(plaintext)


# =========================
# SCORE TEXT
# =========================

def score_text(text,quad,floor):

    score = 0

    for i in range(len(text)-3):

        q = text[i:i+4]

        score += quad.get(q,floor)

    return score


# =========================
# MUTATE KEY
# =========================

def mutate_key(key):

    new = key[:]

    a,b = random.sample(range(25),2)

    new[a],new[b] = new[b],new[a]

    return new


# =========================
# HILL CLIMB + ANNEALING
# =========================

def simulated_annealing(ciphertext,quad,floor,iterations=50000):

    key = list(ALPHABET)
    random.shuffle(key)

    best_key = key[:]
    best_plain = decrypt(ciphertext,key)
    best_score = score_text(best_plain,quad,floor)

    current_score = best_score

    for i in range(iterations):

        new_key = mutate_key(key)

        new_plain = decrypt(ciphertext,new_key)

        new_score = score_text(new_plain,quad,floor)

        delta = new_score-current_score

        temp = 20*(1-i/iterations)

        if delta>0 or random.random()<math.exp(delta/(temp+1e-9)):

            key = new_key
            current_score = new_score

            if new_score>best_score:

                best_score=new_score
                best_key=new_key
                best_plain=new_plain

        if i%10000==0:

            print("Iter",i,"score",best_score)

    return best_key,best_plain,best_score


# =========================
# MULTIPLE RESTART
# =========================

def auto_attack(ciphertext,quad,floor,restarts=20):

    global_best_score=-1e9
    global_best_plain=""
    global_best_key=None

    for r in range(restarts):

        print("\nRestart",r+1)

        key,plain,score = simulated_annealing(ciphertext,quad,floor)

        print("Score:",score)

        print("Preview:",plain[:200])

        if score>global_best_score:

            global_best_score=score
            global_best_plain=plain
            global_best_key=key

    return global_best_key,global_best_plain


# =========================
# MAIN
# =========================

if __name__=="__main__":

    with open("ciphertext.txt","r") as f:

        ciphertext = clean_text(f.read())

    print("Ciphertext length:",len(ciphertext))

    character_distribution(ciphertext)

    bigram_analysis(ciphertext)

    print("\nBuilding English model...")

    quad,floor = build_quadgrams()

    start=time.time()

    key,plaintext = auto_attack(ciphertext,quad,floor)

    end=time.time()

    print("\n===== FINAL RESULT =====")

    print("Recovered Key:")
    print(''.join(key))

    print("\nPreview Plaintext:")
    print(plaintext[:1000])

    with open("decrypted_output.txt","w") as f:

        f.write(plaintext)

    print("\nSaved to decrypted_output.txt")

    print("\nTime:",round(end-start,2),"seconds")