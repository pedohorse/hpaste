# hpaste
simple plain text snippet exchange for Houdini

for simple and fast exchange of node packs through any messenger

**Hpaste** works/tested for **Houdini 16.0, 15.5**. Should work also for 15.0 and maybe even less, to the point when Qt appeared in Houdini
**HCollections** should work in **Houdini 16.x, 15.5** with both Qt4 and Qt5

You can read a bit more about it in here:
* https://cgallin.blogspot.com/2017/09/hpaste.html
* https://cgallin.blogspot.com/2018/02/hpaste-update.html
* https://cgallin.blogspot.com/2018/01/hcollections.html

## installation ##
### Super short and simple variant ###
1. Download the contents of this repository as ZIP
2. Unzip it into your Houdini user folder, something like C:\Users\\<**USER>**\Documents\houdini16.5\
(you actually don't need to copy the example folder from there)
3. Enjoy!

### a bit longer variant ###
1. copy **hpaste** folder from python2.7libs to your local script folder
    * for example: C:\Users\\<**USER>**\Documents\houdini16.0\python2.7libs\
        * hint: create python2.7libs folder if it doesnt exist 
2. copy contents of **toolbar** folder to your toolbar folder
    * for example: C:\Users\\<**USER>**\Documents\houdini16.0\toolbar\
        * hint: create toolbar folder if it doesnt exist 
3. copy **.hpaste_githubcollection** into your **user** folder to gain access to a demo public collection straight away
4. start Houdini !!
5. locate the HPaste shelf in shelf list
6. if you want fancy icons for the buttons - copy **config** folder content into your config
    * for example: C:\Users\\<**USER>**\Documents\houdini16.0\config\
        * hint: create config folder if it doesnt exist 
        * hint: merge icons folder with yours one if you dont have one yet
7. You can download file **HotkeyOverrides** to your Houdini user folder to automatically set hotkeys to
      1. Ctrl+Alt+Shift+C for HCopyWeb
      2. Ctrl+Alt+Shift+V for HPasteWeb
      3. Shift+Tab for HCollections
   * if you want - you can assign **hotkeys** to copy-paste and collection commands manually with: 
      * right-click on the **tool button** on the **shelf** -> **Edit Tool**, **Hotkeys** tab
   * **Note!** That you **will not** be able to use collections without a **hotkey**, so set it up if you plan to use them
8. and may the force be with you

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
* **collections:**
    1. go to **hpaste** shelf tab, notice the last button - **Collection Authorization** - it opens an account manager
    2. If you want to have your own collection which you can read/write and from which other people can read public snippets - you will have to:
       1. register at **github.com**
       2. **confirm your email** after registration
       3. open **Collection Authorization** and click **add** in the upper part of the opened account manager and enter your credentials
       4. you will see your account name appears in the upper list of the account manager - this means you are ready to go!
       5. click **re-initialize collections** to force collections to reread new added accounts
    3. If you want to use public collections in read only manner - just:
       1. open **Collection Authorization** and click lower **add** in the opened account manager
       2. enter a known name of a collection you want to add (check spelling twice!)
       3. click **re-initialize collections** to force collections to reread new added accounts


## description ##
* shelf goes with 6 buttons now: 
    * **hcopy**, **hpaste** to copy-paste direct chunks of code
        * pluses: doesnt require any 3-rd party web resources or watever
        * minuses: code chunk can be pretty huge!
    * **hcopyweb**, **hpasteweb** to copy-paste web ids for the code
        * pluses: links are super small and cozy
        * minuses: this require the code to be stored on 3-rd party web resource, and it can be accessed (pure theoretically) by anyone in the world!
   * **hpastecollection** - cloud storage for your snippets
        * require github account
        * works only from a hotkey in the Network Editor
   * **hpastecollectionauth** - account manager for hpaste collections
        * add any number of private and public collections to use

## Attributions ##
Icons in hpaste-demo-collection:
* Icon made by Freepik from www.flaticon.com
* Icon made by Pixel perfect from www.flaticon.com

