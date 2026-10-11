################################################################################
#
# reglinux-games-databases
#
################################################################################

# No fixed upstream tarball: these are live, unversioned data feeds fetched
# straight from Redump.org/GameTDB/MAME's own GitHub releases at build time,
# so there's nothing to pin a hash against - see the wget-based download
# commands below instead of the usual _SITE/_SOURCE/.hash trio.
REGLINUX_GAMES_DATABASES_SOURCE =

REGLINUX_GAMES_DATABASES_DEPENDENCIES = host-python3

# regmsgd's reference databases, gzipped; datainit unpacks them to /userdata/bios/databases.
REGLINUX_GAMES_DATABASES_DBDIR = $(TARGET_DIR)/usr/share/reglinux/datainit/bios/databases

# Redump.org system code -> output basename
REGLINUX_GAMES_DATABASES_REDUMP_SYSTEMS = \
	PSX:psx \
	PS2:ps2 \
	PSP:psp \
	SS:saturn \
	MCD:segacd \
	DC:dreamcast

# MAME_VERSION (package/emulators/mame/mame.mk) is a GroovyMAME tag like
# "gm0287sr222b" - pull just the upstream MAME release number ("0287")
# back out of it, so the -listxml release download always tracks whatever
# MAME version mame.mk currently builds, without hand-syncing two files.
REGLINUX_GAMES_DATABASES_MAME_VERSION = $(shell echo $(MAME_VERSION) | sed -n 's/^gm\([0-9]\+\)sr.*/\1/p')

define REGLINUX_GAMES_DATABASES_INSTALL_TARGET_CMDS
	# Drop the copies earlier builds left elsewhere.
	rm -rf $(TARGET_DIR)/usr/share/reglinux/datainit/bios/Databases \
		$(TARGET_DIR)/usr/share/reglinux/datainit/bios/mame/mame-stripped.xml.gz \
		$(TARGET_DIR)/usr/share/regmsg/data/databases \
		$(TARGET_DIR)/usr/share/regmsg/data/mame/mame-stripped.xml
	mkdir -p $(REGLINUX_GAMES_DATABASES_DBDIR)

	for entry in $(REGLINUX_GAMES_DATABASES_REDUMP_SYSTEMS); do \
		code=$${entry%%:*}; \
		name=$${entry#*:}; \
		echo "reglinux-games-databases: downloading Redump.org datfile for $$code"; \
		wget -q --tries=3 --waitretry=5 -O $(@D)/redump-$$name.zip \
			"https://redump.info/datfile/$$code/serial,version"; \
		rm -rf $(@D)/redump-$$name && mkdir -p $(@D)/redump-$$name; \
		$(UNZIP) -o $(@D)/redump-$$name.zip -d $(@D)/redump-$$name; \
		gzip -9nc "$$(ls $(@D)/redump-$$name/*.dat | head -n1)" \
			> $(REGLINUX_GAMES_DATABASES_DBDIR)/redump-$$name.dat.gz; \
	done

	echo "reglinux-games-databases: downloading GameTDB wiitdb.zip (Wii + GameCube)"
	wget -q --tries=3 --waitretry=5 -O $(@D)/wiitdb.zip \
		"https://www.gametdb.com/wiitdb.zip"
	rm -rf $(@D)/wiitdb && mkdir -p $(@D)/wiitdb
	$(UNZIP) -o $(@D)/wiitdb.zip -d $(@D)/wiitdb
	gzip -9nc $(@D)/wiitdb/wiitdb.xml > $(REGLINUX_GAMES_DATABASES_DBDIR)/gametdb-wiitdb.xml.gz

	echo "reglinux-games-databases: downloading MAME $(REGLINUX_GAMES_DATABASES_MAME_VERSION) -listxml release"
	wget -q --tries=3 --waitretry=5 \
		-O $(@D)/mame$(REGLINUX_GAMES_DATABASES_MAME_VERSION)lx.zip \
		"https://github.com/mamedev/mame/releases/download/mame$(REGLINUX_GAMES_DATABASES_MAME_VERSION)/mame$(REGLINUX_GAMES_DATABASES_MAME_VERSION)lx.zip"
	rm -rf $(@D)/mamelx && mkdir -p $(@D)/mamelx
	$(UNZIP) -o $(@D)/mame$(REGLINUX_GAMES_DATABASES_MAME_VERSION)lx.zip -d $(@D)/mamelx
	$(HOST_DIR)/bin/python3 $(REGLINUX_GAMES_DATABASES_PKGDIR)/strip-mame-xml.py \
		$(@D)/mamelx/mame$(REGLINUX_GAMES_DATABASES_MAME_VERSION).xml \
		$(@D)/mame-stripped.xml
	gzip -9nc $(@D)/mame-stripped.xml > $(REGLINUX_GAMES_DATABASES_DBDIR)/mame-stripped.xml.gz

	# Atari Lynx screen rotation. Lives in a softlist rather than -listxml, so
	# mame-stripped.xml.gz has nowhere to carry it; hash/lynx.xml is the only
	# one of MAME's 764 softlists with rotation metadata. Same tag as the
	# -listxml release above. Lands beside the hand-maintained special/*.csv
	# tables installed below -- generated and curated tables, same directory,
	# same package.
	echo "reglinux-games-databases: downloading MAME $(REGLINUX_GAMES_DATABASES_MAME_VERSION) hash/lynx.xml"
	wget -q --tries=3 --waitretry=5 -O $(@D)/lynx.xml \
		"https://raw.githubusercontent.com/mamedev/mame/mame$(REGLINUX_GAMES_DATABASES_MAME_VERSION)/hash/lynx.xml"
	$(HOST_DIR)/bin/python3 $(REGLINUX_GAMES_DATABASES_PKGDIR)/lynx-rotation-csv.py \
		$(@D)/lynx.xml $(@D)/lynx.csv
	$(INSTALL) -D -m 0644 $(@D)/lynx.csv \
		$(TARGET_DIR)/usr/share/regmsg/data/special/lynx.csv

	# Hand-maintained launcher data tables (ex-configgen files): MAME/MESS system + control maps
	# and per-softlist autoload commands, the non-arcade screen-rotation tables,
	# and the blank Dreamcast VMU image. Read by regmsgd's lua generators and launcher/helpers.
	mkdir -p $(TARGET_DIR)/usr/share/regmsg/data
	cp -dpfr $(REGLINUX_GAMES_DATABASES_PKGDIR)/data/mame \
		$(REGLINUX_GAMES_DATABASES_PKGDIR)/data/special \
		$(REGLINUX_GAMES_DATABASES_PKGDIR)/data/dreamcast \
		$(TARGET_DIR)/usr/share/regmsg/data/

	# Per-game input-device database (light gun / wheel / spinner / trackball,
	# N64 rumble pak, widescreen). Read by regmsgd: launcher/metadata.rs when
	# configuring an emulator, library/wheelandgungamesdb.rs to set the
	# gamelist's inputdevice field. Note this one sits directly under
	# /usr/share/regmsg, not under data/.
	$(INSTALL) -D -m 0644 $(REGLINUX_GAMES_DATABASES_PKGDIR)/data/wheelandgungamesdb.json \
		$(TARGET_DIR)/usr/share/regmsg/wheelandgungamesdb.json

	$(INSTALL) -D -m 0644 \
		$(REGLINUX_GAMES_DATABASES_PKGDIR)/CREDITS.txt \
		$(REGLINUX_GAMES_DATABASES_DBDIR)/CREDITS.txt
endef

$(eval $(generic-package))
