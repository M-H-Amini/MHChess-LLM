from transformers import pipeline
from mh_agent import MHAgent
from mh_chess import MHChess
import torch

class MHLLama3(MHAgent):
    def __init__(self, model_name='meta-llama/Meta-Llama-3-8B-Instruct', color='white'):
        self.model_name = model_name
        self.name = self.getname()
        self.color = color
        self.pipeline = pipeline(
            "text-generation",
            model=model_name,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device="cuda",
        )

    def getname(self):
        if '8b' in self.model_name:
            return 'Llama3-8b'
        elif '70b' in self.model_name:
            return 'Llama3-70b'

    def makeMove(self, board):
        prompt = self.generatePrompt(board)
        ans = self.generateResponse(prompt)
        ##  Validate the move...
        legal_moves = board.getLegalMoves()
        for move in legal_moves:
            if move in ans:
                return move, ans
        return None, ans


    def generateResponse(self, input_text):
        system_message = f"You are a professional chess player. You are playing a game of chess as {self.color}. P, N, B, R, Q and K represent white pieces. p, n, b, r, q and k represent black pieces. It's your turn to make a move. You will get a list of legal moves you can make. You should choose one of them. You should only output the UCI notation of the move you want to make with no additional text."
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": input_text},
        ]
        
        prompt = self.pipeline.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )

        terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = self.pipeline(
            prompt,
            max_new_tokens=256,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
        )
        return outputs[0]["generated_text"][len(prompt):]

    def generatePrompt(self, board):
        message = "Here's the current board state:\n\n" + str(board) + "\n\n"
        message += "Here's a list of possible moves:\n- "
        message += "\n- ".join(board.getLegalMoves()) + "\n\n"
        message += "Please make a move by choosing one of the above options. You should only output the UCI notation of the move you want to make with no additional text."
        return message


if __name__ == "__main__":
    mh_llama3 = MHLLama3()
    board = MHChess()
    for i in range(10):
        move, ans = mh_llama3.makeMove(board)
        print(move, ans)
        board.makeMove(move)
    