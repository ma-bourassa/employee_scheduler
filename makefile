clean:
	rm -fr inm5151_projet/migrations
	rm -f db.sqlite3

reset:
	rm -fr inm5151_projet/migrations
	rm -f db.sqlite3
	python manage.py makemigrations inm5151_projet
	python manage.py migrate
	python manage.py seed

install:
	pip install django django-crispy-forms django-nose

server:
	python manage.py runserver

test:
	clear
	python manage.py test --nocapture
