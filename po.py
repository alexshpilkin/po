from collections     import OrderedDict, namedtuple
from collections.abc import Mapping
from io              import StringIO

# FIXME Support obsolete (#~) and previous (#|) entries, multiple plurals

class ParseError(IOError):
	pass

Token = namedtuple('Token', ['type', 'value'])

END = Token('end', None)
NIL = Token('nil', None)

def tokenize(lines):
	for line in lines:
		line = line.lstrip().rstrip('\n')

		# Empty lines
		if not line or line.isspace():
			yield NIL
			continue

		# Comments
		if line[0] == '#':
			if len(line) == 1 or line[1].isspace():
				yield Token('#', line[1:])
			elif len(line) == 2 or line[2].isspace():
				yield Token(line[0:2], line[2:])
			else:
				raise ParseError("Unknown comment marker")
			continue

		# Keywords and strings
		while line:
			if line[0] == '"':
				i = 1
				while i < len(line):
					if line[i] == '"': break
					i += 2 if line[i] == '\\' else 1
				if i >= len(line):
					raise ParseError("Unterminated string")
				yield Token('string', line[1:i])
				line = line[i+1:]
			elif line[0].isalpha():
				i = 0
				while i < len(line) and line[i].isalpha():
					i += 1
				yield Token('keyword', line[:i])
				line = line[i:]
			else:
				raise ParseError("Unknown character")
			line = line.lstrip()

class Reader:
	__slots__ = ['Entry', 'file', '_header', '_peek', '_tokens']

	def __init__(self, entry, file):
		self.Entry   = entry
		self.file    = file
		self._tokens = tokenize(file)

		self._peek = None; self._next() # prime the pump
		self._header = None # FIXME

	def _next(self):
		p, self._peek = self._peek, next(self._tokens, END)
		return p

	def __iter__(self):
		return self

	def __next__(self):
		if self._peek.type == 'end':
			raise StopIteration

		entry = OrderedDict()

		# Comments
		while self._peek.type.startswith('#'):
			if self._peek.type in entry:
				raise ParseError("Discontinuous comment")
			key   = self._peek.type
			lines = [self._next().value]
			while self._peek.type == key:
				lines.append(self._next().value)
			entry[key] = tuple(lines)

		# Keywords
		while self._peek.type == 'keyword':
			if self._peek.type in entry:
				raise ParseError("Duplicate keyword")
			key   = self._next().value
			lines = []
			while self._peek.type == 'string':
				lines.append(self._next().value)
			if not lines:
				raise ParseError("No strings after keyword")
			entry[key] = tuple(lines)

		# Empty
		if self._peek.type not in ['nil', 'end']:
			raise ParseError("Expected end of entry")
		while self._peek.type == 'nil':
			self._next()

		return self.Entry(entry)

class Writer:
	__slots__ = ['file', '_end']

	def __init__(self, file):
		self.file = file
		self._end = ''

	def write(self, entry):
		print(end=self._end, file=self.file)

		for key in OrderedDict(entry):
			lines = entry[key]
			if key.startswith('#'):
				for line in lines:
					assert not line or line[0].isspace()
					print(key + line, file=self.file)
			else:
				if not lines: continue
				print(key, end=' ', file=self.file)
				for line in lines:
					print('"' + line + '"', file=self.file)

		self._end = '\n'

def _comment(key):
	def get(self): return self._getcomment(key)
	return property(get)

def _keyword(key):
	def get(self): return self._getkeyword(key)
	return property(get)

class Entry(Mapping):
	ESCAPES = {
		r'\"': '\"', r"\'": '\'', r'\\': '\\', r'\a': '\a', r'\b': '\b',
		r'\f': '\f', r'\n': '\n', r'\r': '\r', r'\t': '\t', r'\v': '\v',
	}

	@classmethod
	def unescape(cls, string):
		chunks = []; i = 0
		while True:
			j = string.find('\\', i)
			if j < 0: break
			chunks.append(string[i:j])
			raw = cls.ESCAPES.get(string[j:j+2], None)
			if raw is None:
				raise ParseError("Unknown escape")
			chunks.append(raw)
			i = j + 2
		chunks.append(string[i:])
		return ''.join(chunks)

	DEFAULT = ['#', '#.', '#,', '#|', 'msgctxt', 'msgid', 'msgstr']
	DEFAULT = OrderedDict((k, ()) for k in DEFAULT)

	def __init__(self, entries):
		if not all(k in self.DEFAULT for k in entries):
			raise ParseError("Unknown comment or keyword")
		self._dict = OrderedDict(entries)

	def __getitem__(self, key):
		return self._dict.get(key, self.DEFAULT[key])

	def __iter__(self):
		return iter(self._dict)

	def __len__(self):
		return len(self._dict)

	def __repr__(self):
		return '{}.Entry({!r})'.format(__name__, self._dict)

	def _getcomment(self, key):
		return '\n'.join(v[1:] for v in self[key])

	tcomment = _comment('#')
	pcomment = _comment('#.')

	LETTERS = set("abcdefghijklmnopqrstuvwxyz-")

	@property
	def flags(self):
		flags = set()
		for flag in self._getcomment('#,').split(','):
			flag = flag.strip()
			if not flag:
				continue
			if not all(c in self.LETTERS for c in flag):
				raise ParseError("Unknown flag")
			if flag in flags:
				raise ParseError("Duplicate flag")
			flags.add(flag)
		return flags

	@property
	def previous(self):
		# FIXME where to get Reader?
		entries = list(Reader(type(self), StringIO(self._getcomment('#|'))))
		if not entries:
			return None
		elif len(entries) == 1:
			return entries[0]
		else:
			raise ParseError("Multiple previous entries")

	def _getkeyword(self, key):
		return self.unescape(''.join(self[key]))

	# FIXME domain, plurals
	context = _keyword('msgctxt')
	id      = _keyword('msgid')
	string  = _keyword('msgstr')
