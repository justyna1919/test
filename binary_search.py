def binary_search(list, target):

    start = 0
    end = len(list) - 1
    while start <= end:
        mid = start + end
        guess = list[mid]
        if guess == target:
            return mid
        elif guess > target:
            end = mid - 1
        else:
            start = mid + 1
    return None


my_list = [1, 3, 5, 7, 9]
print(binary_search(my_list, 3))  # => 1
