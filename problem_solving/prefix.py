"This function is to get the longest prefix from strings in an array"

def pref(arr: list) -> str:
    if len(arr) == 1:
        return arr[0]
    elif len(arr) == 0:
        return ""
    
    pref = ''
    i = 1
    shortest_string = min(arr, key=lambda x: len(x))
    while len(pref) < len(shortest_string):
        f_word = arr[0][:i]
        for word in arr:
            if not word.startswith(f_word):
                return pref
        pref = f_word
        i += 1
    return pref


print(pref(["flower", "flow", "flight"]))
print(pref(["dog", "racecar", "car"]))
print(pref(["interspecies", "interstellar", "interstate"]))
print(pref(["a"]))
print(pref([]))
