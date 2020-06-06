``Patrick`` - A framework for writing FB Messenger bots
=======================================================


Example usage:

.. code-block::

    import config
    from fbchat import MessageEvent
    from patrick import Patrick


    bot = Patrick("Patrick", config=config)


    @bot.listener()
    def my_echo(e: MessageEvent):
        print("bot: " + e.message.text)


    bot.listen()