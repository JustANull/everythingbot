import commands
import json
import sys

class Loader(commands.Commands):
	def __init__(self, config):
		commands.Commands.__init__(self, {
			'!listmodules': self.do_list,
			'!load':        self.do_load,
			'!unload':      self.do_unload,
			'!reload':      self.do_reload
		})

		self.allowed_users = config["allowed_users"]
		self.autoload = config["autoload"]
		self.loaded_modules = {
			"loader": True
		}
		self.running_modules = {
			"loader": True
		}

	def load_module(self, name):
		self.publisher.parent.say("Loading module %s." % name)

		if name in self.loaded_modules:
			del sys.modules[name]

		self.loaded_modules[name] = True
		exec("import %s" % name)

		config = None
		with open("config.json") as f:
			config = json.load(f)

		self.running_modules[name] = True
		self.publisher.add_subscriber(name, getattr(sys.modules[name], name.capitalize())(config[name]))

	def unload_module(self, name):
		if name in self.running_modules:
			self.publisher.parent.say("Unloading module %s." % name)
			del self.running_modules[name]
			self.publisher.remove_subscriber(name)
		else:
			self.publisher.parent.say("Module %s not loaded." % name)

	def reload_module(self, name):
		self.publisher.parent.say("Reloading module %s." % name)

		if name in self.running_modules:
			self.unload_module(name)

		self.load_module(name)

	def do_list(self, nick, rest):
		"""Lists the currently running modules."""
		self.publisher.parent.say("Currently running: %s." % ", ".join(map(lambda (k, v): k, self.running_modules.iteritems())))

	def do_load(self, nick, rest):
		"""Restricted to a subset of users. Loads a module at runtime."""
		if nick in self.allowed_users:
			if len(rest.split()) > 1:
				self.publisher.parent.say("Please provide a single lowercase word as the argument.")
			else:
				self.load_module(rest.strip())

	def do_unload(self, nick, rest):
		"""Restricted to a subset of users. Unloads a module at runtime."""
		if nick in self.allowed_users:
			if len(rest.split()) > 1:
				self.publisher.parent.say("Please provide a single lowercase word as the argument.")
			else:
				self.unload_module(rest.strip())

	def do_reload(self, nick, rest):
		"""Restricted to a subset of users. Reloads a module at runtime."""
		if nick in self.allowed_users:
			if len(rest.split()) > 1:
				self.publisher.parent.say("Please provide a single lowercase word as the argument.")
			else:
				self.reload_module(rest.strip())

	def on_add(self, publisher):
		self.publisher = publisher

		for name in self.autoload:
			self.load_module(name)

	def on_remove(self):
		for name, _ in self.running_modules.copy().iteritems():
			self.unload_module(name)

		self.running_modules = {}