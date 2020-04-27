# build Docker image to Heroku
docker build -t projecon -f Dockerfile .

# push webapp directory to Heroku
heroku container:push web -a projecon

# release webapp on Heroku
heroku container:release web -a projecon

# run Django migrate on Heroku
heroku run python manage.py migrate -a projecon
