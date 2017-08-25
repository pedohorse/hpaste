# hpaste
simple plain text snippet exchange for Houdini

for simple and fast exchange of node packs through any messenger

Works/tested for **Houdini 16.0, 15.5**. Should work also for 15.0 and maybe even less, to the point when Qt appeared in Houdini

## installation ##
1. copy **hpaste** folder from python2.7libs to your local script folder
    * for example: C:\Users\\<**USER>**\Documents\houdini16.0\python2.7libs\
        * hint: create python2.7libs folder if it doesnt exist 
2. copy contents of **toolbar** folder to your toolbar folder
    * for example: C:\Users\\<**USER>**\Documents\houdini16.0\toolbar\
        * hint: create toolbar folder if it doesnt exist 
3. start Houdini !!
4. locate the HPaste shelf in shelf list
5. if you want fancy icons for the buttons - copy **config** folder content into your config
    * for example: C:\Users\\<**USER>**\Documents\houdini16.0\config\
        * hint: create config folder if it doesnt exist 
        * hint: merge icons folder with yours one if you dont have one yet
6. if you want - you can assign **hotkeys** to copy-paste commands with: 
    * right-click on the **tool button** on the **shelf** -> **Edit Tool**, **Hotkeys** tab
    * set them to something not too common like Ctrl+Alt+Shift+C ,  Ctrl+Alt+Shift+V
7. and may the force be with you

## how to use: ##
* **to copy:**
    1. select nodes you want to copy (nodes must be of the same parent!)
    2. press **hcopy/hcopyweb** button (or hotkey) now you have the code/web-id in your clipboard
    3. paste it to some messenger and send to a collegue
* **to paste:**
    1. receive code or web-id
    2. copy received text to your system clipboard
    3. in houdini - open the node viewer to the location you want to paste your nodes
    4. press **hpaste/hpasteweb** button (or hotkey) depending on if you are pasting code or web-id


## description ##
* shelf goes with 4 buttons now: 
    * **hcopy**, **hpaste** to copy-paste direct chunks of code
        * pluses: doesnt require any 3-rd party web resources or watever
        * minuses: code chunk can be pretty huge!
    * **hcopyweb**, **hpasteweb** to copy-paste web ids for the code
        * pluses: links are super small and cozy
        * minuses: this require the code to be stored on 3-rd party web resource, and it can be accessed (pure theoretically) by anyone in the world!
        

