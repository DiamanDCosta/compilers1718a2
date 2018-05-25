
import plex



class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass



class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """
      def __init__(self):
           self.st = {}
	
	 def create_scanner(self,fp):
		""" Creates a plex scanner for a particular grammar 
		to operate on file object fp. """

		# define some pattern constructs
		letter = plex.Range("AZaz")
		digit = plex.Range("09")
		identifier = letter + plex.Rep(letter|digit)
	  	keyword = plex.Str('print')
	   	NotOp = plex.Str('not')
      		AndOrOp = plex.Str('and','or')
	  	equals = plex.Str('=')
	  	parenthesis = plex.Any('()')
		space = plex.Rep1(plex.Any(' \n\t'))
	  	boolFalse = plex.NoCase(plex.Str('false','f','0'))
		boolTrue = plex.NoCase(plex.Str('true','t','1'))


		# the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
		lexicon = plex.Lexicon([
			(identifier,'IDENTIFIER'),
			(keyword,plex.TEXT),
			(NotOp,plex.TEXT),
      			(AndOrOp,plex.TEXT),
			(equals,plex.TEXT),
			(parenthesis,plex.TEXT),
			(space,plex.IGNORE),
			(boolFalse,'FALSE'),
     			(boolTrue,'TRUE')
			])
		
		# create and store the scanner object
		self.scanner = plex.Scanner(lexicon,fp)
		
		# get initial lookahead
		self.la, self.val = self.next_token()


	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		
		return self.scanner.read()		

	
	def position(self):
		""" Utility function that returns position in text in case of errors.
		Here it simply returns the scanner position. """
		
		return self.scanner.position()
	

	def match(self,token):
		""" Consumes (matches with current lookahead) an expected token.
		Raises ParseError if anything else is found. Acquires new lookahead. """ 
		
		if self.la==token:
			self.la,self.val = self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	
	def parse(self,fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		
		# create the plex scanner for fp
		self.create_scanner(fp)
		
		# call parsing logic
		self.session()
	
	def stmtList(self):
		if self.la == 'IDENTIFIER' or self.la == 'Print':
			self.stmt()
			self.stmtList()
		elif self.la is None:
			return
			
	def stmt(self):
		if self.la == 'IDENTIFIER':
			self.match('IDENTIFIER')
			self.match('=')
			self.expr()
		elif self.la == 'print':
			self.match('print')
			self.expr()
		else:
			raise ParseError("Expected identifier or print keyword")
			 	
	def expr(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'TRUE' or self.la == 'FALSE':
			self.term()
			self.termTail()
		else:
			ParseError('Expected (,identifier or t-f')
			
	def termTail(self):
		if self.la == 'and' or self.la == 'or':
			self.OP1()
			self.term()
			self.termTail()
		elif self.la in ('identifier','print',None,')'):
			return
		else:
			raise ParseError('Expected \'and\' or \'or\'')
			
			
	def term(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'TRUE' or self.la == 'FALSE' or self.la == 'not':
			self.factor()
			self.factorTail()
		else:
			raise ParseError('Expected (,identifier or t-f')
			
			
	def factor_tail(self):
		if self.la == 'not':
				self.NotOp()
				self.Factor()
				self.Factor_tail()
		elif self.la =='and' or self.la=='or' or self.la =='print' or self.la =='IDENTIFIER' or self.la == ')' or self.la is None:
				return
		else:
			raise ParseError('Expected not')
	
	def factor(self):
		if self.la =='(':
				self.match('(')
				self.expr()
				self.match(')')
		elif self.la =='IDENTIFIER':
				self.match('IDENTIFIER')
		elif self.la == 'TRUE':
				self.match('TRUE')
		elif self.la == 'FALSE':
				self.match('FALSE')
		else:
				raise ParseError('error expected for identifier, t-f')	
	def AndOrOp(self):
		if self.la == 'and':
				self.match('and')
		elif self.la == 'or':
				self.match('or')
		else:
				raise ParseError('Expected and-or')
	def multop(self):
		if self.la == 'not':
				self.match('not')
		else:
				raise ParseError('Expected not')
		
# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
	with open("test.txt","r") as fp:

		try:
			parser.parse(fp)
		except ParseError as perr:
			print(perr)
