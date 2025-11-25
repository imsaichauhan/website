PY := .venv/bin/python
RUN := _scripts/run.sh
.PHONY: bookmarks projects images all build photos photos-clean copy-originals

bookmarks:
	$(RUN) bookmarks

projects:
	$(RUN) projects

images:
	$(RUN) images

all: bookmarks projects

build:
	quarto render
	# Copy photo assets to _site (thumbnails and originals)
	mkdir -p _site/_assets/images/photos
	cp -r _assets/images/photos/* _site/_assets/images/photos/ 2>/dev/null || true
	# Ensure originals are restored after a render (copies may be overwritten by render)
	$(MAKE) copy-originals

photos:
	python _scripts/generate-photos.py

photos-clean:
	find _assets/images/photos -name "thumbnails" -type d -exec rm -rf {} +

copy-originals:
	@echo "Copying photo originals into _site..."
	_scripts/copy_originals_to_site.sh