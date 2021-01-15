[![Build Status](https://travis-ci.org/lewisemm/vistagrid-backend-k8.svg?branch=master)](https://travis-ci.org/lewisemm/vistagrid-backend-k8) [![Coverage Status](https://coveralls.io/repos/github/lewisemm/vistagrid-backend-k8/badge.svg?branch=master)](https://coveralls.io/github/lewisemm/vistagrid-backend-k8?branch=master)

# vistagrid-backend-k8

## Setup and Install Instructions


### Prerequisite Environment Variables
This project requires the following environment variables to be defined in order to run.
* SQLALCHEMY_DATABASE_URI
* JWT_SECRET_KEY

### Running the project
1. Open terminal and navigate to your projects directory.

```sh
cd ~/projects/
```

2. Clone the repo.

```sh
git clone git@github.com:lewisemm/vistagrid-backend-k8.git
```

3. `cd` into the `vistagrid-backend-k8` directory.

```sh
cd vistagrid-backend-k8
```

4. Start the app.

```sh
docker-compose up
```
