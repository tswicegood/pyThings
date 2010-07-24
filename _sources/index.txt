.. pyThings documentation master file, created by
   sphinx-quickstart on Sat Jul 24 11:14:01 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyThings
========

Installation
------------
pyThings can be installed using your favorite Python installer.  I recommend
`pip <http://pip.openplans.org>`_::

    pip insall pythings

To install the latest greatest via pip::

    pip install -e git://github.com/tswicegood/pythings#egg=pythings


Usage & Examples
----------------
Below is a series of examples of common tasks that you might want to perform.
They all assume that the following code has been run::

    >>> from things import Things
    >>> t = Things()

That initializes the ``appscript`` needed for talking to Things and loads all
of the tasks.  pyThings currently loads all tasks when you initialize the
``Things`` object, so it may take a few seconds if you have a lot of tasks.

Seeing the tasks stored in Today
""""""""""""""""""""""""""

::

    >>> t.today.to_dos
    [<Todo: Start documentation/website for pyThings>,
     <Todo: Flesh out the rest of pyThings>]


Looking at the top task for Today
"""""

::

    >>> t.today.to_dos[0]
    <Todo: Start documentation/website for pyThings>
    >>> current = t.today.to_dos[0]

Look at the notes and set the notes
""""

::

    >>> current.notes
    u''
    >>> current.notes = u'Updated from within Python'
    >>> current.notes
    u'Updated from within Python'

Check and set the status of a task
""""

    >>> current.status
    k.open
    >>> from things import Todo
    >>> current.status == Todo.OPEN
    True
    >>> current.is_open()
    True
    >>> current.is_complete() is False and current.is_canceled() is False
    True
    >>> current.status = Todo.CANCELED
    >>> current.is_canceled()
    True
    >>> current.is_open()
    False
    >>> current.open()
    >>> current.is_open()
    True

*NOTE*: There appears to be a bug in the AppleScript of Things (as of 1.3.4)
that causes tasks from Today to be shifted to Next when re-opening them from
a canceled state.

Seeing the tasks stored in Next
"""""""""""""

::

    t.next.to_dos


Getting Involved
-------

Steps to get involved:
"""""

* Find something you want to add or refactor
* Fork the project
* Submit pull requests

Todos:
"""""
There's still tons to do to make feature complete.  Here are a few things I'd
like to see added:

* Lazying loading of information from Things.  Not sure how feasible it is
  given we have to build the lists doing some ugly comparisons, but would
  be nice.
* Add in some unit testing.  Kind of a hard one given that we're translating to
  another language, but it could be done.  My inclination is to have a unit
  test suite that isolates pyThings from appscript, then have an integration
  test that uses real AppleScript and modifies and checks against a real Things
  intance.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

