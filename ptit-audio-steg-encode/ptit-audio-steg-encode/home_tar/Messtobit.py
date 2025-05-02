def message_to_bits(message):
    return ''.join(format(ord(char), '08b') for char in message)

msg = "abc"
bits = message_to_bits(msg)
print(bits)

