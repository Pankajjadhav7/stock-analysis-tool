class JSONResponse:
    def __init__(self, data="", error="",message="", status_code=""):
        self.data = data
        self.error = error
        self.message = message
        self.status_code = status_code

    def to_json(self):
        return {
            "data": self.data,
            "error": self.error,
            "message": self.message,
            "status": self.status_code
        }
