# Waha-Wrapper

Python wrapper for [devlikeapro/waha](https://github.com/devlikeapro/waha) using 
[pydantic](https://docs.pydantic.dev/latest/) and [aiohttp](https://docs.aiohttp.org/en/stable/).

The pydantic models are generated from a modified version of the  `openapi.json` spec supplied by the original repo.
Changes to the `openapi.json` spec were necessary since it labeled certain fields as `object` despite them being string, 
leading to validation errors.


# TODO 
- [ ] Fully convert the `openapi.json` spec to pydantic models
- [ ] Wrap all Endpoints
- [ ] Add tests
- [ ] Create complete error handling
- [ ] Add logging
- [ ] Wait for error documentation + consistent errors from the api and then add a Pydantic Model for the errors to. [Issue](https://github.com/devlikeapro/waha/issues/403)