# Thoughts from the first architecture:

events, tasks, and event handlers/commands are defined in plugins. plugins are
loaded in main.py.

ideally a use of the bot should be able to install plugins into a plugins folder,
and main.py should load anything in that folder. plugins can be configured in config.ini

should i then define what commands are available in different chats at the plugin
level? works for me, but what if i want to distribute pieces of a plugin?
that will likely only be wanted for commands. should i separate commands and plugins?
probably not... so perhaps ill just have a generic commands plugin and implement some form
of disallowing/allowing commands per thread, and also allow such allow/disallow on a plugin 
level as well

how do plugins depend on each other? for example, logging chats to a database is obviously
useful as a plugin. this creates a database of logs, which other plugins would want access to.
easiest solution is to just not enforce that. perhaps just have db name be some piece of config
for either plugin. that's a matter of external resources (ie not eg events). for internal commands
ill just disallow dependencies, ie a plugin cannot use events defined in other plugins. ill need to
special-case some sort of default commands (e.g. .help), events, and tasks. but then how do i make
those accessible to plugins? ie how can they import them? i suppose the same way plugins import
huey in order to define tasks...
update: i think i should allow plugins to depend on events from each other after all

it would be nicer to be able to distribute patrick as a module and do like

```
import load_plugin, listen from patrick
import plugin1

load_plugin(plugin1)
listen()
```

plugins depend on patrick, can import events
how to i deal with huey in this case? plugins need to be 

problems: name collisions for commands. can warn about this though, and allows
disambiguation by using plugin name as namespace for commands, say if plugin1 and plugin2
have command cmd, they can be called with .plugin1:cmd and .plugin2:cmd

is this possible? things to confirm:
- tasks can be loaded into heuy with dynamic imports
- events can be defined for blinker in diff plugins

change events to be sent on signals per thread?

# Thoughts on the new architecture 

the problem: handling an event requires an instance of a bot, e.g. for triggering
the handling of new events. where does that behavior exist? should i define it with
a protocol like before?

when handling an event, should the callback be passed the main fbchatbot instance,
or should it be passed the plugin instance it is attached to? i think this depends
on how plugins are allowed to extend fbchatbot. for example, ill want a scheduler
for remindme command. should the scheduler be defined in a plugin? if so, how can
other plugins use that scheduler?

if the scheduler is defined in a plugin and event handlers are passed their own
plugin, then scheduler can only be used within the plugin its defined in.

... scheduler should probably be builtin anyway...


what is the motivation behind plugins anyway? the current design of plugins is that
they encapsulate events and commands. currently there is no definition of how they
can modify a bot beyond that

1) Sharing. im not sure if this is a good enough
   reason for them to exist though considering i have been basically making up plugin 
   use cases to justify their existence. its not clear to me how useful they can be
   without use cases, so defining how they interact with a bot instance is hard, and
   perhaps a bit premature

2) Easy way to split bot functionality across different threads

Defining different bot behavior for different threads is something I want but haven't
really nailed down how i want to do. but perhaps figuring out how i want to do that
would inform how plugins are used?

my original idea was to have some sort of thread filtering applied to plugins and 
the functionality they contain. but i think that's actually the wrong way to think
(plugin first, threads second). Its more natural I think to create bots for different
threads, which use the same user credentials but whose behavior is specified on
a thread-to-thread basis. what might that look like?

```
from fbchat import MessageEvent
from fbchatbot import Chatbot
from fbchatbot-plugin-x import plugin_x

import config
from plugins import plugin_list


fbchatbot = Chatbot(config=config)

bot1 = fbchatbot.bot_for_thread("<threadid>", nickname="MyThreadBot").use_plugin(plugin_x)

@bot1.listener
def my_echo(e: MessageEvent):
    print("bot: " + e.message.text)

bot2 = fbchatbot.bot_for_thread("<threadid>")
bot2.use_plugins(plugin_list)
bot2.exclude_commands(['fire_rockets'])

fbchatbot.listen()
```

```config.py
FB_EMAIL=...
FB_PASSWORD=...
DEBUG=True # log events to stdout, log listeners being registered, etc
```

should logging be a builtin or a plugin? one nice aspect of it being in a plugin
is configurability... like logging messages, messages and reactions, etc... logging
can be pretty complex. i guess really 

```
@attr.s
class LoggingPlugin(Plugin):
    

## Plugins as instances vs classes

If a plugin is an instance then any state inherent to a plugin will be shared
across its uses. this might be problematic if two bots which use the same plugin
should be theoretically separate. Ways this would be a problem:

 - configuring the same plugin in two different ways for two different bots:
    if i want to have some config object local to a plugin which specifies how
    it is configured, eg the name of a table used to store logs, then plugins
    will need to be separate instances
 - testing plugins?

So perhaps I can just lift what I've done with listeners to the class level?
listeners look like:

    @MyPlugin.listener
    def foo(event: Type): ...

This creates a list of listeners on the class. When a MyPlugin is instantiated,
these listeners get registered on the instance. 

An alternative is to copy a plugin instance and run some init callable when
load_plugin is called? Might be a nicer api...