import requests
from bs4 import BeautifulSoup
import json

res = requests.get("https://law.stackexchange.com/questions")

print(res.text)

soup = BeautifulSoup(res.text, "html.parser")

print(soup)

questions_data = {
	"questions": []
}

questions = soup.select(".question-summary")

# get data for one question
# print(questions[0].select_one('.question-hyperlink').getText())

# get data for all questions
for que in questions: 
    q = que.select_one('.question-hyperlink').getText()
    vote_count = que.select_one('.vote-count-post').getText()
    views = que.select_one('.views').attrs['title']
    questions_data['questions'].append({
        "questions": q,
        "views": views,
        "vote_count": vote_count 
    })
    # print(views)
    # print(vote_count)
    # print(q)

json_data = json.dumps(questions_data)

print(json_data)

# copy output json from terminal and validate using the following site
# https://jsonlint.com/
# see README.txt for sample scraped data