import numpy as np
from sklearn.naive_bayes import MultinomialNB

DELIM = "+++$+++"
all_genres = set()
all_words = set()

def transform_word(word):
    return word.lower().strip().strip("?").strip(".").strip("!")

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

def bag_of_words(convo):
    bag = { word: 0 for word in all_words }
    for line in convo["lines"]:
        for word in line.split(" "):
            bag[transform_word(word)] += 1

    return bag.values()

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


print len(data)
print len(training_data)
print len(hold_out_data)

print len(all_words)

print max(bag_of_words(data[2]))

training_bags = [bag_of_words(x) for x in training_data]
training_labels = [simplify_rating(x["movie"]["rating"]) for x in training_data]

print "Training Classifier...."
nb_classifier = MultinomialNB()
nb_classifier.fit(training_bags, training_labels)

print "Training Data Acc:"
print nb_classifier.score(training_bags, training_labels)


print "Hold Out Data Acc:"
print nb_classifier.score([bag_of_words(x) for x in hold_out_data], [simplify_rating(x["movie"]["rating"]) for x in hold_out_data])



