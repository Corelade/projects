def max_subarray(arr: list) -> int:
    if len(arr) <= 1:
        return sum(arr)

    max_sub = float("-inf")
    for i in range(len(arr)):
        for j in range(i + 1, len(arr) + 1):
            if not arr[i:j]:
                continue
            sliced_arr = sum(arr[i:j])
            if sliced_arr > max_sub:
                max_sub = sliced_arr

    return max_sub


# def max_subarray_v2(arr: list) -> int:
    TODO


print(max_subarray([1, -3, 2, 1, -1]))
print(max_subarray([4, -1, 2, 1]))
print(max_subarray([1]))
print(max_subarray([-2, -3, -1, -5]))
print(max_subarray([0, 0, 0]))
print(max_subarray([0, 2, 0]))
print(max_subarray([-1, 0, -2]))
"""
M([1]) -> 1
M([1, 2]) -> [1], [1, 2]
M([1, 2, 3]) -> [1], [1, 2], [1, 2, 3], [2, 3]

"""
