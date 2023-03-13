import openai
import re

class Bookgpt:
    def __init__(self, message_history):
        openai.api_key = "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"
        self.message_history = message_history
    
    def predict(self,input):
        # tokenize the new input sentence
        self.message_history.append({"role": "user", "content": f"{input}"})

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", #10x cheaper than davinci, and better. $0.002 per 1k tokens
            messages= self.message_history
        )
        #Just the reply:
        reply_content = completion.choices[0].message.content#.replace('```python', '<pre>').replace('```', '</pre>')
        print(reply_content)
        print(type(reply_content))
        self.message_history.append({"role": "assistant", "content": f"{reply_content}"}) 
        
        # get a list of reply_content 
        # delete number and punctuation
        reply_content = re.sub('[0-9.]+', '', reply_content)
        response = list(reply_content.split("\n"))
        response = list(map(lambda x: x.strip('"\' \n\t'), response))
        print(response)
        print(type(response))
        return response

#api_key = "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"

if __name__ == "__main__":
    message = [{"role": "user", "content": f"You are a book suggestion bot. I will specify the subject matter in my messages, and you will reply with 5 books that includes the subjects I mention in my messages. ONLY reply BOOK TITLE without author for further input. If you understand, say OK."},
                {"role": "assistant", "content": f"OK"}]
    
    #message_history = [{"role": "user", "content": f"You are a book suggestion robot. I'll specify the first words of the title in the message, and you will reply with 2 titles that start with the words I mentioned in the message. Only reply book information for further input. If you understand, say OK."},
    #                   {"role": "assistant", "content": f"OK"}]

    bookgpt1 = Bookgpt(message)
    #bookgpt1.predict("I am a Edinburgh informatics student, I like to read books to prepare for new semester. Module name is Text Technologies for Data Science.")
    bookgpt1.predict("stardew valley")
