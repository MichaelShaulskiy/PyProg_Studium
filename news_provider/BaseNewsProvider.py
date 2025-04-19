from .provider import NewsProvider

class CBaseNewsProvider(NewsProvider):
    """
    NOT A BASE CLASS
    Wrapper of the abstract base class to make it constructable via toolz curry
    BaseNewsProvier = curry(CBaseNewsProvider)
    WeltNewsProvider = BaseNewsProvider("welt.de")
    etc...
    """
    def __init__(self, site):
        super().__init__(site)