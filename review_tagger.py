import os
import random
import signal
import msvcrt
import sys

# 사용법: python review_tagger.py [영화제목]
# 영화 리뷰 파일들은 [영화제목] 폴더 안에 있어야 함 -> movie.tgz 파일 압축 해제하면 나오는 디폴트 구조를 사용하면 됨.
# review_tagger.py
# [영화제목]/[번호]_[영화제목]_long.txt
# 처음 전체 리뷰가 나오고 skip할 것이냐고 물어봄 -> y/n/q 로 대답
# n 입력시 각각의 문장마다 y/n/q로 스포일러 존재 여부 태깅
# q는 즉시종료

sentenceCount = 0
parsed = []

def signal_handler(signal, frame):
	out = open("./%s/result/data" % movie_dir)
	out.write(sentenceCount)
	out.write("\n")
	for item in parsed:
		out.write("%s\n" % item)
	out.close()

def writeSpoiler(movie_dir):
	global sentenceCount
	movie_name = movie_dir
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
		elif skipInput.lower() == b'q':
			sys.exit(1)



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

	writeSpoiler(sys.argv[1])