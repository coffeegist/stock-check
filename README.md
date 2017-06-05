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
stock-check]$ heroku config:set ENV_VAR=env_var_value
```
