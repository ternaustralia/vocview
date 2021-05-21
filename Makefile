version = 1.1.5

build:
	docker build -t ternau/vocview:$(version) .
	docker build -t ternau/vocview:latest .

run:
	docker run --rm --name vocview -p 8000:8000 ternau/vocview:$(version)

# Push to Docker Hub.
push:
	docker push ternau/vocview:$(version)
	docker push ternau/vocview:latest