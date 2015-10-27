from collections import defaultdict
from collections import Counter
from random import randint
DELIM = "+++$+++"
all_genres = set()
all_words = set()

def transform_word(word):
    return word
    #return word.lower().strip().strip("?").strip(".").strip("!")

def parse_data(movies_file_name, lines_file_name, conv_file_name):

    lines = {}
    movies = []
    conversations = []

    with open(lines_file_name) as lines_file:
        for line in lines_file:
            line_id, speaker_id, movie_id, speaker_name, line_text = line.split(DELIM)
            for word in line_text.split(' '):
                all_words.add(transform_word(word))

            lines[line_id.strip()] = line_text.strip()

    with open(movies_file_name) as movies_file:
        for line in movies_file:
            indx, title, year, rating, votes, genres = line.split(DELIM)
            genres = [x.strip()[1:-1] for x in genres.strip()[1:-1].split(",")]
            all_genres.update(genres)
            movies.append({"title": title.strip(), "rating": float(rating.strip()), "genres": genres})

    with open(conv_file_name) as conv_file:
        for line in conv_file:
            u, u2, movie_id, conv_line_idxs = line.split(DELIM)
            movie = movies[int(movie_id.strip()[1:])]
            conversations.append({
                "movie": movie,
                "lines": [lines[idx.strip("' ")] for idx in conv_line_idxs.strip()[1:-1].split(",")]
            })


    return conversations
def simplify_rating(rating):
    if rating < 3: return "bad"
    if rating < 7: return "ok"
    else: return "good"



prefix="data/cornell-movie-dialogs-corpus/"
data=parse_data(prefix + "movie_titles_metadata.txt", prefix + "movie_lines.txt",
    prefix + "movie_conversations.txt")

training_data=data[:int(.7*len(data))]
hold_out_data=data[len(training_data):]

labels = ["bad", "ok", "good"]


print(len(data))
print(len(training_data))
print(len(hold_out_data))
print(len(all_words))
training_labels = [simplify_rating(x["movie"]["rating"]) for x in training_data]
hold_labels = [simplify_rating(x["movie"]["rating"]) for x in hold_out_data]
bad = defaultdict(lambda :Counter())
ok = defaultdict(lambda :Counter())
good = defaultdict(lambda :Counter())
def build(dic,x):
    for line in x["lines"]:
        line = [transform_word(word) for word in line.split()]
        for first, second in zip(line, line[1:]):
            dic[first].update([second])
print("building")
for x,rating in zip(training_data, training_labels):
    if rating == 'bad':
        build(bad,x)
    if rating == 'ok':
        build(ok,x)
    if rating == 'good':
        build(good,x)
def norm(x):
    if x>0:
        return 1
    return 0
def score(dicts, x):
    scores = [1,1,1]
    for line in x["lines"]:
        line = [transform_word(word) for word in line.split()]
        for first, second in zip(line, line[1:]):
            sc = []
            for d in dicts:
                total = sum(d[first].values())
                if total!=0:
                    sc.append(d[first][second]/total)
                else:
                    sc.append(0)
            scores[sc.index(max(sc))]+=1
    return scores
def test(data, labels):
    #diff = 0
    right = 0
    for x,rating in zip(data, labels):
        scores = score((good, ok, bad), x)
        total = sum(scores)
        scores = [x/total for x in scores]
        s = scores[0] * 10 + scores[1] * 5 + scores[2] * 1
        if simplify_rating(s)==simplify_rating(x['movie']['rating']):
            right+=1
        #diff += round(abs(s-x['movie']['rating']),1)
    return (right / len(data))

#print("Training acc")
#print(test(training_data, training_labels))
print("Testing acc")
print(test(hold_out_data, hold_labels))
