def infoed(fn):
    def __wrapper__(self, *args, **kwargs):
        # ensure that info cache is updated
        self.info
        return fn(self, *args, **kwargs)
    return property(__wrapper__)