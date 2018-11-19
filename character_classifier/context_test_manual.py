import context

top_level = context.Scope({})

while True:
    print(top_level.get_valid_characters())
    char = input()
    if char == '_':
        break
    top_level.put_character(char)

print(top_level.to_string())
