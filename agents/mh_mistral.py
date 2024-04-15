from transformers import AutoModelForCausalLM, AutoTokenizer
from mh_agent import MHAgent
from mh_chess import MHChess
import torch

class MHMistral(MHAgent):
    def __init__(self, model_name='mistralai/Mistral-7B-Instruct-v0.2', color='white'):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model_name = model_name
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.name = self.getname()
        self.color = color

    def getname(self):
        return 'Mistral'

    def makeMove(self, board):
        prompt = self.generatePrompt(board)
        ans = self.generateResponse(prompt)
        ##  Validate the move...
        ans = ans[ans.index('[/INST]')+8:].strip().rstrip()
        legal_moves = board.getLegalMoves()
        for move in legal_moves:
            if move in ans:
                return move, ans
        return None, ans


    def generateResponse(self, input_text):
        messages = [
            {"role": "user", "content": input_text},
        ]
        encodeds = self.tokenizer.apply_chat_template(messages, return_tensors="pt")
        model_inputs = encodeds.to(self.device)
        self.model.to(self.device)
        generated_ids = self.model.generate(model_inputs, max_new_tokens=1000, do_sample=True)
        decoded = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        return decoded[0]

    def generatePrompt(self, board):
        template = '{system_message}. {message}'
        system_message = f"You are a professional chess player. You are playing a game of chess as {self.color}. P, N, B, R, Q and K represent white pieces. p, n, b, r, q and k represent black pieces. It's your turn to make a move. You will get a list of legal moves you can make. You should choose one of them. You should only output the UCI notation of the move you want to make with no additional text."
        message = "Here's the current board state:\n\n" + str(board) + "\n\n"
        message += "Here's a list of possible moves:\n- "
        message += "\n- ".join(board.getLegalMoves()) + "\n\n"
        message += "Please make a move by choosing one of the above options. You should only output the UCI notation of the move you want to make with no additional text."
        return message


if __name__ == "__main__":
    mh_mistral = MHMistral()
    board = MHChess()
    for i in range(10):
        move, ans = mh_mistral.makeMove(board)
        board.makeMove(move)
        print(move)
        print(board)
    