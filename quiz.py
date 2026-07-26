#Quiz
import random
def load_highscore():
    try:
        with open("highscore.txt","r")as f:
            return int(f.read())
    except FileNotFoundError:
        return 0
def save_highscore(score):
    with open("highscore.txt","w")as f:
        f.write(str(score))
all_questions=[
{"q": "What is 2+2? ", "a": "4"},
    {"q": "Capital of France? ", "a": "paris"},
    {"q": "What color is the sky? ", "a": "blue"},
    {"q": "How many sides does a triangle have? ", "a": "3"},
    {"q": "How many days in a year? ", "a": "365"},
    {"q": "What is 5x5? ", "a": "25"},
    {"q": "Capital of Romania? ", "a": "bucharest"},
    {"q": "How many months in a year? ", "a": "12"},
    {"q": "What is 10-3? ", "a": "7"},
    {"q": "How many hours in a day? ", "a": "24"},
]
x=int(input("How many questions? "))
questions=random.sample(all_questions,x)
score =0
for item in questions:
    answer=input(item["q"])
    if answer.lower()==item["a"]:
        print("Correct")
        score+=1
    else:
        print("Wrong Answer was:",item["a"])
print(f"\nScore: {score}/{len(questions)}")
highscore=load_highscore()
if highscore<score:
    print("New High score!")
    save_highscore(score)

    
