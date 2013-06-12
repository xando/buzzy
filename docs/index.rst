Buzzy!
======

Low level static page generator, with simple API!

**Why to write use static sites generator?** There are many cases, when your website will be static and using dynamic pages framework like Django, Ruby on Rails, Flask, Sinatra would be a bit of overhead.

**Why to write another static website generator?** Not really sure, yet!


Install
-------

Buzzy currently runs only Python 2.7.x and earlier versions of Python are not supported. 

You can install it from PyPi, by simply **pip**:

.. code-block:: bash

   $ pip install buzzy

as an alternative method is **easy_install** (If you don’t have pip installed):

.. code-block:: bash

   $ easy_install buzzy

While the above is the simplest method is simple, the recommended approach would be to create a virtual environment for buzzy project via virtualenv before installing it.


Quick Start
-----------

.. code-block:: python

   import buzzy

   class StaticSite(buzzy.Base):
   
       @buzzy.register
       def thing(self):
           yield buzzy.render.content("index.html", "Hello world")
   
   if __name__ == "__main__":
       StaticSite()

Each "view" created with buzzy needs to be decorated with **register**. This way buzzy will know which method in class should be called during the build process.

.. code-block:: bash

   $ python project.py build
   Generated 2013-06-09 11:10:40.133868

In your build directory, which will be **_build**. 

.. code-block:: bash

   $ ls _build
   index.html
   $ cat _build/index.html
   Hello world

You should see there one file *index.html*, 
and the content of this file will be 'Hello world'

.. code-block:: bash

   $ python project.py server

Go to your browser to http://127.0.0.1:8000/, done!


Renderers
---------

.. function:: render.content(target, content)
	      
   Renderer class to create a file from a content.

   :param target: name of the destination file
   :param content: content to put inside he file

.. code-block:: python
   
   @buzzy.register
   def view(self):
       yield buzzy.render.content("index.html", "hello world")


   
.. function:: render.template(target, template, **context)

   Renderer class to render file from a template.

   :param target: name of the destination file
   :param template: jinja2 template located in the **TEMPLATE_DIR**
   :param **context: as many named parameters as needed, 
		     all will be put as a context inside the template

.. code-block:: python

   @buzzy.register
   def view(self):
       yield buzzy.render.template("index.html", "index.tpl", text="hello world")



.. function:: render.markdown(target, source)
	      
   Renderer class to render file from a markdown markup.

   :param target: name of the destination file
   :param source: for source of the markup file

.. code-block:: python

   @buzzy.register
   def view(self):
       yield buzzy.render.markdown("index.html", "index.md")


Settings
--------

* **INCLUDE**, *default* = []
  
  List of files and directories that will be copy over to build directory 
  without any modifications.
  
* **BUILD_DIR**, *default* = 'build'

  Build directory, where static page will be generated after executing **build** method.
  
* **TEMPLATES_DIR**, *default* = 'templates'

  Templates directory, jinja2 base template directory used with **render.template**.

* **SERVER_PORT**, *default* = '8000'

  Developer server port, from which will page will be server after executing **server** method.
  
* **WATCH_EXCLUDE**, *default* = ['.git*', '*.py', '*.pyc']

  List of files to be excluded from watch process. 
  When **watch** command is called, the build directory will be reload every time when page got changed. 
  This setting prevents from calling rebuild for some files. **BUILD_DIR** is will be excluded as well.


Helpers
-------


.. function:: memoized
	      
   Helper function decorator that will remember function results within one build cycle. 
   Useful when you have code to use in than more render function.

.. code-block:: python

   import buzzy

   class StaticSite(buzzy.Base):

       @buzzy.memoized
       def something_expensive(self):
           # code
           return results

       @buzzy.register
       def some_view(self):
           context = self.something_expensive()
           yield buzzy.render.template("index.html", "index.html", context=context)

       @buzzy.register
       def other_view(self):
           context = self.something_expensive()
	   yield buzzy.render.template("rss.html", "rss.html", context=context)


In this case **something_expensive** will be called only once and results will be remembered, if **other_view** will call this method again, thanks to **memoized** decorator won't trigger execution and just return precalculated value.


Why yield
---------

There are three main reasons why to use yield here:

* yield is cool, and is overly underrated as python mechanism,
* render function may call yield many times, which means that one function may generate more than one file,
* yield is memory efficient, we are operating here on file contents in memory, yield will reduce some pain here.


Source Code
-----------

https://github.com/xando/buzzy
