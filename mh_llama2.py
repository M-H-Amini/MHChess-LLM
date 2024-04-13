from transformers import AutoTokenizer, LlamaForCausalLM
from mh_agent import MHAgent
from mh_chess import MHChess

class MHLLama2(MHAgent):
    def __init__(self):
        self.model = LlamaForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
        self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")

    def makeMove(self, board):
        prompt = self.generatePrompt(board)
        ans = self.generateResponse(prompt)
        ##  Validate the move...
        ans = ans[ans.index('[/INST]')+8:].strip().rstrip()
        legal_moves = board.getLegalMoves()
        if ans in legal_moves:
            return ans, True
        return ans, False


    def generateResponse(self, input_text):
        inputs = self.tokenizer(input_text, return_tensors="pt")
        res_ids = self.model.generate(inputs.input_ids, max_length=1000)
        ans = self.tokenizer.decode(res_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return ans

    def generatePrompt(self, board):
        template = '<s>[INST] <<SYS>>\n{system_message}<</SYS>>\n\n{message} [/INST]'
        system_message = "You are a professional chess player. You are playing a game of chess. It's your turn to make a move. You should only answer with 4-character strings like 'e2e4'."
        message = "Here's the current board state:\n\n" + str(board) + "\n\n"
        message += "Here's a list of possible moves:\n- "
        message += "\n- ".join(board.getLegalMoves()) + "\n\n"
        return template.format(system_message=system_message, message=message)


if __name__ == "__main__":
    mh_llama2 = MHLLama2()
    board = MHChess()
    ans = mh_llama2.makeMove(board)
    print(ans)
    