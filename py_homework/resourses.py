def construct_matrix(n, k):
    if k == 1:
        return (True, [[i] for i in range(1, n + 1)])

    if n % 2 == 1:
        return (False, None)

    m = []
    for i in range(1, n + 1):
        row = []
        for j in range(k):
            row.append(i + j * n)
        m.append(row)

    return True, m