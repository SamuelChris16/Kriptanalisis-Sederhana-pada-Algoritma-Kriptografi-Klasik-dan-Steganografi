import random
import string
import os
import time
import math
from collections import Counter

# =========================
# 1. CLEAN TEXT
# =========================

def clean_text(text):
    text = text.upper().replace("J", "I")
    return ''.join(c for c in text if c in string.ascii_uppercase)


# =========================
# 2. BUILD INTERNAL QUADGRAM MODEL
# =========================

def build_quadgrams():

    # Corpus internal besar (gabungan teks klasik)
    corpus = """
    THE PROJECT GUTENBERG EBOOK OF THE ADVENTURES OF SHERLOCK HOLMES BY ARTHUR CONAN DOYLE
    IT WAS THE BEST OF TIMES IT WAS THE WORST OF TIMES IT WAS THE AGE OF WISDOM
    IT WAS THE AGE OF FOOLISHNESS IT WAS THE EPOCH OF BELIEF IT WAS THE EPOCH OF INCREDULITY
    CALL ME ISHMAEL SOME YEARS AGO NEVER MIND HOW LONG PRECISELY
    IN THE BEGINNING GOD CREATED THE HEAVEN AND THE EARTH
    TO THE DISTINGUISHED COMMISSIONER OF THE METROPOLITAN POLICE
    HOWEVER I AM A GENTLEMAN THIEF AND I BELIEVE IN FAIR PLAY
    IT WAS A STRANGE AND TRAGIC ENDING TO A VOYAGE THAT HAD COMMENCED IN AN AUSPICIOUS MANNER
    THE ATLANTIC STEAMSHIP LA PROVENCE WAS A SWIFT AND COMFORTABLE VESSEL
    """

    text = clean_text(corpus)

    quad_counts = Counter(text[i:i+4] for i in range(len(text)-3))
    total = sum(quad_counts.values())

    quadgrams = {}
    for q in quad_counts:
        quadgrams[q] = math.log10(quad_counts[q] / total)

    floor = math.log10(0.01 / total)

    return quadgrams, floor


# =========================
# 3. PLAYFAIR DECRYPT
# =========================

def decrypt(ciphertext, key):

    plaintext = []
    pos = {key[i]: (i//5, i%5) for i in range(25)}

    for i in range(0, len(ciphertext), 2):

        if i+1 >= len(ciphertext):
            break

        a = ciphertext[i]
        b = ciphertext[i+1]

        r1, c1 = pos[a]
        r2, c2 = pos[b]

        if r1 == r2:
            plaintext.append(key[r1*5 + (c1-1)%5])
            plaintext.append(key[r2*5 + (c2-1)%5])

        elif c1 == c2:
            plaintext.append(key[((r1-1)%5)*5 + c1])
            plaintext.append(key[((r2-1)%5)*5 + c2])

        else:
            plaintext.append(key[r1*5 + c2])
            plaintext.append(key[r2*5 + c1])

    return ''.join(plaintext)


# =========================
# 4. SCORING
# =========================

def score_text(text, quadgrams, floor):
    score = 0
    for i in range(len(text)-3):
        quad = text[i:i+4]
        score += quadgrams.get(quad, floor)
    return score


# =========================
# ADVANCED MUTATION
# =========================

def mutate_key(key):

    new_key = key[:]
    mode = random.randint(0, 2)

    # swap dua huruf
    if mode == 0:
        a, b = random.sample(range(25), 2)
        new_key[a], new_key[b] = new_key[b], new_key[a]

    # swap satu baris
    elif mode == 1:
        row1, row2 = random.sample(range(5), 2)
        for i in range(5):
            new_key[row1*5+i], new_key[row2*5+i] = \
            new_key[row2*5+i], new_key[row1*5+i]

    # swap satu kolom
    else:
        col1, col2 = random.sample(range(5), 2)
        for i in range(5):
            new_key[i*5+col1], new_key[i*5+col2] = \
            new_key[i*5+col2], new_key[i*5+col1]

    return new_key


# =========================
# STRONGER ANNEALING
# =========================

def simulated_annealing(ciphertext, quadgrams, floor,
                        iterations=40000,
                        start_temp=20):

    key = list("ABCDEFGHIKLMNOPQRSTUVWXYZ")
    random.shuffle(key)

    best_key = key[:]
    best_plain = decrypt(ciphertext, key)
    best_score = score_text(best_plain, quadgrams, floor)

    current_score = best_score

    for i in range(iterations):

        new_key = mutate_key(key)
        new_plain = decrypt(ciphertext, new_key)
        new_score = score_text(new_plain, quadgrams, floor)

        temp = start_temp * (1 - i/iterations)

        delta = new_score - current_score

        if delta > 0 or random.random() < math.exp(delta / (temp + 1e-9)):
            key = new_key
            current_score = new_score

            if new_score > best_score:
                best_key = new_key
                best_plain = new_plain
                best_score = new_score

        # 🔥 Reheat kalau stuck
        if i % 10000 == 0 and i != 0:
            key = best_key[:]
            current_score = best_score

    return best_key, best_plain, best_score


# =========================
# MULTIPLE SHORT RESTART
# =========================

def auto_attack(ciphertext, quadgrams, floor, restarts=1):

    global_best_score = -1e9
    global_best_plain = ""
    global_best_key = None

    for r in range(restarts):

        print(f"\nRestart {r+1}/{restarts}")

        key, plain, score = simulated_annealing(ciphertext, quadgrams, floor)

        print("Score:", score)
        print("Preview:", plain[:200])

        if score > global_best_score:
            global_best_score = score
            global_best_plain = plain
            global_best_key = key

    return global_best_key, global_best_plain


# =========================
# 8. MAIN
# =========================

if __name__ == "__main__":

    if not os.path.exists("ciphertext.txt"):
        print("ciphertext.txt tidak ditemukan!")
        exit()

    with open("ciphertext.txt", "r") as f:
        ciphertext = clean_text(f.read())

    print("Building internal quadgram model...")
    quadgrams, floor = build_quadgrams()

    print("Memulai attack...\n")
    start = time.time()

    key, plaintext = auto_attack(ciphertext, quadgrams, floor)

    end = time.time()

    print("\n=== HASIL TERBAIK ===")
    print("Key:", ''.join(key))
    print("\nPreview plaintext:\n")
    print(plaintext[:1000])

    with open("decrypted_output.txt", "w") as f:
        f.write(plaintext)

    print("\nTotal waktu:", round(end-start,2), "detik")
    print("Hasil disimpan ke decrypted_output.txt")