MKFILE_DIR := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))
MKFILE_DIR_BASENAME := $(shell basename $(MKFILE_DIR))
PROJECT := hybrid
PACKAGE := hybrid.tar.gz

run: ;\
  $(MKFILE_DIR)/$(PROJECT).py
$(PACKAGE): ;\
  echo "Creating server tarball";\
  tar -C $(MKFILE_DIR) -pcz -f $(PACKAGE) *
deploy: $(MKFILE_DIR)/hybrid-config/install $(PACKAGE);\
  echo "Getting ssh-agent ready..." ; \
  eval "$(shell pgrep ssh-agent || ssh-agent -t 120)" > /dev/null; \
  ssh-add ;\
  echo "Copying server files..." ; \
  scp -rpq $(PACKAGE) root@hybrid:/tmp/; \
  echo "Unpacking and running install script..." ; \
  ssh root@hybrid "mkdir /tmp/$(PROJECT); tar -C /tmp/$(PROJECT) -pxz -f /tmp/$(PACKAGE); /tmp/$(PROJECT)/install/install" ;\
  echo "Reloading systemd manager configuration for user srv..." ;\
  ssh srv@hybrid "systemctl --user daemon-reload" ;\
  echo "Closing ssh-agent..." ;\
  pkill ssh-agent ;\
  echo "Done!" ; 
.SILENT: deploy $(PACKAGE) clean reset
clean: ;\
  echo "Cleaning up..." ;\
  $(RM) $(MKFILE_DIR)/*.log ; \
  $(RM) $(MKFILE_DIR)/*.log.1 ; \
  $(RM) $(MKFILE_DIR)/$(PACKAGE) 
reset: clean ;\
  echo "Resetting DBs and signing key..." ;\
  $(RM) $(MKFILE_DIR)/app_key ;\
  $(RM) $(MKFILE_DIR)/db/* 
