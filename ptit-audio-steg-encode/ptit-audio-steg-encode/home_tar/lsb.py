import wave
import os

def encode(input_wave, output_wave, message):
    # Mở file âm thanh gốc
    song = wave.open(input_wave, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    
    # Lấy kích thước file gốc
    original_size = os.path.getsize(input_wave)
    print(f"📊 Kích thước file gốc: {original_size} bytes")
    
    # Thêm ký tự kết thúc để biết khi nào dừng lại khi giải mã
    message = message + '###'
    bits = ''.join([format(ord(i), '08b') for i in message])
    
    # Hiển thị chuỗi nhị phân sẽ được giấu
    print(f"🔢 Chuỗi nhị phân sẽ giấu: {bits}")
    print(f"📝 Độ dài chuỗi nhị phân: {len(bits)} bits")

    if len(bits) > len(frame_bytes):
        raise ValueError("Thông điệp quá dài để giấu trong file âm thanh này.")
    
    print(f"💾 Số byte có thể sử dụng trong file âm thanh: {len(frame_bytes)} bytes")

    # Giấu từng bit của thông điệp vào LSB của frame bytes
    for i, bit in enumerate(bits):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(bit)

    modified_frames = bytes(frame_bytes)

    # Lưu file âm thanh đã chứa thông điệp
    with wave.open(output_wave, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(modified_frames)

    song.close()
    
    # Lấy kích thước file sau khi giấu tin
    modified_size = os.path.getsize(output_wave)

    print(f"✅ Giấu tin thành công vào {output_wave}")


def decode(stego_wave):
    # Mở file âm thanh đã giấu tin
    song = wave.open(stego_wave, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    # Trích xuất bit LSB từ mỗi byte
    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    bits = ''.join(map(str, extracted))
    
    # Hiển thị một phần chuỗi nhị phân đã được trích xuất (để tránh quá dài)
    print(f"🔢 Phần đầu của chuỗi nhị phân được trích xuất: {bits[:100]}...")
    
    # Chuyển chuỗi nhị phân thành ký tự
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    
    message = ''.join(chars)

    # Tách lấy thông điệp (trước ký tự kết thúc "###")
    if "###" in message:
        hidden_message = message.split("###")[0]
        print(f"🔍 Tin đã giấu là: {hidden_message}")
        
        # Hiển thị chuỗi nhị phân tương ứng với thông điệp
        binary_message = ''.join([format(ord(i), '08b') for i in hidden_message])
        print(f"🔢 Chuỗi nhị phân của tin đã giấu: {binary_message}")
    else:
        print("❌ Không tìm thấy thông điệp hợp lệ.")
    
    song.close()

# Ví dụ sử dụng
if __name__ == "__main__":
    encode("sample-1.wav", "output.wav", "toi yeu e nuoc man dong chua r")
