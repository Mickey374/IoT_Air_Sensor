CONTIKI_PROJECT = border-router
PLATFORMS_ONLY = = cc26X0-cc13x0
all: $(CONTIKI_PROJECT)
CONTIKI = ../../..

# The BR is either native or embedded, and in the latter case must support SLIP
# BOARDS_EXCLUDE = nrf52840/dongle

# Include RPL BR module
include $(CONTIKI)/Makefile.dir-variables
MODULES += $(CONTIKI_NG_SERVICES_DIR)/rpl-border-router
# Include webserver module
MODULES_REL += webserver
# Include optional target-specific module
include $(CONTIKI)/Makefile.identify-target
MODULES_REL += $(TARGET)

include $(CONTIKI)/Makefile.include
