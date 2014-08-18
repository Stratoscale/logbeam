all: unittest check_convention

clean:
	rm -fr build dist logbeam.egg-info

UNITTESTS=$(shell find tests -name 'test*.py' | sed 's@/@.@g' | sed 's/\(.*\)\.py/\1/' | sort)
COVERED_FILES=$(shell find logbeam -name '*.py' -printf '%p,')
unittest:
	rm -f .coverage*
	PYTHONPATH=`pwd` COVERAGE_FILE=`pwd`/.coverage coverage run --parallel-mode --append -m unittest $(UNITTESTS)
	coverage combine
	coverage report --show-missing --rcfile=coverage.config --fail-under=87 --include='$(COVERED_FILES)'

check_convention:
	pep8 . --max-line-length=109

uninstall:
	-yes | sudo pip uninstall logbeam
	sudo rm /usr/bin/logbeam

install:
	-yes | sudo pip uninstall logbeam
	python setup.py build
	python setup.py bdist
	python setup.py bdist_egg
	sudo python setup.py install
	sudo cp logbeam.sh /usr/bin/logbeam
	sudo chmod 755 /usr/bin/logbeam
	sudo cp bash.completion.sh /etc/bash_completion.d/logbeam.sh
