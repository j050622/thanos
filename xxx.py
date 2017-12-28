import copy

lst = [['mark', 3], ['jessica', 5], ['lucy', 1]]
max_num = 5
old_lst = copy.deepcopy(lst)
new_lst = []
del_lst = []

while 1:
    for i in old_lst:
        if i[1] == 0:
            del_lst.append(i)
            continue
        new_lst.append(i[0])
        i[1] -= 1

    for j in del_lst:
        old_lst.remove(j)
    del_lst = []

    if not old_lst:
        break

print(new_lst)

# lst0 = []
# for n in range(1, 5 + 1):
#     for sub_lst in lst:
#         if sub_lst[1] >= n:
#             lst0.append(sub_lst[0])
#
#     print(n, ' --- ', lst0)
