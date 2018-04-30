import os
import random
import signal
import msvcrt
import sys

sentenceCount = 0
parsed = []

def signal_handler(signal, frame):
	out = open("./%s/result/data" % movie_dir)
	out.write(sentenceCount)
	out.write("\n")
	for item in parsed:
		out.write("%s\n" % item)
	out.close()

def writeSpoiler(movie_dir, movie_name):
	global sentenceCount
	s = len([name for name in os.listdir(".\\%s" % movie_dir)])
	# print(s)
	try:
		parseResult = open("./%s/result/data" % movie_dir)
		sentenceCount = int(parseResult.readline())
		for line in parseResult.readlines():
			parsed.append(int(line.strip()))
		parseResult.close()
	except Exception as e:
		# raise e
		print("no such file")
		

	while True:
		nextTarget = random.randrange(s)
		if nextTarget in parsed:
			continue
		reviewFile = open("./%s/%d_%s_long.txt" % (movie_dir, nextTarget, movie_name), 'r', encoding="UTF8")
		reviewSentence = [sentence.strip() for sentence in reviewFile.readlines()]
		filter(lambda x: len(x) > 0, reviewSentence)
		result = checkReview(reviewSentence)
		if result is None:
			continue
		resultFile = open("./%s/result/%d_%s.txt" % (movie_dir, nextTarget, movie_name), 'w', encoding="UTF8")
		resultFile.write(result)
		sentenceCount += len(reviewSentence)
		parsed.append(nextTarget)
		reviewFile.close()
		resultFile.close()
		out = open("./%s/result/data" % movie_dir, 'w')
		out.write(str(sentenceCount))
		out.write("\n")
		for item in parsed:
			out.write("%s\n" % item)
		out.close()
		print(sentenceCount)

def checkReview(review):
	# review: list of sentence
	print("---------------")
	print("\n".join(review)+"\nSKIP?(Y/N)", end="")
	while True:
		skipInput = msvcrt.getch()
		if skipInput.lower() == b"y":
			print("\r--SKIPPED--")
			return None
		elif skipInput.lower() == b'n':
			print("---------------")
			return "\n".join([tag(x) for x in review])




def tag(sentence):
	while True:
		print("\n"+sentence)
		userInput = msvcrt.getch()
		if userInput.lower() in [b'y', b'p']:
			return "P "+sentence
		elif userInput.lower() == b"n":
			return "N "+sentence
		elif userInput.lower() == b'q':
			sys.exit(1)


if __name__ == '__main__':
	writeSpoiler("신과함께", "신과함께")