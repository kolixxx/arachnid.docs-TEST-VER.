## Building UI template

from `custom-ui` folder run
```
docker run --rm -v "${PWD}:/workspace" -w /workspace node:18 bash -c "npm install && npx gulp bundle"
```

or 

```
docker run --rm -v "${PWD}:/workspace" -w /workspace node:18 npx gulp bundle
```

when npm packages already installed


## Building documentation
from `content` folder

```
docker run -v "${PWD}:/antora" --rm -t antora/antora antora-playbook.yml
```