# Systemd user resource limitation imposer

This script impose some resource constrain upon every user
session when they are first created.  In other words, when a user's
first login, our script catch a signal and invoke systemd's API to set
constraint over her resource usage.

See [here](https://www.freedesktop.org/software/systemd/man/systemd.resource-control.html)
for a list of available resource type.


### Example

Apply the `MemoryLimit` Systemd resource rule to the user `john`:

```
    $ ./logind-hook.py --users john --rules MemoryLimit=53687091200

```

Apply the `MemoryLimit` Systemd resource to all users:

```
    $ ./logind-hook.py --rules MemoryLimit=53687091200
```
