# hpaste
simple plain text snippet exchange for Houdini

## installation ##
1. copy **hpaste** folder from python2.7libs to your local script folder
    * for example: C:\Users\\<**USER>**\Documents\houdini16.0\python2.7libs\
2. copy contents of **toolbar** folder to your toolbar folder
    * for example: C:\Users\\<**USER>**\Documents\houdini16.0\toolbar\
3. start Houdini !!
4. locate the HPaste shelf in shelf list
5. if you want - you can assign **hotkeys** to copy-paste commands with: 
    * right-click on the **tool button** on the **shelf** -> **Edit Tool**, **Hotkeys** tab
    * set them to something not too common like Ctrl+Alt+Shift+C ,  Ctrl+Alt+Shift+V
6. and may the force be with you

## description ##
* shelf goes with 4 buttons now: 
    * **hcopy**, **hpaste** to copy-paste direct chunks of code
        * pluses: doesnt require any 3-rd party web resources or watever
        * minuses: code chunk can be pretty huge!
    * **hcopyweb**, **hpasteweb** to copy-paste web ids for the code
        * pluses: links are super small and cozy
        * minuses: this require the code to be stored on 3-rd party web resource, and it can be accessed (pure theoretically) by anyone in the world!
        
* to use:
    * to copy:
        1. select nodes you want to copy (nodes must be of the same parent!)
        2. press **hcopy/hcopyweb** button (or hotkey) now you have the code/web-id in your clipboard
        3. paste it to some messenger and send to a collegue
    * to paste:
        1. receive code or web-id
        2. copy received text to your system clipboard
        3. in houdini - open the node viewer to the location you want to paste your nodes
        4. press **hpaste/hpasteweb** button (or hotkey) depending on if you are pasting code or web-id
    
