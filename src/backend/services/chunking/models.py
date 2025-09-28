from backend.interfaces.paper import IPaper


class PaperChunk(IPaper):
    """Representa um chunk de um documento."""

    def __init__(self, page: int, content: str):
        self.page = page
        self.content = content
