from PIL import Image

img = Image.open("/Users/amandarizki/Desktop/Semester 06/Kriptografi/Kriptanalisis-Sederhana-pada-Algoritma-Kriptografi-Klasik-dan-Steganografi/extract_this.png")
pixels = list(img.getdata())

bits = []

# ambil LSB dari GREEN channel
for r,g,b in pixels:
    bits.append(g & 1)

# bit → byte
bytes_data = []
for i in range(0,len(bits),8):
    byte = 0
    for j in range(8):
        if i+j < len(bits):
            byte = (byte << 1) | bits[i+j]
    bytes_data.append(byte)

data = bytes(bytes_data)

# cari magic byte
start = data.find(b"1412")

if start == -1:
    print("Magic byte tidak ditemukan")
    exit()

hidden = data[start+4:]

# decode tanpa crash
text = hidden.decode("utf-8", errors="ignore")

# simpan ke file
with open("pesan_tersembunyi.txt","w",encoding="utf-8") as f:
    f.write(text)

print("Pesan berhasil disimpan ke pesan_tersembunyi.txt")