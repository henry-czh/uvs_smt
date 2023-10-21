ifeq ($(test),testcase0)
	delay = 50
else ifeq ($(test),testcase1)
	delay = 20
else ifeq ($(test),testcase2)
	delay = 20
else ifeq ($(test),testcase3)
	delay =  50
	error = sleep error
else
	delay = 10
endif

clean:
	echo "this is clean task"
	rm -rf simdir/$(test)

build:
	mkdir -p simdir/$(test)/flists
	mkdir -p simdir/$(test)/sim_temp
	sleep $(delay)
	$(error)
	echo "this is build task"

compiler:
	echo $(test)
	sleep $(delay)
	$(error)
	echo "this is compiler task"

run:
	echo $(test)
	sleep $(delay)
	$(error)
	echo "this is run task"