# Lab 1 — Self-hosting compiler bootstrapping

Bootstrapping the P5 Pascal compiler.

Mount file system of virtual machine to access files from host machine:

```bash
cd /home/z/Documents/BMSTU-Compilers/lab1
# mount shared folder
sshfs z@192.168.122.186:/home/z/Downloads/p5 ./vm-shared -o reconnect,ServerAliveInterval=15,ServerAliveCountMax=3
# unmount shared folder
fusermount -u ./vm-shared
```

## Solution

Run `hello.pas` program with provided compiler and interpreter:

```bash
./pcom <hello.pas
mv prr prd
./pint
```

Compile pcom2.pas (pcom -> pco2 -> hello2.pas)

```bash
./pcom <pcom2.pas
mv prr prd
# prd is assembly of pcom.pas
# run hello2.pas with prd as compiler
./pint <hello2.pas
mv prr prd
./pint
```

Compile pcom3.pas (pcom -> pcom2 -> pcom3 -> hello2.pas)

```bash
./pcom <pcom2.pas
mv prr prd
cp prd prd_pcom2
# compile pcom3.pas with pcom2 as compiler
./pint <pcom3.pas
mv prr prd
cp prd prd_pcom3
# compile hello2.pas with pcom3 as compiler
./pint <hello2.pas
```

```bash
diff -u src/pcom.pas vm-shared/pcom2.pas
diff -u vm-shared/pcom2.pas vm-shared/pcom3.pas
```

## Links

- [pascal compiler sources](./lab1.1.zip)
- [wiki bootstraping](<https://en.wikipedia.org/wiki/Bootstrapping_(compilers)>)
