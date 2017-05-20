
class Algorithm(object):

    def __init__(self, *args, **kwargs):
        pass
    def fit(self):
        pass

    @property
    def result(self):
        """I'm the 'result' property."""
        return self._result

    @result.setter
    def result(self, value):
        self._result = value

    @result.deleter
    def result(self):
        del self._result