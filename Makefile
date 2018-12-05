REGISTRY='registry.jorgeadolfo.com'
IMAGE='epav-sugar-syntax-gui'
APIIMAGE='epav-sugar-syntax-api'
VERSION='latest'
FULLNAME=$(REGISTRY)/$(IMAGE):$(VERSION)
APIFULLNAME=$(REGISTRY)/$(APIIMAGE):$(VERSION)


make:
	docker build -t $(FULLNAME) -f docker/Dockerfile .
	docker build -t $(APIFULLNAME) -f docker/Dockerfile-API .

compose:
	docker-compose -f docker/docker-compose.yml up

composed:
	docker-compose -f docker/docker-compose.yml up -d

logs:
	docker-compose -f docker/docker-compose.yml logs -f
