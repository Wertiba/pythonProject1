import re

data = 'и таким образом кодовое слово куница'

def find_word():
    tags = re.finditer(r"кодовое слово (\S+)", data)
    for tag in tags:
        word = (tag.group(1))
        return word

print(find_word())