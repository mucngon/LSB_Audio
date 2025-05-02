import wave
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tabulate import tabulate

def analyze_audio_files(original_file, modified_file, num_bytes=50, offset=0):
    with wave.open(original_file, 'rb') as orig:
        orig_params = orig.getparams()
        orig_frames = orig.readframes(orig.getnframes())
        orig_bytes = bytearray(orig_frames)

    with wave.open(modified_file, 'rb') as mod:
        mod_params = mod.getparams()
        mod_frames = mod.readframes(mod.getnframes())
        mod_bytes = bytearray(mod_frames)

    print(f"=== THONG TIN CO BAN ===")
    print(f"File goc: {original_file}")
    print(f"- So kenh: {orig_params.nchannels}")
    print(f"- Sample width: {orig_params.sampwidth} bytes")
    print(f"- Frame rate: {orig_params.framerate} Hz")
    print(f"- So frames: {orig_params.nframes}")
    print(f"- Tong so bytes: {len(orig_bytes)}")
    print(f"\nFile da giau tin: {modified_file}")
    print(f"- Tong so bytes: {len(mod_bytes)}")

    print("\n=== SO SANH THONG SO KY THUAT ===")
    if orig_params == mod_params:
        print("Thong so ky thuat giong nhau")
    else:
        print("Thong so khac nhau:")
        for param_name in ['nchannels', 'sampwidth', 'framerate', 'nframes']:
            orig_val = getattr(orig_params, param_name)
            mod_val = getattr(mod_params, param_name)
            if orig_val != mod_val:
                print(f"- {param_name}: {orig_val} (goc) vs {mod_val} (giau tin)")

    print(f"\n=== SO SANH BYTE (offset {offset}, {num_bytes} bytes) ===")
    data = []
    for i in range(offset, min(offset + num_bytes, len(orig_bytes), len(mod_bytes))):
        ob = orig_bytes[i]
        mb = mod_bytes[i]
        ob_bin = format(ob, '08b')
        mb_bin = format(mb, '08b')
        if ob != mb:
            diff = "✓" if abs(ob - mb) == 1 else "✗"
            bit_diff = "".join(["●" if ob_bin[j] != mb_bin[j] else " " for j in range(8)])
        else:
            diff = " "
            bit_diff = " " * 8
        data.append([i, ob, ob_bin, mb, mb_bin, diff, bit_diff])

    headers = ["Vi tri", "Byte goc", "Nhi phan goc", "Byte sau", "Nhi phan sau", "Khac", "Bit khac"]
    print(tabulate(data, headers=headers, tablefmt="grid"))

    diff_bytes = sum(1 for i in range(min(len(orig_bytes), len(mod_bytes))) if orig_bytes[i] != mod_bytes[i])
    print(f"\nTong byte khac: {diff_bytes}/{min(len(orig_bytes), len(mod_bytes))} ({diff_bytes/min(len(orig_bytes), len(mod_bytes))*100:.2f}%)")
    lsb_diff = sum(1 for i in range(min(len(orig_bytes), len(mod_bytes))) if (orig_bytes[i]&1) != (mod_bytes[i]&1))
    print(f"Byte co LSB khac: {lsb_diff}/{min(len(orig_bytes), len(mod_bytes))} ({lsb_diff/min(len(orig_bytes), len(mod_bytes))*100:.2f}%)")

    if diff_bytes > 0:
        for i in range(min(len(orig_bytes), len(mod_bytes))):
            if orig_bytes[i] != mod_bytes[i]:
                print(f"\nVi tri dau tien khac: {i}")
                print(f"Byte goc: {orig_bytes[i]} ({format(orig_bytes[i],'08b')})")
                print(f"Byte sau: {mod_bytes[i]} ({format(mod_bytes[i],'08b')})")
                break

    return orig_bytes, mod_bytes

def visualize_differences(orig_bytes, mod_bytes, start=0, length=200):
    end = min(start + length, len(orig_bytes), len(mod_bytes))
    x = range(start, end)
    plt.figure(figsize=(12, 8))
    plt.subplot(211)
    plt.plot(x, orig_bytes[start:end], 'b-', label='Goc', alpha=0.7)
    plt.plot(x, mod_bytes[start:end], 'r-', label='Giau tin', alpha=0.7)
    plt.title('So sanh byte')
    plt.xlabel('Vi tri byte')
    plt.ylabel('Gia tri')
    plt.legend()
    plt.grid(True)
    plt.subplot(212)
    diff = [mod_bytes[i] - orig_bytes[i] for i in range(start, end)]
    plt.stem(x, diff, linefmt='g-', markerfmt='go', basefmt='r-')
    plt.title('Chenhlech byte')
    plt.xlabel('Vi tri byte')
    plt.ylabel('Chenhlech')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('byte_comparison.png')

def extract_lsb_pattern(bytes_array, length=100):
    lsb = [byte & 1 for byte in bytes_array[:length]]
    print("\n=== MAU BIT LSB ===")
    print("".join(map(str, lsb)))
    return lsb

def compare_with_message(message, mod_bytes, length=None):
    if length is None:
        length = len(message) * 8
    msg_bits = ''.join([format(ord(i), '08b') for i in message])
    lsb_bits = ''.join([str(byte & 1) for byte in mod_bytes[:length]])
    print("\n=== SO SANH THONG DIEP VOI LSB ===")
    print(f"Bit tu thong diep: {msg_bits}")
    print(f"Bit LSB trich xuat: {lsb_bits[:len(msg_bits)]}")
    match = sum(1 for i in range(min(len(msg_bits), len(lsb_bits))) if msg_bits[i] == lsb_bits[i])
    print(f"Bit khop: {match}/{len(msg_bits)} ({match/len(msg_bits)*100:.2f}%)")

def analyze_steganography(original_file, modified_file, message=None, num_bytes=50, offset=0, visualize=True):
    orig_bytes, mod_bytes = analyze_audio_files(original_file, modified_file, num_bytes, offset)
    extract_lsb_pattern(mod_bytes, 100)
    if message:
        compare_with_message(message, mod_bytes)
    if visualize:
        visualize_differences(orig_bytes, mod_bytes, offset, 200)
    return orig_bytes, mod_bytes

if __name__ == "__main__":
    analyze_steganography(
        original_file="sample-1.wav",
        modified_file="output.wav",
        message="toi yeu e nuoc man dong chua r",
        num_bytes=50,
        offset=0,
        visualize=True
    )

