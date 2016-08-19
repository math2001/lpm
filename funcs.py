from __future__ import print_function, division

def die(*mes, **kwargs):
	if len(mes) != 0:
		print(*mes, **kwargs)
	exit(0)

def make_good_path(*args):
	if type(args[0]) in (list, tuple):
		args = args[0]

	return os.path.normpath( os.path.join(*args) )

def confirm(question, default=None):
	rep = None
	yes = ('y', 'yes')
	no = ('n', 'no')
	while rep not in yes + no:
		rep = raw_input(question + ' (Y/N) ').lower()
		if rep == '' and default is not None:
			return default
		elif rep in yes:
			return True
		elif rep in no:
			return False


def ask(question, default=None):
	if default != None:
		question += ' ({})'.format(default)
	question += ' '
	ans = raw_input(question)
	return (ans if ans != '' else default)

def copytree(src, dst, symlinks=False, ignore=None):
	src = unicode("\\\\?\\" + src)
	dst = unicode("\\\\?\\" + dst)
	for item in os.listdir(src):
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isdir(s):
			shutil.copytree(s, d, symlinks, ignore)
		else:
			shutil.copy2(s, d)

def json_decode(json, is_file=False):
	if not is_file:
		return JSONDecoder().decode(json)

	with open(json, 'r') as fp: 
		return JSONDecoder().decode(fp.read())

def json_encode(py, path=False, nice=False):
	if nice is False:
		json = JSONEncoder().encode(py)
	else:
		json = json_dumps(py, indent=2, sort_keys=True)
	if not path:
		return json
	with open(path, 'w') as fp: 
		fp.write(json)

def error(*args, **kwargs):
	string = 'error: '
	for arg in args:
		string += str(arg) + ' '
	if kwargs.get('see_help', True):
		string += 'See npm-cache --help.'
	die(string)

def quote(el):
	return '"{}"'.format(el)

def are_in(*args, **kwargs):
	args = list(args)
	type = kwargs.get('type', 'all')
	iter = args.pop(-1)

	for arg in args:
		if type == 'all' and not arg in iter:
			return False
		if type == 'any' and arg in iter:
			return True
				
	if type == 'any':
		return False
	return True

def file_get_content(path):
	with open(path, 'r') as fp:
		return fp.read()

def file_set_content(path, content, mode='w'):
	with open(path, mode) as fp:
		fp.write(content)
	return True