from collections import OrderedDict
from hypothesis  import HealthCheck, given, settings
from hypothesis.strategies \
                 import characters, composite, lists, sampled_from, text
from io          import StringIO
from operator    import add
from pytest      import raises

from po import ParseError, Reader, Token, Writer, END, tokenize as tk

def tokenize(lines):
	return list(tk(lines))

def test_tokenize_empty_file():
	assert tokenize([]) == []

def test_tokenize_empty_lines():
	assert tokenize(["  \n", "\n", "\t  \t\n"]) == [Token('nil', None)]*3

def test_tokenize_comments():
	assert (tokenize(["# foo\n", "#. bar baz\n"]) ==
	        [Token('#', ' foo'), Token('#.', ' bar baz')])

def test_tokenize_keywords():
	assert (tokenize(["foo bar"]) ==
	        [Token('keyword', 'foo'), Token('keyword', 'bar')])

def test_tokenize_strings():
	assert (tokenize([r' "foo\nbar" "spam"']) ==
	        [Token('string', r'foo\nbar'), Token('string', 'spam')])

def test_tokenize_unterminated_string():
	with raises(ParseError, match="Unterminated string"):
		tokenize(['  "foo', 'bar"'])

def test_tokenize_unknown_character():
	with raises(ParseError, match="Unknown character"):
		tokenize(['foo%'])

def detokenize(tokens):
	text = []; nl = True; kw = False
	for t in tokens:
		if t.type == 'nil':
			if not nl: text.append('\n')
			text.append('\n'); nl = True
		elif t.type.startswith('#'):
			if not nl: text.append('\n')
			text.append(t.type + t.value + '\n'); nl = True
		elif t.type == 'keyword':
			if not nl: text.append(' ')
			text.append(t.value); nl = False
		elif t.type == 'string':
			if not nl: text.append(' ')
			text.append('"' + t.value + '"'); nl = False
		else: # pragma: no cover
			raise ValueError("Invalid token list")
	return ''.join(text)

@composite
def tokens(draw):
	t = draw(sampled_from(['nil', '#', '#.', 'keyword', 'string']))
	if t == 'nil':
		return Token(t, None)
	elif t[0] == '#':
		s = draw(characters(whitelist_categories=['Zs']))
		v = draw(text(alphabet=characters(
			blacklist_categories=['Zl', 'Zp', 'Cc', 'Cs', 'Cn']
		)))
		return Token(t, s + v)
	elif t == 'keyword':
		v = draw(text(min_size=1, alphabet=characters(
			whitelist_categories=['Lu', 'Ll', 'Lt', 'Lm', 'Lo'],
			max_codepoint=128 # ASCII
		)))
		return Token(t, v)
	elif t == 'string':
		v = draw(text(min_size=1, alphabet=characters(
			blacklist_categories=['Cc', 'Cs', 'Cn']
		)))
		v = (v.replace('\\', r'\\')
		      .replace('\r', r'\r')
		      .replace('\n', r'\n')
		      .replace('\"', r'\"'))
		return Token(t, v)

@settings(suppress_health_check=[HealthCheck.too_slow])
@given(lists(tokens()))
def test_tokenize_detokenize(tokens):
	assert tokenize(StringIO(detokenize(tokens))) == tokens
