NAME=vhdl-coding-style

all: $(NAME).html $(NAME).pdf

$(NAME).html: $(NAME).adoc
	asciidoc -a source-highlighter=highlight -a language=vhd -o $@ $<

$(NAME).pdf: $(NAME).xml
	dblatex --pdf -P latex.output.revhistory=0 -o $@ $<

$(NAME).xml: $(NAME).adoc
	asciidoc -a language=vhdl -b docbook -o $@ $<

clean:
	$(RM) $(NAME).html $(NAME).xml $(NAME).pdf

# Display all the rules
rules:
	sed -e '/^==== /s/^==== //p' -n $(NAME).adoc

.PHONY: clean rules
