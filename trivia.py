import requests
import base64
import argparse

def decode(text: str):
  return base64.b64decode(text).decode("utf-8")

class Question:
  def __init__(self, data):
    self.question = decode(data['question'])
    self.correct_answer = decode(data['correct_answer'])
    self.incorrect_answers = [decode(ans) for ans in data['incorrect_answers']]

  def answers(self):
    answers = set(self.incorrect_answers)
    answers.add(self.correct_answer)
    return list(answers)

class OpenTDB:
  types = ["multiple", "boolean"]
  difficulties = ["easy", "medium", "hard"]
  
  def get_categories():
    return requests.get("https://opentdb.com/api_category.php").json()['trivia_categories']

  def get_questions(params):
    params.update({"encode": "base64"})
    # no error handling lol
    return [Question(question) for question in requests.get("https://opentdb.com/api.php", params=params).json()['results']]

categories = OpenTDB.get_categories()
category_offsets = categories[0]['id'] - 1
category_choices = [cat['id']-category_offsets for cat in categories]
category_metavar = dict([(cat['id']-category_offsets, cat['name']) for cat in categories])

parser = argparse.ArgumentParser()
parser.add_argument('--type', choices=OpenTDB.types, default=None)
parser.add_argument('--amount', type=int, metavar='1..50', choices=range(1, 50), default=1)
parser.add_argument('--category', type=int, metavar=category_metavar, choices=category_choices, default=None, help="The category to choose questions from, selected by the number.")
parser.add_argument('--difficulty', choices=OpenTDB.difficulties, default=None)
args = parser.parse_args()
if args.category: args.category += category_offsets

def prompt_question(question):
  print(question.question)
  answers = question.answers()
  [print(f"[{i+1}] {answer}") for i, answer in enumerate(answers)]
  chosen_answer = None
  while True:
    try:
      chosen_answer = input("answer: ")
      chosen_answer = int(chosen_answer)
      if(chosen_answer > len(answers)):
        # this shouldn't be repeated but meh
        print(f"'{chosen_answer}' is not a valid question selection between 1 and {len(answers)}, try selecting again with a valid number.")
        continue
      break
    except ValueError:
      print(f"'{chosen_answer}' is not a valid question selection between 1 and {len(answers)}, try selecting again with a valid number.")
      continue
  if answers[chosen_answer-1] is question.correct_answer:
    print("Correct answer!")
    return True
  else: 
    print(f"Incorrect answer!\nThe correct answer was: [{answers.index(question.correct_answer)+1}] {question.correct_answer}")
    return False

questions = OpenTDB.get_questions(vars(args))
print("score:", len([question for question in questions if prompt_question(question)]), "/", len(questions))
