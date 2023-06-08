import random, string

class MappingFunction():
    def __init__(self, size = 30) -> None:
        self.sampleSize = size

    def setSampleSize(self, size):
        self.sampleSize = size

    def generate_random_string(self, length):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))

    def mapToTestData(self, seed):
        random.seed(seed)
        result = []
        for _ in range(self.sampleSize):
            r = self.generate_random_string(10)
            o = self.generate_random_string(10)
            result.append((r, o))

        return result

mappingFunction = MappingFunction()