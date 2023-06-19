### dependencies
- python3
- python3-click
- ostree
- ostree-rs-ext
- skopeo
- bubblewrap
- qemu-user and binfmt (x86)
    - Arch Linux: Install `qemu-user-static` and `qemu-user-static-binfmt`.

### preparation
append the content of `registries.conf` to `~/.config/containers/registries.conf`

### usage
```
# init ostree repo
ruyi init
# pull os image
ruyi pull arch archlinux:riscv
# checkout image into working copy
ruyi checkout arch arch-1
# enter working copy
ruyi activate arch-1
# commit changes
ruyi commit arch-1 arch-new
# show available images
ruyi refs
```
