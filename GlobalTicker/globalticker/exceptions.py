class GlobalTickerError(Exception):
    pass

class ProviderNotFound(GlobalTickerError):
    pass

class SymbolNotFound(GlobalTickerError):
    pass