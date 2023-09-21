count = 0
messages = []
while True:
    count = count + 1
    s = input()
    if s != "#stop":
        if count % 2 != 0:
            messages.append({'role': 'assistant', 'content': s})
        else:
            messages.append({'role': 'user', 'content': s})
    else:
        break
print(messages)
with open('memory.txt', 'a', encoding='utf-8') as f:
    f.write(str(messages) + "\n")
    f.close()
