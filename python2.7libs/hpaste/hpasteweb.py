import hou  # for ui only
import hpastewebplugins
import widcacher
import random  # to shuffle plugins
import re  # to cleanup wid

from webclipboardbase import WebClipBoardWidNotFound


def webPack(asciiText, pluginList=None, maxChunkSize=None):
    allPackids=[]
    done = False

    while not done:
        packid = None
        if pluginList is None:
            pluginClasses = [x for x in hpastewebplugins.pluginClassList]
            random.shuffle(pluginClasses)
            pluginClasses.sort(reverse=True, key=lambda x: x.speedClass())
        else:
            pluginClasses = []
            for pname in pluginList:
                pluginClasses += [x for x in hpastewebplugins.pluginClassList if x.__name__ == pname]

        # sanity check
        print('www', len(asciiText))
        raise('lelol')
        if len(asciiText) > 2**24:
            if hou.isUiAvailable():
                if hou.ui.displayMessage('you are about to save %d Mb into a snippet. This is HIGHLY DISCOURAGED!',
                                         buttons=('Proceed', 'Cancel'), default_choice=1, close_choice=1,
                                         severity=hou.severityType.Warning) != 0:
                    raise RuntimeError('snippet too big. cancelled')
            else:
                raise RuntimeError('snippet too big. cancelled')
        #

        cls = None
        for cls in pluginClasses:
            try:
                packer = cls()
                chunklen = min(packer.maxStringLength(), len(asciiText))
                if maxChunkSize is not None:
                    chunklen = min(chunklen, maxChunkSize)
                chunk = asciiText[:chunklen]
                packid = packer.webPackData(chunk)
                asciiText = asciiText[chunklen:]
                break
            except Exception as e:
                print("error: %s" % str(e.message))
                print("failed to pack with plugin %s, looking for alternatives..." % cls.__name__)
                continue
        if packid is None or cls is None:
            print("all web packing methods failed, sorry :(")
            raise RuntimeError("couldnt web pack data")

        allPackids.append('@'.join((packid, cls.__name__)))
        done = len(asciiText) == 0
        # just a failsafe:
        if len(allPackids) > 128:
            raise RuntimeError("Failsafe triggered: for some reason too many chunks. plz check the chunkSize, or your plugins for too small allowed string sizes, or your data for sanity.")

    return '#'.join(allPackids)


def webUnpack(wid, useCached=True, cache=None):
    #just a bit cleanup the wid first, in case it was copied with extra spaces
    # strip witespaces, just to be sure
    wid = wid.strip()
    # strip comments if there are
    wid = re.sub(r'^\S+\s+', '', wid)
    #
    if useCached:
        if cache is None:  # default cacher
            cache = widcacher.WidCacher.globalInstance()
        if wid in cache:
            return cache[wid]

    allPackids = wid.split('#')
    asciiTextParts = []
    for awid in allPackids:
        if awid.count('@') != 1:
            raise RuntimeError('given wid is not a valid wid')
        id, cname = awid.split('@')

        pretendents = [x for x in hpastewebplugins.pluginClassList if x.__name__ == cname]
        if len(pretendents) == 0:
            raise RuntimeError("No plugins that can process this wid found")

        asciiText = None
        for cls in pretendents:
            try:
                unpacker = cls()
                asciiText = unpacker.webUnpackData(id)
                break
            except WebClipBoardWidNotFound as e:
                raise RuntimeError('item "%s" does not exist. it may have expired' % e.wid)
            except Exception as e:
                print("error: %s: %s" % (str(type(e)), str(e.message)))
                print("Exception: %s" % repr(e))
                print("keep trying...")
                continue
        if asciiText is None:
            print("failed")
            raise RuntimeError("couldn't web unpack data")
        asciiTextParts.append(asciiText)

    finalText = ''.join(asciiTextParts)
    if useCached and cache is not None:
        cache[wid] = finalText

    return finalText