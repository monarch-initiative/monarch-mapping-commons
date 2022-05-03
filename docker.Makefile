################################################
#### Commands for building the Docker image ####
################################################

VERSION = "0.1.1"
IM=monarchinitiative/mapping-commons
ROBOT=robot

build-no-cache:
	@docker build --no-cache -t $(IM):$(VERSION) . \
	&& docker tag $(IM):$(VERSION) $(IM):latest

build:
	@docker build -t $(IM):$(VERSION) . \
	&& docker tag $(IM):$(VERSION) $(IM):latest
	
build-use-cache-dev:
	@docker build -t $(DEV):$(VERSION) . \
	&& docker tag $(DEV):$(VERSION) $(DEV):latest

clean:
	docker kill $(IM) || echo not running ;
	docker rm $(IM) || echo not made 

publish-no-build:
	@docker push $(IM):$(VERSION) \
	&& docker push $(IM):latest
	
publish-dev-no-build:
	@docker push $(DEV):$(VERSION) \
	&& docker push $(DEV):latest
	
publish: build
	@docker push $(IM):$(VERSION) \
	&& docker push $(IM):latest
