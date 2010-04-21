pyThings
========
Simple, untested, incomplete, hacked together wrapper around Things.app's
AppleScript code that lets you sanely interact with it without a ton of
``get()[n]`` calls.


Usage
-----
It attempts to mimic the Thing's AppleScript API where appropriate.  One area
that it does simplify is the ability to access the top-level lists.  Rather
than having to go through the ``lists`` property, you can access the ``Today``
list directly:

    from things import Things
    t = Things()
    t.today.to_dos[0]

Likewise, I've started adding some convinence functions in that handle the boolean
checks so you don't have to compare against the ``appscript.k.*`` values by hand.

For example:

    from things import Things
    t = Things()
    t.today.to_dos[0].is_complete() # True/False
    t.today.to_dos[0].complete()
    t.today.to_dos[0].is_complete() == True

Todo
----
* Expand what ``Things`` object responds to
* Add ``Area`` object
* Add ``Project`` object
* Finish adding the rest of the ``application`` properties that are exposed via AppleScript
