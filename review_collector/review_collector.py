import urllib.request
import http.client
import html.parser
import re
def getMovieReview(slotted_url, movie_code, parser, end_function, print_page=False):
	page_count = 1
	last = []
	while True:
		url = slotted_url % (movie_code, page_count)
		data = urllib.request.urlopen(url)
		if print_page: print("\r%d" % page_count, flush=True, end="")
		
		if data.status != 200:
			break
		page = parser.getReview(data.read().decode("utf8"))
		if end_function(page, last):
			break
		for item in page:
			if len(item) == 0:
				continue
			yield item
		last = page
		page_count += 1

def default_end_function(page, lastdata):
	if len(lastdata) > 0 and lastdata == page:
		return True
	if len(page) == 0:
		return True


def getNaverMovieReview(movie_code, longdata=False, print_page=False):
	short_url = "https://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?code=%d&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false&page=%d"
	long_url = "https://movie.naver.com/movie/bi/mi/review.nhn?code=%d&order=newest&page=%d"

	if not longdata:
		url = short_url
		parser = NaverHTMLParser()
	else:
		url = long_url
		parser = NaverLongMovieListParser(movie_code)
	return getMovieReview(url, movie_code, parser, default_end_function, print_page)
		
	# page_count = 1
	# last = []
	# while True:
	# 	url = "https://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?code=%d&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false&page=%d" % (movie_code, page_count)
	# 	longurl = "https://movie.naver.com/movie/bi/mi/review.nhn?code=%d&order=newest&page=%d" % (movie_code, page_count)
	# 	data = urllib.request.urlopen(url)
	# 	print("\r%d" % page_count, flush=True, end="")
	# 	if data.status != 200:
	# 		break
	# 	n = NaverHTMLParser()
	# 	page = n.getReview(data.read().decode("utf8"))
	# 	if len(last) > 0 and last == page: break
	# 	if len(page) == 0: break
	# 	for item in page:
	# 		if len(item) == 0: continue
	# 		yield item
	# 	page_count += 1
	# 	last = page

def getDaumMovieReview(movie_code):
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
		if len(last) > 0 and last == page: break
		if len(page) == 0: break
		for item in page:
			if len(item) == 0: continue
			yield item
		page_count += 1
		last = page
	

class MovieHTMLParser(html.parser.HTMLParser):
	def __init__(self):
		super().__init__()
		self.parseMode = 0

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

class NaverLongMovieListParser(MovieHTMLParser):
	def __init__(self, movie_code):
		super().__init__()
		self.movie_code = movie_code
	def getReview(self, html):
		self.reviews = []
		self.reviewLinkCodes = []
		self.feed(html)
		p = NaverLongReviewParser()
		for item in self.reviewLinkCodes:
			url = "https://movie.naver.com/movie/bi/mi/reviewread.nhn?nid=%d&code=%d&order=newest#tab" % (item, self.movie_code)
			data = urllib.request.urlopen(url).read().decode("utf8")
			self.reviews.append(p.getReview(data))
		print(self.reviews)
		return self.reviews
	def handle_starttag(self, tag, attrs):
		if tag == "ul" and ("class", "rvw_list_area") in attrs:
			self.parseMode = 1
		if self.parseMode == 1 and tag == "a":
			for item in attrs:
				if item[0] == "onclick" and "showReviewDetail" in item[1]:
					# print(item[1])
					self.reviewLinkCodes.append(int("".join(re.findall("\d", item[1]))))
					# print(len(self.reviewLinkCodes))
	def handle_endtag(self, tag):
		if tag == "div":
			self.parseMode = 0


class NaverLongReviewParser(MovieHTMLParser):
	def getReview(self, html):
		self.review = []
		# print(html)
		self.feed(html)
		r = "\n".join(self.review)
		#print(r)
		return r
	def handle_starttag(self, tag, attrs):
		if tag == "div" and ("class", "user_tx_area") in attrs:
			self.parseMode = 1
		if self.parseMode == 1 and tag == "p":
			self.parseMode = 10
	def handle_data(self, data):
		if self.parseMode == 10:
			self.review.append(data.replace("&nbsp", " "))
	def handle_endtag(self, tag):
		if tag == "div":
			self.parseMode = 0


class DaumHTMLParser(MovieHTMLParser):
	def handle_starttag(self, tag, attrs):
		if tag == "p" and ("class", "desc_review") in attrs:
			self.parseMode = 1

	def handle_data(self, data):
		if self.parseMode == 1:
			self.reviews.append(" ".join(data.strip().split("\n")))
	def handle_endtag(self, tag):
		self.parseMode = 0

if __name__ == '__main__':
	# f = open("daum_%s.txt" % "레디 플레이어 원","w", encoding="UTF8")

	# for review in getDaumMovieReview(96030):
	# 	f.write(review+"\n")
	# f.close()
	codes = open("naver_moviecode", "r", encoding="UTF8")
	for line in codes.readlines():
		if line.startswith("#"): continue
		movie_name, movie_code = line.strip().split(",")
		print()
		print(movie_name)
		f = open("naver_%s.txt" % movie_name, "w", encoding="UTF8")
		for review in getNaverMovieReview(int(movie_code), False, print_page=True):
			f.write(review+"\n")
		f.close()
	codes.close()