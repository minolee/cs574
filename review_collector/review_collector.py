import urllib.request
import http.client
import html.parser
def get():
	url = "https://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?code=172454&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false&page=1"
	data = urllib.request.urlopen(url)
	print(data.status, data.reason)
	print(data.read().decode("utf8"))

def get_naver_movie_review(movie_code):
	page_count = 1
	last = []
	while True:
		url = "https://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?code=%d&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false&page=%d" % (movie_code, page_count)
		data = urllib.request.urlopen(url)
		#print("\r%d" % page_count, flush=True, end="")
		if data.status != 200:
			break
		n = NaverHTMLParser()
		page = n.getReview(data.read().decode("utf8"))
		if len(last) > 0 and last[-1] == page[-1]: break
		for item in page:
			yield item
		page_count += 1
		last = page

def get_daum_movie_review(movie_code):
	page_count = 1
	last = []
	while True:
		url = "http://movie.daum.net/moviedb/grade?movieId=%d&type=netizen&page=%d" % (movie_code, page_count)
		data = urllib.request.urlopen(url)
		print("\r%d" % page_count, flush=True, end="")
		if data.status != 200:
			break
		n = DaumHTMLParser()
		page = n.getReview(data.read().decode("utf8"))
		if len(last) > 0 and last[-1] == page[-1]: break
		for item in page:
			yield item
		page_count += 1
		last = page
	

class MovieHTMLParser(html.parser.HTMLParser):
	def __init__(self):
		super().__init__()
		self.parseMode = 0
		self.reviews = []

	def getReview(self, html):
		self.reviews = []
		self.feed(html) # add review data to self.reviews when feeding html
		
		return self.reviews


class NaverHTMLParser(MovieHTMLParser):

	def handle_starttag(self, tag, attrs):
		if tag == "div":
			if ("class", "score_reple") in attrs:
				self.parseMode = 1
			if ("class", "star_score") in attrs:
				self.parseMode = 2
			if ("class", "btn_area") in attrs:
				self.parseMode = 3
		if tag == "span" and self.parseMode == 10:
			self.parseMode = 11
		if tag == "p" and self.parseMode == 1:
			self.parseMode = 10
		
	def handle_data(self, data):
		if self.parseMode == 10:
			self.reviews.append(data)

	def handle_endtag(self, tag):
		if tag == "div":
			self.parseMode = 0
		if tag == "p":
			self.parseMode = 0
		if tag == "span" and self.parseMode == 11:
			self.parseMode = 10

class DaumHTMLParser(MovieHTMLParser):
	def handle_starttag(self, tag, attrs):
		if tag == "p" and ("class", "desc_review") in attrs:
			self.parseMode = 1

	def handle_data(self, data):
		if self.parseMode == 1:
			self.reviews.append(data.strip())
	def handle_endtag(self, tag):
		self.parseMode = 0

if __name__ == '__main__':
	for review in get_daum_movie_review(96030):
		print(review)
	# codes = open("naver_moviecode", "r", encoding="UTF8")
	# for line in codes.readlines():
	# 	movie_name, movie_code = line.strip().split(",")
	# 	print()
	# 	print(movie_name)
	# 	f = open("naver_%s.txt" % movie_name, "w", encoding="UTF8")
	# 	for review in get_naver_movie_review(int(movie_code)):
	# 		f.write(review+"\n")
	# 	f.close()
	# codes.close()