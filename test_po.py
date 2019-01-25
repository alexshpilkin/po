from collections import OrderedDict
from sys         import stdin, stdout
from po          import ParseError, Reader, Token, Writer, tokenize
from pytest      import raises

def tok(lines):
	return list(tokenize(lines))

def test_tokenize_empty_file():
	assert tok([]) == []

def test_tokenize_empty_lines():
	assert tok(["  \n", "\n", "\t  \t\n"]) == [Token('nil', None)]*3

def test_tokenize_comments():
	assert (tok(["# foo\n", "#. bar baz\n"]) ==
	        [Token('#', ' foo'), Token('#.', ' bar baz')])

def test_tokenize_keywords():
	assert (tok(["foo bar"]) ==
	        [Token('keyword', 'foo'), Token('keyword', 'bar')])

def test_tokenize_strings():
	assert (tok([r' "foo\nbar" "spam"']) ==
	        [Token('string', r'foo\nbar'), Token('string', 'spam')])

def test_tokenize_unterminated_string():
	with raises(ParseError, match="Unterminated string"):
		tok(['  "foo', 'bar"'])

def test_tokenize_unknown_character():
	with raises(ParseError, match="Unknown character"):
		tok(['foo%'])
