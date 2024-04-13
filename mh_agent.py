from abc import ABC, abstractmethod

class MHAgent(ABC):
    @abstractmethod
    def makeMove(self, board):
        pass

    @abstractmethod
    def generateResponse(self, input_text):
        pass

    @abstractmethod
    def generatePrompt(self, board):
        pass

        

