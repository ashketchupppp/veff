class Test:
    def __init__(self, v) -> None:
        self.v = v

    def __iter__(self) -> None:
        for i in self.v:
            yield i

t = Test([1, 2, 3])
for i in t:
    print(i)