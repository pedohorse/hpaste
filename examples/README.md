This directory contains a couple of plugin examples for hpaste.

The main idea of hpaste is to create ascii and url-safe representation of the snippet with assets and other metadata. You can see the result of that with **HCopy**
shelf button (not HCopyWeb that is by default bound to shortcut ctrl+alt+shift+C)

That huge piece of text then is fed to one of hpaste's **web plugins**, that take that huge text, store it somewhere and return you a small id (or wid, or handle, whatever you call it)  
The order of plugin being tried is defined in **HPaste Options** dialog  
The plugins themselves are read from **hpastewebplugins** directory

You can write your own web plugins very easily, it just requires you to reimplement a couple of methods, nothing more

#### Local network usage
You can easily adapt hpaste to share snippets inside your company's local network, without any internet access.  
There are two examples provided: 
- storing snippets in shared network directory
- storing snippets in a shared network sqlite database (this can easily be adapted to locally running mysql or postgres servers)

check the files and read comments to guide you through this little plugins' structures
