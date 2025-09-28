from backend.interfaces.paper import IPaper


class PaperPage(IPaper):
    """Representa uma página de um documento com metadados."""

    def __init__(self, page: int, content: str):
        self.page = page
        self.content = content
