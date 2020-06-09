``fbchatbot`` - A framework for writing FB Messenger bots
=======================================================

`fbchat <https://github.com/carpedm20/fbchat>`__ does all the heavy lifting. Thanks fbchat!

Very much still in progress! :construction_worker:

Very much subject to breaking change! :trollface:

Example:

.. code-block:: python

    import config
    from fbchatbot import Chatbot, CommandEvent, MessageEvent


    bot = Chatbot(config=config)


    @bot.listener()
    def my_echo(e: MessageEvent):
        print("bot heard: " + e.message.text)


    @bot.command("hi")
    def say_hi(e: CommandEvent):
        """Say hi back"""
        e.thread.send_text("Hello")


    bot.listen()

Features
--------

Built-in events
~~~~~~~~~~~~~~~

Comes with new events, normalizing the ones fbchat provides to make some tasks easier

Type-directed event listeners
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use type hints to specify what events to listen for:

.. code-block:: python

    @bot.listener()
    def my_echo(e: MessageEvent):
        print("bot: " + e.message.text)
        
Or don't...

.. code-block:: python

    @bot.listener(MessageEvent)
    def my_echo(e):
        print("bot: " + e.message.text)
        
Plugin system
~~~~~~~~~~~~~

Break functionality into plugins! Distribute them, maybe one day.

On the roadmap
--------------

- Logging plugin!
- Optional message queue!
- Configure behavior at the user/group thread level


Examples
--------

Plugin example
~~~~~~~~~~~~~~

``my_plugin.py``

.. code-block:: python

    from fbchatbot import Plugin


    my_plugin = Plugin("MyPlugin")
    
    @my_plugin.listener()
    def my_echo(e: MessageEvent):
        print("bot: " + e.message.text)


``main.py``

.. code-block:: python

    import config
    from .my_plugin import my_plugin
    from fbchatbot import Chatbot


    bot = Chatbot(config=config)
    bot.load_plugin(my_plugin)
    bot.listen()
