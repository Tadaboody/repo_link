# Repo Link
Open github links inside your favorite editor

Automatically runs `clone`, `checkout`, and opens the correct line for you!

## Usage:
```sh
usage: repo_link [-h] [--parents PARENTS [PARENTS ...]] [--editor EDITOR]
                 [--config CONFIG]
                 link

Open github link in editor

positional arguments:
  link                  The opened link

optional arguments:
  -h, --help            show this help message and exit
  --parents PARENTS [PARENTS ...]
                        Directories where the repository will be searched. if
                        not found it will be cloned into the first one
  --editor EDITOR       The editor opened (default: EDITOR)
  --config CONFIG       A json file where command line options can be hard-
                        coded, default:~/.repo_link_config.json
```
A config json can be given, it will look like this
```js
{
    "editor":"vim",
    "parents":["~/Forks","~"]
}
```