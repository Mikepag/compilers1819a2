#!/usr/bin/env python3
# -*- coding: utf_8 -*-

"""
Example of recursive descent parser written by hand using plex module as scanner
NOTE: This progam is a language recognizer only.

Sample grammar from p.242 of:
Grune, Dick, Jacobs, Ceriel J.H., "Parsing Techniques, A Practical Guide" 2nd ed.,Springer 2008.

Session  -> Facts Question | ( Session ) Session
Facts    -> Fact Facts | ε
Fact     -> ! string
Question -> ? string

FIRST sets
----------
Session:  ( ? !
Facts:    ε !
Fact:     !
Question: ?

FOLLOW sets
-----------
Session:  # )
Facts:    ?
Fact:     ! ?
Question: # )
  

"""


import plex



class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass



class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """
	
	def create_scanner(self,fp):
		""" Creates a plex scanner for a particular grammar 
		to operate on file object fp. """

		# define some pattern constructs
		decimalDigit = plex.Range('09')
		binaryDigit = plex.Range('01')
		letter = plex.Range('azAZ')
		
		equals = plex.Str('=')
		leftPar = plex.Str('(')
		rightPar = plex.Str(')')
		space = plex.Any(' \n\t')
		binaryNumber = plex.Rep1(binaryDigit)
		name = letter + plex.Rep(letter|decimalDigit)
		printKeyword = plex.Str('print')
		andOperator = plex.Str('and')			
		orOperator = plex.Str('or')
		xorOperator = plex.Str('xor')

		# the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
		lexicon = plex.Lexicon([
			(space,plex.IGNORE),
			(leftPar, plex.TEXT),		#plex.TEXT (?)
			(rightPar, plex.TEXT),		#plex.TEXT (?)
			(equals, plex.TEXT),		#plex.TEXT (?)
			(printKeyword, plex.TEXT),
			(binaryNumber, 'BINARY_NUM'),
			(andOperator, plex.TEXT),
			(orOperator, plex.TEXT),
			(xorOperator, plex.TEXT),
			(name, 'ID')				#Identifier must be at the bottom of the lexicon so that keywords are not misidentified as Ιdentifiers.
			])
		
		# create and store the scanner object
		self.scanner = plex.Scanner(lexicon,fp)
		
		# get initial lookahead
		self.la,self.val = self.next_token()


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
		self.stmt_list()
	
			
	def stmt_list(self):
		""" Stmt_list -> Stmt Stmt_list | ε """
		
		if self.la=='ID' or self.la=='PRINT':
			self.stmt()
			self.stmt_list()
		elif self.la == None:
			return
		else:
			raise ParseError("in session: id or print expected")
			 	
	
	def stmt(self):
		""" Stmt -> id = Expr | print Expr """
		
		if self.la=='id':
			self.match('id')
			self.match('equals')
			self.expr()
		elif self.la=='print':	
			self.match('print')
			self.expr()
		else:
			raise ParseError("in facts: id or print expected")
	
	
	def expr(self):
		if self.la=='lpar' or self.la=='ID' or self.la=='BINARY_NUM':
			self.term()
			self.term_tail
		else:
			raise ParseError("in facts: id or print expected")

	def term_tail(self):
		if self.la=='xor':
			self.match('xor')
			self.term()
			self.term_tail()
		elif self.la=='rPar' or self.la=='ID' or self.la=='print':
			return
		else:
			raise ParseError("in facts: id or print expected")

	def term(self):
		if self.la=='lPar' or self.la=='ID' or self.la=='BINARY_NUM':
			self.factor()
			self.factor_tail()
		else:
			raise ParseError("in facts: id or print expected")
		
	def factor_tail(self):
		if self.la=='or':
			self.match('or')
			self.factor()
			self.factor_tail()
		elif self.la=='rPar' or self.la=='xor' or self.la=='ID' or self.la=='print':
			return
		else:
			raise ParseError("in facts: id or print expected")

	def factor(self):
		if self.la=='lPar' or self.la=='ID' or self.la=='BINARY_NUM':
			self.atom()
			self.atom_tail()
		else:
			raise ParseError("in facts: id or print expected")

	def atom_tail(self):
		if self.la=='and':
			self.match('and')
			self.atom()
			self.atom_tail()
		elif self.la=='rPar' or self.la=='or' or self.la=='xor' or self.la=='ID' or self.la=='print':
			return
		else:
			raise ParseError("in facts: id or print expected")

	def atom(self):
		if self.la=='lPar':
			self.match('lPar')
			self.expr()
			self.match('rPar')
		elif self.la=='ID':
			self.match('ID')
		elif self.la=='BINARY_NUM':
			self.match('BINARY_NUM')
		else:
			raise ParseError("in facts: id or print expected")



		
# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
with open("recursive-descent-parsing.txt","r") as fp:

	# parse file
	try:
		parser.parse(fp)
	except plex.errors.PlexError:
		_,lineno,charno = parser.position()	
		print("Scanner Error: at line {} char {}".format(lineno,charno+1))
	except ParseError as perr:
		_,lineno,charno = parser.position()	
		print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))

