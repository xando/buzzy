.. Buzzy documentation master file, created by
   sphinx-quickstart on Sat Jun  1 14:14:55 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Buzzy!
=================

Low level static page generator, with simple API!

Quick Start
-----------

Buzzy currently runs only Python 2.7.x and earlier versions of Python are not supported. 

You can install it from PyPi, by simply pip:

.. code-block:: bash

   $ pip install buzzy

as an alternative method is easy_install (If you don’t have pip installed):

.. code-block:: bash

   $ easy_install buzzy

While the above is the simplest method is simple, the recommended approach would be to create a virtual environment for buzzy project via virtualenv before installing it.

The very simple page with buzzy
```````````````````````````````

.. code-block:: python

   import buzzy

   class StaticSite(buzzy.Base):
   
       @buzzy.register
       def pygments(self):
           yield buzzy.render.content("index.html", "Buzzy is awesome!")
   
   if __name__ == "__main__":
       StaticSite()

save this you project file

.. code-block:: bash

   $ python project.py server
   Generated 2013-06-09 11:10:40.133868
   serving at port 8000

And then go to your browser to http://127.0.0.1:8000/, done. 


Source Code
-----------

https://github.com/xando/buzzy


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
  
* **WATCH_EXCLUDE**, *default* = ['.git*', '*.py', '*.pyc', '%s/*' % BUILD_DIR, BUILD_DIR']

  List of files to be excluded from watch process. Usually when **server** method is called, the build directory will be reload every time when page got changed. This setting prevents from calling rebuild for some files. 


Renderers
---------

.. function:: render.content(target, content)
	      
   Renderer class to create a file from a content.

   :param target: name of the destination file
   :param content: content to put inside he file


.. function:: render.template(target, template, **context)

   Renderer class to render file from a template.

   :param target: name of the destination file
   :param template: jinja2 template located in the **TEMPLATE_DIR**
   :param **context: as many named parameters as needed, 
		     all will be put as a context inside the template


.. function:: render.markdown(target, source)
	      
   Renderer class to render file from a markdown markup.

   :param target: name of the destination file
   :param source: for source of the markup file


Helpers
-------

memonize


Why yield
---------

There are three reasons why to use yield here.

* is cool, and is overly underrated as python mechanism,
* render function may call yield many times, which means that one function may generate more than one file,
* yield is memory efficient, we are operating here on file contents in memory, yield will reduce some pain here.

