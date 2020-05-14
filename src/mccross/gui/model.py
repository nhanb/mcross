from .. import document


class Model:
    plaintext = "Nothing to see here... yet."
    gemini_nodes = None

    def update_content(self, plaintext):
        self.plaintext = plaintext
        self.gemini_nodes = []
        try:
            self.gemini_nodes = document.parse(plaintext)
        except Exception:
            print("Invalid gemini document!")
