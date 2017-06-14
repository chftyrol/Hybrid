# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python -msphinx
SPHINXPROJ    = hybrid
SOURCEDIR     = .
BUILDDIR      = _build
MKFILEDIR := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))
PROJDIR := $(shell dirname $(MKFILEDIR))

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) ;\
	cp -r "$(BUILDDIR)/$@/" "$(PROJDIR)/docs" ;\
	touch "$(PROJDIR)/docs/.nojekyll"
