import traceback
import logging

class Publisher():
	def __init__(self, parent):
		self.parent = parent
		self.subscribers = {}

	def add_subscriber(self, identity, sub):
		self.subscribers[identity] = sub
		sub.on_add(self)

	def remove_subscriber(self, identity):
		self.subscribers[identity].on_remove()
		del self.subscribers[identity]

	def remove_all_subscribers(self):
		for identity, sub in self.subscribers.copy().iteritems():
			sub.on_remove()

		self.subscribers = {}

	def get_subscriber(self, identity):
		return self.subscribers[identity]

        def message(self, kind, *args):
                for identity, sub in self.subscribers.copy().iteritems():
                        try:
                                sub.message(kind, *args)
			except Exception as e:
                                # TODO: Python 2/3 compat here
                                message = "Error in module %s: %s: %s" % (sub.__module_, e, traceback.format_exc())
                                self.parent.say(message)
                                logging.error(message)
