import urllib.request
import http.client
import html.parser
import re

reviewDivider = "------------div------------"

def getMovieReview(slotted_url, movie_code, parser, end_function, print_page=False):
	page_count = 1
	last = []
	while True:
		url = slotted_url % (movie_code, page_count)
		data = urllib.request.urlopen(url)
		if print_page: print("\r%d" % page_count, flush=True, end="")
		
		if data.status != 200:
			print(data.status)
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
	long_url = "https://movie.naver.com/movie/bi/mi/review.nhn?code=%d&page=%d"

	if not longdata:
		url = short_url
		parser = NaverHTMLParser()
	else:
		url = long_url
		parser = NaverLongMovieListParser(movie_code)
	return getMovieReview(url, movie_code, parser, default_end_function, print_page)

# def getDaumMovieReview(movie_code):
# 	page_count = 1
# 	last = []
# 	while True:
# 		url = "http://movie.daum.net/moviedb/grade?movieId=%d&type=netizen&page=%d" % (movie_code, page_count)
# 		data = urllib.request.urlopen(url)
# 		print("\r%d" % page_count, flush=True, end="")
# 		if data.status != 200:
# 			break
# 		n = DaumHTMLParser()
# 		page = n.getReview(data.read().decode("utf8"))
# 		if len(last) > 0 and last == page: break
# 		if len(page) == 0: break
# 		for item in page:
# 			if len(item) == 0: continue
# 			yield item
# 		page_count += 1
# 		last = page
	

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
		self.reviewLinkCodes = set()
		self.feed(html)
		p = NaverLongReviewParser()
		# print(self.reviewLinkCodes)
		for item in self.reviewLinkCodes:
			url = "https://movie.naver.com/movie/bi/mi/reviewread.nhn?nid=%d&code=%d&order=#tab" % (item, self.movie_code)
			data = urllib.request.urlopen(url).read().decode("utf8")
			self.reviews.append(p.getReview(data))
		# print(self.reviews)
		return self.reviews

	def handle_starttag(self, tag, attrs):
		if tag == "ul" and ("class", "rvw_list_area") in attrs:
			self.parseMode = 1
		if self.parseMode == 1 and tag == "a":
			for item in attrs:
				if item[0] == "onclick" and "showReviewDetail" in item[1]:
					# print(item[1])
					self.reviewLinkCodes.add(int("".join(re.findall("\d", item[1]))))
					# print(len(self.reviewLinkCodes))
	# def handle_data(self, data):
	# 	if self.parseMode == 1:
	# 		print(data)
	def handle_endtag(self, tag):
		if tag == "ul":
			self.parseMode = 0


class NaverLongReviewParser(MovieHTMLParser):
	def getReview(self, html):
		self.review = []
		self.reviewParts = []
		self.feed(html)
		r = "\n".join(self.review)
		# print(r)
		return r
	def handle_starttag(self, tag, attrs):
		if tag == "div" and ("class", "user_tx_area") in attrs:
			self.parseMode = 1
		if tag == "div" and (("class", "from_blog") in attrs or ("class", "cbox_module") in attrs):
			self.parseMode = 0
		if self.parseMode == 1 and tag == "p":
			self.parseMode = 10
		if len(self.reviewParts) > 0 and tag == "p":
			self.review.append("".join(self.reviewParts))
			self.reviewParts = []

	def handle_data(self, data):
		if self.parseMode == 10:
			d = self.postprocess(data)
			if len(d) > 1:
				self.reviewParts.append(d)

	def postprocess(self, reviewText):
		d = reviewText
		d = d.replace("&nbsp", " ")
		d = d.replace("\\xa0", " ")
		d = re.sub(r"(\\n|\\r)+", "\n", d)
		return d


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
	import getopt
	import sys
	optlist, args = getopt.getopt(sys.argv[1:], "la")
	# print(optlist)
	ld = False
	both = False
	for o, a in optlist:
		if o == "-l":
			ld = True
		if o == "-a":
			ld = False
			both = True
	codes = open("naver_moviecode", "r", encoding="UTF8")

	for line in codes.readlines():
		if line.startswith("#"): continue
		movie_name, movie_code = line.strip().split(",")
		print()
		print(movie_name)
		fn = "naver_%s" % movie_name
		if ld: fn += "_long"
		f = open("%s.txt" % fn, "w", encoding="UTF8")
		for review in getNaverMovieReview(int(movie_code), ld, print_page=True):
			f.write(review+"\n")
			if ld: f.write("%s\n" % reviewDivider)
		f.close()
		if both:
			f2 = open("naver_%s_long.txt" % movie_name, "W", encoding="UTF8")
			for review in getNaverMovieReview(int(movie_code), True, print_page=True):
				f2.write(review+"\n")
				f2.write("%s\n" % reviewDivider)
			f2.close()
	codes.close()