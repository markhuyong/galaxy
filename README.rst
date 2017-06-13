==========================
galaxy
==========================

.. image:: https://travis-ci.org/lebooks/galaxy.svg?branch=master
    :target: https://travis-ci.org/lebooks/galaxy

HTTP server which provides API for scheduling Scrapy spiders and
making requests with spiders.

Allows you to easily add HTTP API to your existing Scrapy project. All Scrapy project
components (e.g. middleware, pipelines, extensions) are supported out of the box. You
simply run galaxy in Scrapy project directory and it starts HTTP server allowing you
to schedule your spiders and get spider output in JSON format.

Install
=============
tar czf galaxy.tar.gz galaxy
scp galaxy.tar.gz lebooks@39.108.102.79:/home/lebooks/galaxy.tar.gz
sudo apt-get install python-dev
sudo apt-get install python-lxml
sudo pip install -r requirements.txt
./start.sh
./stop.sh

Documentation
=============

Documentation is available here:


Support
=======

Open source support is provided here in Github. Please `create a question
issue`_ (ie. issue with "question" label).

Commercial support is also available by `lebooks`_.

.. _create a question issue:
.. _lebooks: http://lebooks.com
