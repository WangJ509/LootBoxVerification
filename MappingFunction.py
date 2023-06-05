import random, string

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def mapToTestData(seed):
    random.seed(seed)
    result = []
    for _ in range(5):
        r = generate_random_string(10)
        o = generate_random_string(10)
        result.append((r, o))

    return result
