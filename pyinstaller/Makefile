
ifeq ($(s),1)
 opt = -F
endif

#opt += --add-data="/home/czh/github/uvs_smt/web_rc.py:."
#opt += --add-data="/home/czh/github/uvs_smt/web.qrc:."
opt += --icon=../ico/uvs_white.jgp

build:
	pyinstaller $(opt) ../main.py

clean:
	rm -rf dist build main.spec
