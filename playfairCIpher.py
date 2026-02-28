import random
import string
import os

# =========================
# 1. CLEAN TEXT
# =========================

def clean_text(text):
    text = text.upper().replace("J", "I")
    return ''.join(c for c in text if c in string.ascii_uppercase)


# =========================
# 2. GENERATE RANDOM KEY
# =========================

def generate_random_key():
    alphabet = list("ABCDEFGHIKLMNOPQRSTUVWXYZ")
    random.shuffle(alphabet)
    return alphabet


def key_to_matrix(key):
    return [key[i:i+5] for i in range(0, 25, 5)]


def find_position(matrix, char):
    for r in range(5):
        for c in range(5):
            if matrix[r][c] == char:
                return r, c


# =========================
# 3. PLAYFAIR DECRYPT
# =========================

def decrypt(ciphertext, key):
    matrix = key_to_matrix(key)
    plaintext = ""
    
    for i in range(0, len(ciphertext), 2):
        if i+1 >= len(ciphertext):
            break
        
        a, b = ciphertext[i], ciphertext[i+1]
        r1, c1 = find_position(matrix, a)
        r2, c2 = find_position(matrix, b)
        
        if r1 == r2:
            plaintext += matrix[r1][(c1-1)%5]
            plaintext += matrix[r2][(c2-1)%5]
        elif c1 == c2:
            plaintext += matrix[(r1-1)%5][c1]
            plaintext += matrix[(r2-1)%5][c2]
        else:
            plaintext += matrix[r1][c2]
            plaintext += matrix[r2][c1]
    
    return plaintext


# =========================
# 4. ENGLISH FILTER
# =========================

COMMON_PATTERNS = [
    "THE", "AND", "ING", "THAT", "WITH", "YOU", "THIS", "FROM", "HAVE", "NOT", "YOUR", "I", "WAS", "TO", "OF", "A", "IN", "IS", "IT", "FOR", "ON", "AS", "ARE"
]

def looks_english(text):
    score = 0
    for pattern in COMMON_PATTERNS:
        if pattern in text:
            score += 1
    return score


# =========================
# 5. MAIN
# =========================

if __name__ == "__main__":
    
    if not os.path.exists("ciphertext.txt"):
        print("File ciphertext.txt tidak ditemukan!")
        exit()
    
    with open("ciphertext.txt", "r") as f:
        ciphertext = clean_text(f.read())
    
    print("Ciphertext loaded.")
    
    attempts = int(input("Berapa banyak key ingin dicoba? "))
    threshold = int(input("Minimal jumlah pola English agar ditampilkan? (misal 2 atau 3): "))
    
    results = []
    
    for i in range(attempts):
        key = generate_random_key()
        plaintext = decrypt(ciphertext, key)
        score = looks_english(plaintext)
        
        if score >= threshold:
            print("\n=================================")
            print(f"Match ditemukan! Attempt #{i+1}")
            print("Score:", score)
            print("Key:", ''.join(key))
            print("Preview:", plaintext[:300])
            
            results.append((score, ''.join(key), plaintext[:500]))
    
    # Simpan semua kandidat bagus
    with open("filtered_results.txt", "w") as f:
        for r in results:
            f.write("Score: " + str(r[0]) + "\n")
            f.write("Key: " + r[1] + "\n")
            f.write("Preview: " + r[2] + "\n")
            f.write("\n=====================\n\n")
    
    print("\nSelesai.")
    print("Semua kandidat disimpan di filtered_results.txt")