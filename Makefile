build:
	go build ./cmd/restamp
	go build ./cmd/metric-replayer

timestamp:
	tar -Oxf data/temps.tar.gz | ./restamp -filename - > ./data/temps-stamped.txt
