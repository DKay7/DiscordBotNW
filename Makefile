.PHONY: prepare_cython_files prepare_venv run

VENV_NAME?=venv
PYTHON=${VENV_NAME}/bin/python

prepare_venv: $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: requirements.txt
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -r requirements.txt
	# touch $(VENV_NAME)/bin/activate

prepare_cython_files: prepare_venv
	( \
		. ${VENV_NAME}/bin/activate; 				\
		cd ./utils/automoderation/swear_finder/;	\
		cythonize -i cython_swear_finder.pyx;		\
		cd -;										\
		deactivate; 								\
	)

run: prepare_venv prepare_cython_files
	${PYTHON} main.py
