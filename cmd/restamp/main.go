package main

import (
	"flag"
	"log"
	"os"
	"time"

	"github.com/influxdata/telegraf/plugins/parsers/influx"
	"github.com/influxdata/telegraf/plugins/serializers"
)

// restamp changes the timestamps on metrics.

var (
	filename    = flag.String("filename", "", "Filename with metrics to read. use - for stdin.")
	startOffset = flag.Duration("start_offset", 0, "start offset. duration applied to now() to get start time")
	interval    = flag.Duration("interval", 1*time.Second, "interval between timestamps (1s default)")
)

func main() {
	var err error
	log.SetOutput(os.Stderr)
	log.SetFlags(0)

	flag.Parse()
	if filename == nil || len(*filename) == 0 {
		flag.Usage()
		os.Exit(2)
	}
	var f *os.File
	if *filename == "-" {
		f = os.Stdin
	} else {
		f, err = os.Open(*filename)
		if err != nil {
			log.Fatalf("unable to read file %q", *filename)
		}
		defer f.Close()
	}

	parser := influx.NewStreamParser(f)
	serializer, err := serializers.NewInfluxSerializer()
	if err != nil {
		log.Fatalf("unable to create serializer (%s)", err)
	}

	timestamp := time.Now().Add(*startOffset)
	for {
		metric, err := parser.Next()
		if err != nil {
			if err == influx.EOF {
				break // stream ended
			}
			if parseErr, isParseError := err.(*influx.ParseError); isParseError {
				log.Fatalf("Unable to parse input: %q", parseErr)
				continue
			}
			// some non-recoverable error?
			log.Fatalf("stream error: %q", err)
			return
		}

		metric.SetTime(timestamp)
		timestamp = timestamp.Add(*interval)

		b, err := serializer.Serialize(metric)
		if err != nil {
			log.Fatalf("Unable to serialize metric: %s", err)
		}
		os.Stdout.Write(b)
	}

}
