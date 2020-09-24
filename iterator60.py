arr = ['0', '1', '2', '3', '4', '5',
       '6', '7', '8', '9', 'a', 'b',
       'c', 'd', 'e', 'f', 'g', 'h',
       'i', 'j', 'k', 'l', 'm', 'n',
       'o', 'p', 'q', 'r', 's', 't',
       'w', 'v', 'x', 'y', 'z', 'A',
       'B', 'C', 'D', 'E', 'F', 'G',
       'H', 'I', 'J', 'K', 'L', 'M',
       'N', 'O', 'P', 'Q', 'R', 'S',
       'T', 'W', 'V', 'X', 'Y', 'Z']


def goNext(word):
    for i in range(len(word) - 1, -1, -1):
        word = word[:i] + addOne(word[i]) + word[i + 1:]
        if word[i] != '0':
            break
        if i == 0 and word[0] == '0':
            word = '1' + word
            break
    return word


def addOne(key):
    x = arr.index(key)
    if x < len(arr) - 1:
        x += 1
    else:
        x = 0
    key = arr[x]
    return key

# num = '1'
# for j in range(0, 9999999):
#   num = goNext(num)
#   print(str(j) + ": " + num)
