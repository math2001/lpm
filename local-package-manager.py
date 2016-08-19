# -*- encoding: utf-8 -*-

#  ___
# /\_ \
# \//\ \    _____     ___ ___
#   \ \ \  /\ '__`\ /' __` __`\
#    \_\ \_\ \ \L\ \/\ \/\ \/\ \
#    /\____\\ \ ,__/\ \_\ \_\ \_\
#    \/____/ \ \ \/  \/_/\/_/\/_/
#             \ \_\
#              \/_/
# 
# local pacakge manager

from __future__ import print_function, division
import os, sys
import shutil, errno
import argparse
from json import JSONDecoder, JSONEncoder, dumps as json_dumps

from funcs import *

os.path.valid = make_good_path

args = sys.argv[1:]

CONFIG_FILE = 'C:/python/cmd_command/npm-cache/config.json'

class NiceList(list):

	""" add the `get` method """

	def get(self, index, default=None):
		try:
			return self.__getitem__(index)
		except IndexError:
			return default

	def __getslice__(self, *args, **kwargs):
		return NiceList(list.__getslice__(self, *args, **kwargs))



class Commands(object):

	""" All the command that can be directly called from the terminal. 
	It is in a class just to be cleaner. """

	def __get_path_to_install(self, dir):
		path = os.getcwd()
		if 'node_modules' in path:
			return path
		else:
			path = os.path.join(path, 'node_modules', dir)
			if not os.path.exists(path):
				os.makedirs(path)
			return path

	def __get_config(self):
		with open(CONFIG_FILE, 'r') as fp:
			config = json_decode(fp.read())
		return config

	def __save_config(self, config):
		""" just to fold it """
		return json_encode(config, CONFIG_FILE, False)

	def __get_package_file(self, path=os.getcwd(), kill=True):
		path = os.path.valid(path, 'package.json')
		if not os.path.exists(path):
			if kill:
				die('error: no package.json found in "{}". This package is not valid.\n'
					'       Impossible to install it'.format(
					os.path.dirname(path)))
			else:
				return False

		return path

	def __get_package_name(self, path):
		""" return the package **name** (saved in the package.json) """
		path = os.path.valid(path, 'package.json')
		if not os.path.exists(path):
			return False
		return json_decode(path, True)['name']

	def __get_direct_package(self, path, pck_to_remove=[]):
		packages = {}
		for entrie in os.listdir(path):
			if os.path.isdir(os.path.valid(path, entrie)):
				pck_file = self.__get_package_file(os.path.valid(path, entrie), False)

				if pck_file:
					pck_name = json_decode(pck_file, True)['name']
					if pck_name not in pck_to_remove:
						packages[pck_name] = os.path.valid(path, entrie)
		return packages

	def __get_cmd_help(self):
		return {
			"save": ["Save a key", "npm-cache save <key> <value>"],
			"get": ["Get a key", "npm-cache get <key>"],
			"install": ["Copy a folder into the current node_modules.", "npm-cache install <pck-name> --save|--save-dev"]
		}

	# real commands

	def global_help(self, special=False):
		
		with open('C:\python\cmd_command\local-package-manager\lpm.help', 'r') as fp:
			lpm_help = fp.read().splitlines()
			
		for i, line in enumerate(lpm_help):
			if line.startswith('<input '):
				# pause
				raw_input(line[8:]) if special else print()
			elif line.startswith('<u'):
				# underline
				print(line[2:] * len(lpm_help[i-1]))
			elif line.startswith('<spec '):
				print(line[6:]) if special else ''
			elif not line.startswith('<comment'):
				print(line)

	def set(self, args):
		"""
			Set a shortcut.
			$ npm-cache set <key> <path>
			no options
		"""
		if len(args) != 2:
			die('error: args', args)
		with open(CONFIG_FILE, 'r') as fp:
			config = json_decode(fp.read())

		if config.get(args[0], True) or confirm('This plugin is already set. Replace?'):
			config[str(args[0])] = str(args[1])
			with open(CONFIG_FILE, 'w') as fp:
				fp.write(json_encode(config, nice=True))
			print('The key "{}" has now for value "{}"'.format(*args))
		else:
			print('Not saved')

	def ls(self, args):
		"""
			List all the shortcut.
			$ npm-cache ls
			no options/args
		"""
		if args != []:
			die('error: args')
		config = self.__get_config()
		key_width = max([len(key) for key in config.keys()])
		path_width = max(len(path) for path in config.itervalues())
		header = '<key>'.ljust(key_width + 1) + ' : ' + '<path>'.ljust(path_width + 2) + ' ' + '(<pck_name>)'
		print(header)
		print('-' * len(header))
		for key in config:
			pck_name = self.__get_package_name(config[key])
			if not pck_name:
				pck_name = '!!invalid package. No package.json'
			print('"{key}"{space_1}: "{path}" {space_2}({pck_name})'.format(
				key=key, 
				space_1=' ' * (key_width - len(key)), 
				space_2=' ' * (path_width - len(config[key])), 
				path = config[key],
				pck_name=pck_name
			))

	def get(self, args):
		"""
			Get the value of a shortcut.
			$ npm-cache get <key>
			no options
		"""
		if len(args) != 1:
			die('error: args', args)

		with open(CONFIG_FILE, 'r') as fp:
			config = json_decode(fp.read())
			if not config.get(args[0], False):
				die('error: the key "{}" is not set'.format(args[0]))
			print("{}: \"{}\"".format(args[0], config[args[0]]))

	def delete(self, args):
		"""
			Delete a key (no undo)
			$ npm-cache delete <key>
			no options
		"""
		if len(args) != 1:
			error('args', args)

		key = args[0]
		config = self.__get_config()
		if config.get(key, False) is False:
			error('The key "{}" has not been set. `npm-cache ls` to list all your shortcuts'.format(key), see_help=False)

		value = config[key]

		if confirm('Delete the key "{}" that had for value "{}"'.format(key, value)):
			del config[key]
			self.__save_config(config)
			print('The key "{}" has been deleted!'.format(key))

	def install(self, args):
		"""
			Install a package.
			$ npm install <key|path> [--save] [--save-dev] [-v --verbose] [-p --is-path]
			If the key doesn't exists, it will ask you to use it as the path to the package to copy.
			If you want to use this behavior by default, just use the option `-is-path`

		"""
		if len(args) not in (1, 2, 3):
			die('error args:', args)

		if '--save-dev' in args:
			save = 'devDependencies'
		elif '--save' in args:
			save = 'dependencies'
		else:
			save = False

		is_path = are_in('-p', '--is-path', args, type='any')

		verbose = '-v' in args or '--verbose' in args

		package_file_path = self.__get_package_file(kill=False)
		if package_file_path is False:
			error('no package.json found in here. Please run `npm init`.')


		key = args[0]
		config = self.__get_config()
		if is_path or config.get(key, False) is False:
			if is_path or confirm('No key set. Use key as path?'):
				install_from = key
			else:
				die()

		else:
			install_from = config[key]
		install_to = self.__get_path_to_install(install_from.split(os.path.sep)[-1])
		if not os.path.exists(install_from):
			die('error: the path "{}" does not exist'.format(install_from), 'Can not copy package')
		# if not os.path.exists(install_to):
			# die('error: the path "{}" does not exist'.format(install_to))


		plugin_package_file_path = self.__get_package_file(os.path.valid(install_from))

		plugin_infos = json_decode(plugin_package_file_path, True)
		if 'name' not in plugin_infos:
			die('error: the plugin has no name! Impossible to install it')
		if 'version' not in plugin_infos:
			die('error: the plugin has no version! Impossible to install it')

		name = plugin_infos['name']
		version = '^' + plugin_infos['version']

		if verbose:
			print('install from:', install_from)
			print('install to  :', install_to)
		if verbose is False or confirm('go?'):
			if save:
				# save it to the package.json
				package_info = json_decode(package_file_path, True)
				package_info[save][name] = version
				json_encode(package_info, package_file_path)
			if verbose: 
				print('copying files...')
			copytree(install_from, install_to)

			return print('The package "{}" has been successfully copied to your '
				'node_modules folder.'.format(name))
		return print('Cancel installing the package "{}"'.format(name))
			
	def auto_set(self, args):
		"""
			auto_set: 
				ask to save each package find in `path` (by default current working directory) 
				except the one that are already saved (option all to prevent this)
				options:
					-v --verbose: verbose
					-a --all: show all the packages in the current directory, event the one that are 
					          already saved

		"""
		if len(args) not in range(0, 3 + 1):
			# usage: npm-cache auto-set [--verbose] [--all]
			error('wrong number of args', args)

		verbose = are_in('-v', '--verbose', args, type='any')
		show_all = are_in('-a', '--all', args, type='any')

		path = os.getcwd()

		if not os.path.exists(path):
			error('can not auto set the path "{}" doesn\'t exists!'.format(path))

		pck_saved = []
		config = self.__get_config()
		for key, pck_path in config.items():
			pck_saved.append(self.__get_package_name(pck_path))

		packages = self.__get_direct_package(path, [] if show_all is True else pck_saved)

			

		if packages == {}:
			die('No new package found...' if show_all is False else 'No package found...')

		width = max([len(pck_name) for pck_name in packages.keys()])
		for pck_name, pck_path in packages.items():
			ans = ask('{} "{}"?'.format('set' if pck_name not in pck_saved else 'replace', pck_name), 'no')
			if ans in ('y', 'yes'):
				pck_name = ask('  Package name:', pck_name)
				print('  save', quote(pck_name), quote(pck_path))
				if verbose is False or confirm('  go?'):
					print('  ', end='')
					self.save([pck_name, pck_path])
			elif ans in ('q', 'quit'):
				break

	def help(self, args):
		"""
			Show global help.
			Call `lpm` to see a quick global help
			Call `lpm --help` to see a paused, a bit more complete help
		"""
		if len(args) != 1:
			error('wrong number of args. Accept only one: <cmd>')

		if len(args[0]) == 1:
			for cmd in self.commands:
				if cmd[0] == args[0]:
					args[0] = cmd
					break

		doc = getattr(self, args[0]).__doc__
		if doc is None:
			error('No help available for the command "{}".'.format(args[0]))
		doc = doc.strip()
		doc = doc.splitlines()
		for i, line in enumerate(doc):
			doc[i] = line.strip()
		doc = '\n'.join(doc)
		print(doc)

	def rename(self, args):
		"""
			Rename a key.
			$ npm-cache rename <key> <name> [-s --silent]
			If the new name of the key already exists, it will ask you to confirm to replace it, 
			unless you add the `--silent` option.
		"""
		if len(args) not in range(1, 2 + 1):
			error('wrong number of args.')

		silent = are_in('-s', '--silent', args, type="any")

		config = self.__get_config()
		if config.get(args[0], False) is False:
			error('The key "{}" doesn\'t exists.'.format(args[0]))
		if config.get(args[1], False) is not False:
			if not confirm('The key "{}" is already set. Replace?'):
				die('canceled.')

		val = config[args[0]]
		del config[args[0]]
		config[args[1]] = val
		self.__save_config(config)

	def cmd(self, args):
		""" run a command """
		self.commands = ["help", "set", "install", "get", "ls", "auto-set", "delete", "rename"]
		command_run = False
		cmd = args.get(0, None)
		if cmd is None:
			self.global_help()
			command_run = True
		elif are_in('-h', '--help', cmd, type='any'):
			self.global_help(True)
			command_run = True
		for command in self.commands:
			if cmd in (command, command[0]):
				command_run = True
				getattr(self, command.replace('-', '_'))(args[1:]) 

		if command_run is False:
			error('Main command {} is unknown'.format(quote(args[0])))
		

cmd = Commands()
args = NiceList(args)


cmd.cmd(args)
