import re
import json

class Symbols(object):
	# Whitespace skips
	SKIP = 'SKIP'

	# List operator expanded in parser
	RANGE = 'RANGE'

	# Expression start/end
	LPAREN = 'LPAREN'
	RPAREN = 'RPAREN'

	# Primitives
	NUMBER = 'NUMBER'
	STRING = 'STRING'
	BOOLEAN = 'BOOLEAN'
	IDENTIFIER = 'IDENTIFIER'

	# Used internally for passing functions
	FUNCTION_REFERENCE = 'FUNCTION_REFERENCE'

	# Used internally for describing lists
	LIST = 'LIST'

number = ['^\-?[0-9]+\.?[0-9]*$', Symbols.NUMBER]
string = ['^\"[^\n\"]*\"$', Symbols.STRING]
whitespace = ['^[\s\n]+$', Symbols.SKIP]
comment = ['^;.+?\n$', Symbols.SKIP]
identifier = ['^[a-zA-Z\+\-\/\*\%\_\>\<=]*$', Symbols.IDENTIFIER]
boolTrue = ['true', Symbols.BOOLEAN]
boolFalse = ['false', Symbols.BOOLEAN]
lparen = ['(', Symbols.LPAREN]
rparen = [')', Symbols.RPAREN]
lel_range = ['..', Symbols.RANGE]
minus = ['- ', Symbols.RANGE]

class Patterns(object):
	ambiguous = [
	  ['^\-$', number]
	]
	exact = [
	  boolTrue,
	  boolFalse,
	  lparen,
	  rparen,
	  lel_range,
	  minus
	]
	tokens = [
	  whitespace,
	  comment,
	  number,
	  string,
	  identifier
	]

class Token(object):
	def __init__(self, t, value):
		self.type = t
		self.value = value
		self.is_token = True

	def to_string(self):
		return str(self.type)

	def __repr__(self):
		return json.dumps(self.__dict__) + "\n"

def create_token(t, value):
	return Token(t, value)

def tokenise(chars):
	tokens = []
	check = ""
	i = 0
	while i < len(chars):
		check += chars[i]

		# Check against exact patterns first
		if len(check) == 1:
			matched_exact_pattern = False
			for exact_str, symbol in Patterns.exact:
				if len(exact_str) + i <= len(chars):
					exact_check = check + chars[i + 1: i + len(exact_str)]
					if exact_check == exact_str:
						# Set the new i pointer
						i += len(exact_str) - 1

						exact_check = exact_check.strip()

						# Add the token to the list
						if symbol != Symbols.SKIP:
							tokens.append(create_token(symbol, exact_check))
						# Reset the check string
						check = ""

						# Exit from the token search
						matched_exact_pattern = True
						break
			if matched_exact_pattern:
				i += 1
				continue

		# Perform an ambiguous check to prioritise a pattern match
		if len(check) == 1 and i < len(chars) - 1:
			for re_str, symbol in Patterns.ambiguous:
				re_p = re.compile(re_str)
				if re_p.match(check):
					for t in symbol:
						re_p2 = re.compile(t[0])
						if re_p2.match(check) or re_p2.match(check + chars[i + 1]):
							i += 1
							check += chars[i]
							break

		# Test for tokens until a sucessful one is found
		for re_str, label in Patterns.tokens:
			re_p = re.compile(re_str)
			is_match_peek_check = False
			if re_p.match(check):
				if i == len(chars) - 1:
					# Add the token to the list
					if label != Symbols.SKIP:
						tokens.append(create_token(label, check.strip()))
					break
				# Peek ahead at the next charcters while it's still matching the same token
				peek_check = check
				for j in range(i + 1, len(chars)):
					peek_check += chars[j]
					re_p = re.compile(re_str)
					# Does checking with another character still match?
					if not re_p.match(peek_check):
						# If not, consider everything up until the last peekCheck the token
						check = peek_check[:-1]
						
						# Set tokeniser index to this point
						i = j - 1
						# Add the token to the list
						check = check.strip()
						if check and label != Symbols.SKIP:
							tokens.append(create_token(label, check))
						check = ""
						# Exit from the token search
						is_match_peek_check = True
						break
			if is_match_peek_check:
				break

		i += 1
	return tokens
