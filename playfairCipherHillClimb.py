import random
import string
import os
import time

# =========================
# 1. CLEAN TEXT
# =========================

def clean_text(text):
    text = text.upper().replace("J", "I")
    return ''.join(c for c in text if c in string.ascii_uppercase)


# =========================
# 2. FAST ENGLISH SCORING
# =========================

COMMON_PATTERNS = [
    "THE", "AND", "ING", "THAT",
    "WITH", "YOU", "THIS", "FROM",
    "HAVE", "NOT", "OR", "WILL", "STAY", "BY"
]

def score_text(text):
    score = 0
    for p in COMMON_PATTERNS:
        score += text.count(p) * 5
    return score


# =========================
# 3. FAST PLAYFAIR
# =========================

def generate_random_key():
    alphabet = list("ABCDEFGHIKLMNOPQRSTUVWXYZ")
    random.shuffle(alphabet)
    return alphabet


def decrypt(ciphertext, key):
    plaintext = []
    
    # 🔥 Precompute posisi huruf (FAST lookup)
    pos = {key[i]: (i // 5, i % 5) for i in range(25)}
    
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
# 4. MUTATE KEY
# =========================

def mutate_key(key):
    a, b = random.sample(range(25), 2)
    new_key = key[:]
    new_key[a], new_key[b] = new_key[b], new_key[a]
    return new_key


# =========================
# 5. HILL CLIMBING (FAST)
# =========================

def hill_climb(ciphertext, iterations=3000):
    best_key = generate_random_key()
    best_plain = decrypt(ciphertext, best_key)
    best_score = score_text(best_plain)
    
    for _ in range(iterations):
        new_key = mutate_key(best_key)
        new_plain = decrypt(ciphertext, new_key)
        new_score = score_text(new_plain)
        
        if new_score > best_score:
            best_key = new_key
            best_plain = new_plain
            best_score = new_score
    
    return best_key, best_plain, best_score


# =========================
# 6. MULTIPLE RESTART
# =========================

def auto_attack(ciphertext, restarts=30):
    global_best_score = -1
    global_best_plain = ""
    global_best_key = None
    
    total_start = time.time()
    
    for r in range(restarts):
        restart_start = time.time()
        
        key, plain, score = hill_climb(ciphertext)
        
        restart_time = time.time() - restart_start
        
        print(f"Restart {r+1}/{restarts} | Score: {score} | {restart_time:.2f}s")
        
        if score > global_best_score:
            global_best_score = score
            global_best_plain = plain
            global_best_key = key
    
    total_time = time.time() - total_start
    
    print(f"\nTotal waktu attack: {total_time:.2f} detik ({total_time/60:.2f} menit)")
    
    return global_best_key, global_best_plain


# =========================
# 7. MAIN
# =========================

if __name__ == "__main__":
    
    if not os.path.exists("ciphertext.txt"):
        print("File ciphertext.txt tidak ditemukan!")
        exit()
    
    with open("ciphertext.txt", "r") as f:
        ciphertext = clean_text(f.read())
    
    print("Memulai Hill Climbing Attack (Optimized)...\n")
    
    key, plaintext = auto_attack(ciphertext, restarts=30)
    
    print("\n=== HASIL TERBAIK ===")
    print("Key:", ''.join(key))
    print("\nPreview plaintext:\n")
    print(plaintext[:1000])
    
    with open("decrypted_output.txt", "w") as f:
        f.write(plaintext)
    
    print("\nDisimpan ke decrypted_output.txt")