from transformers import AutoTokenizer, LlamaForCausalLM
from mh_agent import MHAgent
from mh_chess import MHChess

class MHLLama2(MHAgent):
    def __init__(self, model_name='meta-llama/Llama-2-7b-chat-hf'):
        self.model_name = model_name
        self.model = LlamaForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.name = self.getname()

    def getname(self):
        if '7b-chat' in self.model_name:
            return 'Llama2-7b-chat'
        elif '70b-chat' in self.model_name:
            return 'Llama2-70b-chat'

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
        inputs = self.tokenizer(input_text, return_tensors="pt")
        res_ids = self.model.generate(inputs.input_ids, max_length=1000)
        ans = self.tokenizer.decode(res_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return ans

    def generatePrompt(self, board):
        template = '<s>[INST] <<SYS>>\n{system_message}<</SYS>>\n\n{message} [/INST]'
        system_message = "You are a professional chess player. You are playing a game of chess. It's your turn to make a move. You will get a list of legal moves you can make. You should choose one of them. You should only output the UCI notation of the move you want to make with no additional text."
        message = "Here's the current board state:\n\n" + str(board) + "\n\n"
        message += "Here's a list of possible moves:\n- "
        message += "\n- ".join(board.getLegalMoves()) + "\n\n"
        message += "Please make a move by choosing one of the above options."
        return template.format(system_message=system_message, message=message)


if __name__ == "__main__":
    mh_llama2 = MHLLama2()
    board = MHChess()
    for i in range(10):
        move, status, ans = mh_llama2.makeMove(board)
        print(ans, status)
        board.makeMove(move)
    