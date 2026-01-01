import copy

def count_down(n):
    print(n)
    if n == 1:
        return n
    n -= 1
    return count_down(n)


# count_down(5)

# print("-*-" * 10)


def count_up(n, start=1):
    print(start)
    if start == n:
        return n

    start += 1
    return count_up(n, start)


# count_up(5)

# print("-*-" * 10)


def sum_to(n):
    if n == 1:
        return n
    return sum_to(n - 1) + n


# print(sum_to(4))

# print("-*-" * 10)


def factorial(n):
    if n == 1:
        return n
    return factorial(n - 1) * n


# print(factorial(5))

# print("-*-" * 10)


def reverse_string(string):
    """hello should become olleh"""
    """yes should become sey"""
    if len(string) == 1:
        return string

    new_string = ""
    new_string += string[-1]
    return new_string + reverse_string(string[:-1])


# print(reverse_string('hello'))


def length(string):
    if string[0] == string:
        return 1
    count = 0
    count += 1
    return count + length(string[1:])


# print(length('wonderful'))


def sum_list(list):
    if len(list) == 1:
        return list[0]
    count = list[0]
    return count + sum_list(list[1:])


# print(sum_list([2, 3, 4, 5]))


def contains(lst, val):
    if not lst:
        return False
    if lst[0] == val:
        return True
    return contains(lst[1:], val)


# print(contains([3, 5, 7, 9], 7))


def power(n, exp):
    if exp == 0:
        return 1
    if exp == 1:
        return n * exp
    exp -= 1
    return n * power(n, exp)


# print(power(2, 3))


def is_palindrome(string):
    if len(string) == 0:
        return True
    if string[0] != string[-1]:
        return False
    return is_palindrome(string[1:-1])


# print(is_palindrome('madam'))
# print(is_palindrome('hello'))
# print(is_palindrome('bob'))


def count_occurrences(lst, val):
    count = 0
    if len(lst) == 0:
        return count
    if lst[0] == val:
        count += 1
    return count + count_occurrences(lst[1:], val)


# print(count_occurrences([1, 2, 2, 3, 2], 3))


def find_max(lst):
    if len(lst) <= 1:
        return lst[0]

    if lst and find_max(lst[:1]) > find_max(lst[1:]):
        return find_max(lst[:1])
    return find_max(lst[1:])


# print(find_max([3, 7, 2, 9, 4, 11]))
"""
[4] = 4
[5, 4] = 5 , [4] = 4
"""

"""this is linear binary search"""
"""
def binary_search(lst, val):
    if lst:
        if lst[0] == val:
            return True
        return binary_search(lst[1:], val)
    return False
    
"""


def binary_search(lst, val):
    if len(lst) == 1 and lst[0] != val:
        return False
    mid = len(lst) // 2
    if lst[0] == val or lst[mid] == val:
        return True
    first_lst = lst[:mid]
    sec_lst = lst[mid:]

    if first_lst[-1] >= val:
        return binary_search(first_lst, val)
    return binary_search(sec_lst, val)


# print(binary_search([1, 3, 5, 7, 9], 0))
"""
[1,3]
[7, 9]

fl = 3 > 6? No
sl = [7, 9]

fl = [7]
sl = [9]

fl = [7]

"""


def permutations(string):
    lst = []

    if len(string) == 1:
        return [string]
    
    for i in range(len(string)):
        res = string[:i] + string[i + 1:]
        cur = string[i]      
        P = permutations(res)
        ans1 = [cur + p for p in P]
        lst.extend(ans1)
        
    return lst

print(permutations('kola'))

"""
P[abc] -> P[a] + P[bc], P[bc] + P[a] => [abc, bca, acb, cba]
P[bc] -> P[b] + P[c], P[c] + P[b] => lst[b] + lst[c], lst[c] + lst[b] => [bc, cb]
P[b] = lst[b]
P[c] = lst[c]

P[abc] -> P[b] + P[ac], P[ac], P[b] -> bca, cab, bac, acb
P[ac] -> P[a] + P[c], P[c] + P[a] -> ca, ac
P[c] -> c
P[a] -> a

P[abc] -> P[c] + P[ab], P[ab] + P[c]  -> cab, cba
P[ab] -> P[a] + P[b], P[b], P[a] -> ab, ba
P[a] -> a
P[b] -> b
"""

