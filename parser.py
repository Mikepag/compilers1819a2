#!/usr/bin/env python3
# -*- coding: utf_8 -*-

"""
GRAMMAR
-------
Stmt_list   -> Stmt Stmt_list | ε
Stmt        -> id equals Expr | print Expr
Expr        -> Term Term_tail
Term_tail   -> xor Term Term_tail | ε
Term        -> Factor Factor_tail.
Factor_tail -> or Factor Factor_tail | ε
Factor      -> Atom Atom_tail
Atom_tail   -> and Atom Atom_tail | ε
Atom        -> lPar Expr rPar | id | number

FIRST sets
----------
Stmt_list:		id print
Stmt:			id print
Term_tail:		xor
Term:			lPar id number
Factor_tail:	or
Factor:			lPar id number
Atom_tail:		and
Atom:			lPar id number
Expr:			lPar id number

FOLLOW sets
-----------
Stmt_list:		∅
Stmt:			id print
Term_tail:		rPar id print
Term:			rPar xor id print
Factor_tail:	rPar xor id print
Factor:			rPar or xor id print
Atom_tail:		rPar or xor id print
Atom:			rPar and or xor id print
Expr:			rPar id print

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
		self.lexicon = plex.Lexicon([
			(space,plex.IGNORE),
			(leftPar, plex.TEXT),
			(rightPar, plex.TEXT),
			(equals, plex.TEXT),
			(printKeyword, plex.TEXT),
			(binaryNumber, 'BINARY_NUM'),
			(andOperator, plex.TEXT),
			(orOperator, plex.TEXT),
			(xorOperator, plex.TEXT),
			(name, 'ID')				# Identifier must be at the bottom of the lexicon so that keywords are not misidentified as Ιdentifiers.
			])
		
		# create and store the scanner object
		self.scanner = plex.Scanner(self.lexicon,fp)
		
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
		if self.la=='ID' or self.la=='print':
			self.stmt()
			self.stmt_list()
		elif self.la == None:
			return
		else:
			raise ParseError("stmt_list: id or print expected")
			 	
	
	def stmt(self):
		if self.la=='ID':
			self.match('ID')
			self.match('=')
			self.expr()
		elif self.la=='print':	
			self.match('print')
			self.expr()
		else:
			raise ParseError("in stmt: id or print expected")
	
	
	def expr(self):
		if self.la=='(' or self.la=='ID' or self.la=='BINARY_NUM':
			self.term()
			self.term_tail
		else:
			raise ParseError("in expr: (, id or binary number expected")

	def term_tail(self):
		if self.la=='xor':
			self.match('xor')
			self.term()
			self.term_tail()
		elif self.la==')' or self.la=='ID' or self.la=='print' or self.la==None:
			return
		else:
			raise ParseError("in term_tail: xor, rpar, id or print expected")

	def term(self):
		if self.la=='(' or self.la=='ID' or self.la=='BINARY_NUM':
			self.factor()
			self.factor_tail()
		else:
			raise ParseError("in term: (, id or binary number expected")
		
	def factor_tail(self):
		if self.la=='or':
			self.match('or')
			self.factor()
			self.factor_tail()
		elif self.la==')' or self.la=='xor' or self.la=='ID' or self.la=='print' or self.la==None:
			return
		else:
			raise ParseError("in factor_tail: or, rPar, xor, id or print expected")

	def factor(self):
		if self.la=='(' or self.la=='ID' or self.la=='BINARY_NUM':
			self.atom()
			self.atom_tail()
		else:
			raise ParseError("in factor: (, id or binary number expected")

	def atom_tail(self):
		if self.la=='and':
			self.match('and')
			self.atom()
			self.atom_tail()
		elif self.la==')' or self.la=='or' or self.la=='xor' or self.la=='ID' or self.la=='print' or self.la==None:
			return
		else:
			raise ParseError("in atom_tail: and, ), or, xor, id or print expected")

	def atom(self):
		if self.la=='(':
			self.match('(')
			self.expr()
			self.match(')')
		elif self.la=='ID':
			self.match('ID')
		elif self.la=='BINARY_NUM':
			self.match('BINARY_NUM')
		else:
			raise ParseError("in atom: (, id or binary number expected")



		
# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
#with open("recursive-descent-parsing.txt","r") as fp:
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

