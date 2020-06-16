all : 1.png 2.png

# We use convert from ImageMagick to generate PNG files from PDF files, because
# Gnuplot replot command doesn't work well with multiplot used in 1.gnuplot.
# Also, the ratio of Gnuplot-generated PNG and PDF files differ from each other;
# ImageMagick keeps the ratio consistent.
%.png : %.pdf
	convert $< $@

%.pdf : %.gnuplot
	gnuplot $<

1.pdf : 1c.data 1s.data 1.gnuplot
	gnuplot 1.gnuplot

2.pdf : 2.data 2.gnuplot
	gnuplot 2.gnuplot

# tail -n +2 skips over the first one line of a file.  The sed command replaces
# the CSV separator by whitespace, as required by Gnuplot.
%.data : %.csv
	tail -n +2 $<  | sed 's/,/ /g' > $@

clean:
	rm *.data *.pdf *.png
