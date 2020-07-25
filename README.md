# Intro

Simulators need two environment variables set to be able to attach to the platform.

The first is `SIM_ACCESS_KEY`. You can create one from the `Account Settings` page.
You have one chance to copy the key once it has been created. Make sure you don't enter
the ID.

The second is `SIM_WORKSPACE`. You can find this in the URL after `/workspaces/` once
you are logged in to the platform.

There is also an optional `SIM_API_HOST` key, but if it is not set it will default to `https://api.bons.ai`.

If you're launching your simulator from the command line, make sure that you have these two
environment variables set. If you like, you could use the following example script:

Linux:
```sh
export SIM_WORKSPACE=<your-workspace-id>
export SIM_ACCESS_KEY=<your-access-key>
python3 __main__.py
```

Windows:
```cmd
set SIM_WORKSPACE=<your-workspace-id>
set SIM_ACCESS_KEY=<your-access-key>
python3 __main__.py
```

You will need to install support libraries prior to running. Our demos depend on `microsoft-bonsai-api`.

```sh
pip3 install microsoft-bonsai-api
```

## Building Demo Dockerfile
```sh
docker build -t <IMAGE_NAME> .
```

## Run Dockerfile local
```sh
docker run --rm -it -e SIM_ACCESS_KEY="<ACCESS_KEY>" -e SIM_API_HOST="<TARGET>" -e SIM_WORKSPACE="<WORKSPACE>" <IMAGE_NAME>
```

## How to push to ACR
```sh
az login # (Is not necessary if you are already up to date or logged in recently)
az acr login --subscription <SUBSCRIPTION_ID> --name <ACR_REGISTRY_NAME>
docker tag <IMAGE_NAME> <ACR_REGISTRY_NAME>.azurecr.io/bonsai/<IMAGE_NAME>
docker push <ACR_REGSITRY_NAME>.azurecr.io/bonsai/cartpole
```

## Example run Dockerfile
```sh
docker build -t cartpole .
docker run --rm -it -e SIM_ACCESS_KEY="111" -e SIM_API_HOST="https://api.bons.ai" -e SIM_WORKSPACE="123"
```

## Example push to ACR(Assuming you logged in)
```sh
docker build -t cartpole .
docker tag cartpole bonsaisimpreprod.azurecr.io/bonsai/cartpole
docker push bonsaisimpreprod.azurecr.io/bonsai/cartpole
```

Once your image is registered in the ACR you can switch the web and click `Add Simulator` from
the left hand navigation. Enter the URL to the image there and give it a name. Use this name in
your Inkling to refer to the simulator.


## Microsoft Open Source Code of Conduct

This repository is subject to the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct).