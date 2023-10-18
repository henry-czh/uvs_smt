
ifeq ($(s),1)
 opt = -F
endif

#opt += --add-data="/home/czh/github/uvs_smt/web_rc.py:."
#opt += --add-data="/home/czh/github/uvs_smt/web.qrc:."
opt += --icon=../ico/uvs_white.jgp
opt += --name=QSmtool

build:
	pyinstaller $(opt) ../main.py
	cp ./qt.conf ./dist/QSmtool

clean:
	rm -rf dist build

spec_build:
	pyinstaller main.spec