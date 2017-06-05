README

Add Scheduler

```bash
stock-check$ heroku addons:add scheduler
stock-check$ heroku addons:open scheduler
```

Add logging

```bash
stock-check$ heroku addons:add papertrail
stock-check$ heroku addons:open papertrail
```

Add configuration

```bash
stock-check$ heroku config:set ENV_VAR=env_var_value
```

Create DB
```bash
stock-check$ heroku addons:create heroku-postgresql:hobby-dev
stock-check$ psql uri_from_heroku
> CREATE TABLE LINKS(link_id SERIAL PRIMARY KEY, link VARCHAR(500), expiration TIMESTAMP NOT NULL DEFAULT (now() + interval '1 day'));
```
