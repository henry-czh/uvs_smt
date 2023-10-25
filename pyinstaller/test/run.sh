export BASE_CONFIG_FILE=./tb_config
export USER_CONFIG_FILE=./tb_config
export CONFIG_SAVE_DIR=./config
export SVG_FILE=./tb_config/demo.svg
export DIAG_FILE=./src/test.diag
export CBS_HOME=../../
export TB_HOME=../
export DEFAULT_MODE=default
export SMT_HOME=/home/czh/github/uvs_smt

#python2 ./verif_config/cgi-bin/parseConfig.py $BASE_CONFIG_FILE $USER_CONFIG_FILE
export XDG_SESSION_TYPE=x11 #/usr/local/bin/your_soft_bin

python3 -B ../../main.py --disable-seccomp-filter-sandbox
#../dist/main/main
#~/main/main
