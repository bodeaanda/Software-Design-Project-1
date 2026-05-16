def levenshtein_distance(s1: str, s2: str) -> int:
    s1 = s1.lower()
    s2 = s2.lower()

    rows = len(s1) + 1
    cols = len(s2) + 1

    matrix = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(0)
        matrix.append(row)

    # first row and column
    for i in range(rows):
        matrix[i][0] = i
    for j in range(cols):
        matrix[0][j] = j

    # fill the matrix
    for i in range(1, rows):
        for j in range(1, cols):
            if s1[i - 1] == s2[j - 1]:
                matrix[i][j] = matrix[i - 1][j - 1] 
            else:
                delete  = matrix[i - 1][j] + 1
                insert  = matrix[i][j - 1] + 1
                replace = matrix[i - 1][j - 1] + 1
                matrix[i][j] = min(delete, insert, replace)

    return matrix[rows - 1][cols - 1]


def similarity_score(s1: str, s2: str) -> float:
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return 1.0 - (distance / max_len)