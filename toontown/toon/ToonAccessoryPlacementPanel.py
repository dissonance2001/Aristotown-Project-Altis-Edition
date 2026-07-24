from direct.gui.DirectGui import *
from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import TextNode, Vec4

from toontown.toon import ToonDNA, AccessoryGlobals
from toontown.toonbase import TTLocalizer, ToontownGlobals

import copy
import json
import os




def _findAccessoryRegistryPath():
    rel = os.path.join('resources', 'phase_14', 'accessories', 'accessories_registry.json')
    roots = []

    cur = os.path.abspath(os.getcwd())
    while True:
        if cur not in roots:
            roots.append(cur)
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent

    try:
        cur = os.path.dirname(os.path.abspath(__file__))
        while True:
            if cur not in roots:
                roots.append(cur)
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
    except:
        pass

    for root in roots:
        test = os.path.join(root, rel)
        if os.path.isfile(test):
            return test

    return None

def _detectAccessoryType(fileName):
    lowerName = fileName.lower()

    if 'glasses' in lowerName or 'glass' in lowerName:
        return 'glasses'
    if 'backpack' in lowerName or 'pack' in lowerName:
        return 'backpack'
    if 'shoes' in lowerName or 'shoe' in lowerName:
        return 'shoes'
    if 'hat' in lowerName:
        return 'hat'

    return None


def _getNextCustomAccessoryId(accessories, accessoryType):
    startIds = {
        'hat': 1000,
        'glasses': 2000,
        'backpack': 3000,
        'shoes': 4000
    }

    nextId = startIds[accessoryType]

    for accessoryData in accessories.values():
        if not isinstance(accessoryData, dict):
            continue
        if accessoryData.get('type') != accessoryType:
            continue

        accessoryId = accessoryData.get('id')
        if isinstance(accessoryId, int) and accessoryId >= nextId:
            nextId = accessoryId + 1

    return nextId


def _rescanCustomAccessories():
    registryPath = _findAccessoryRegistryPath()
    if not registryPath:
        print 'Accessory editor rescan failed: registry path not found.'
        return False

    accessoryRoot = os.path.dirname(registryPath)

    try:
        registryFile = open(registryPath, 'r')
        try:
            registry = json.load(registryFile)
        finally:
            registryFile.close()
    except:
        registry = {
            'version': 2,
            'accessories': {}
        }

    if not isinstance(registry, dict):
        registry = {}

    accessories = registry.get('accessories')
    if not isinstance(accessories, dict):
        accessories = {}
        registry['accessories'] = accessories

    registry['version'] = 2
    changed = False
    foundCount = 0

    searchDirectories = [('', accessoryRoot)]

    try:
        rootEntries = sorted(os.listdir(accessoryRoot))
    except Exception as error:
        print 'Accessory editor rescan failed:', error
        return False

    for folderName in rootEntries:
        folderPath = os.path.join(accessoryRoot, folderName)
        if os.path.isdir(folderPath):
            searchDirectories.append((folderName, folderPath))

    for folderName, folderPath in searchDirectories:
        try:
            fileNames = sorted(os.listdir(folderPath))
        except:
            continue

        for fileName in fileNames:
            fullPath = os.path.join(folderPath, fileName)

            if not os.path.isfile(fullPath):
                continue
            if not fileName.lower().endswith('.bam'):
                continue

            accessoryType = _detectAccessoryType(fileName)
            if accessoryType is None:
                continue

            foundCount += 1

            if folderName:
                registryKey = folderName + '/' + fileName
                modelPath = 'phase_14/accessories/%s/%s' % (
                    folderName,
                    os.path.splitext(fileName)[0]
                )
            else:
                registryKey = fileName
                modelPath = 'phase_14/accessories/%s' % (
                    os.path.splitext(fileName)[0]
                )

            accessoryData = accessories.get(registryKey)
            if not isinstance(accessoryData, dict):
                accessoryData = {}
                accessories[registryKey] = accessoryData
                changed = True

            displayName = os.path.splitext(fileName)[0]

            if accessoryData.get('folder') != folderName:
                accessoryData['folder'] = folderName
                changed = True

            if accessoryData.get('name') != displayName:
                accessoryData['name'] = displayName
                changed = True

            if accessoryData.get('type') != accessoryType:
                accessoryData['type'] = accessoryType
                changed = True

            if accessoryData.get('model') != modelPath:
                accessoryData['model'] = modelPath
                changed = True

            if not isinstance(accessoryData.get('id'), int):
                accessoryData['id'] = _getNextCustomAccessoryId(
                    accessories,
                    accessoryType
                )
                changed = True

    if changed:
        temporaryPath = registryPath + '.tmp'

        try:
            outputFile = open(temporaryPath, 'w')
            try:
                json.dump(registry, outputFile, indent=4, sort_keys=True)
                outputFile.write('\n')
            finally:
                outputFile.close()

            if os.path.isfile(registryPath):
                os.remove(registryPath)
            os.rename(temporaryPath, registryPath)
        except Exception as error:
            print 'Accessory editor registry rescan write failed:', error
            try:
                if os.path.isfile(temporaryPath):
                    os.remove(temporaryPath)
            except:
                pass
            return False

    print 'Accessory editor rescan complete: %s model(s), changed=%s' % (
        foundCount,
        changed
    )
    return True


def _getCustomAccessories(kind):
    path = _findAccessoryRegistryPath()
    if not path:
        return []

    try:
        registryFile = open(path, 'r')
        try:
            reg = json.load(registryFile)
        finally:
            registryFile.close()
    except:
        return []

    result = []
    for data in reg.get('accessories', {}).values():
        if not isinstance(data, dict):
            continue
        if data.get('type') != kind:
            continue

        internalName = data.get('name', 'Unknown')
        displayName = data.get('display_name')

        if not isinstance(displayName, basestring) or not displayName.strip():
            displayName = internalName.replace('_', ' ').title()

        result.append((
            internalName,
            data.get('id', 0),
            data.get('style'),
            displayName
        ))

    result.sort(key=lambda item: item[1])
    return result


def _findAccessoryPlacementsPath():
    registryPath = _findAccessoryRegistryPath()
    if registryPath:
        return os.path.join(os.path.dirname(registryPath), 'accessory_placements.json')
    return None


def _loadAccessoryPlacements():
    path = _findAccessoryPlacementsPath()
    if not path or not os.path.isfile(path):
        return {}

    try:
        placementFile = open(path, 'r')
        try:
            data = json.load(placementFile)
        finally:
            placementFile.close()

        if isinstance(data, dict):
            return data
    except Exception as error:
        print 'Accessory editor placement read failed:', error

    return {}

HATS = 0
GLASSES = 1
BACKPACKS = 2


class ToonAccessoryPlacementPanel(object):

    def __init__(self):
        self.mode = HATS
        self.selectedName = None
        self.selectedId = None
        self.isCustom = False
        self.currentPlacement = None
        self.copiedPlacement = None
        self.accessoryButtons = []
        self.sliders = []
        self.sliderEntries = []
        self.destroyed = False
        self.previewToon = None

        self.dialogGeom = DGG.getDefaultDialogGeom()
        self.buttonGui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui')
        self.scrollGui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        self.sliderGui = loader.loadModel('phase_3/models/gui/pick_a_toon_gui')
        self.closeGui = loader.loadModel('phase_3.5/models/gui/avatar_panel_gui')

        self.root = DirectFrame(
            parent=base.aspect2d,
            relief=None,
            geom=self.dialogGeom,
            geom_scale=(2.15, 1, 1.62),
            geom_color=(0.82, 0.68, 0.42, 1),
            frameSize=(-1.25, 1.25, -0.92, 0.92)
        )

        self.title = DirectLabel(
            parent=self.root,
            relief=None,
            text='Accessory Placement Editor',
            text_font=ToontownGlobals.getSignFont(),
            text_scale=0.075,
            text_fg=(1, 0.82, 0.12, 1),
            text_shadow=(0.2, 0.08, 0, 1),
            pos=(0, 0, 0.765)
        )

        self.modeHat = self._makeButton('Hats', (-0.55, 0, 0.67), self.changeMode, [HATS])
        self.modeGlasses = self._makeButton('Glasses', (0, 0, 0.67), self.changeMode, [GLASSES])
        self.modeBackpacks = self._makeButton('Backpacks', (0.55, 0, 0.67), self.changeMode, [BACKPACKS])

        self.searchEntry = DirectEntry(
            parent=self.root,
            relief=DGG.SUNKEN,
            frameColor=(0.93, 0.97, 1, 1),
            borderWidth=(0.06, 0.06),
            text_fg=(0.12, 0.07, 0.02, 1),
            scale=0.05,
            width=12,
            pos=(-1.00, 0, 0.55),
            initialText='',
            numLines=1,
            focus=0,
            cursorKeys=1,
            command=self.applySearch,
            focusInCommand=self._searchFocusIn,
            focusOutCommand=self._searchFocusOut
        )

        self.searchButton = self._makeButton('Search', (-0.17, 0, 0.55), self.applySearch)
        self.clearButton = self._makeButton('Clear', (0.16, 0, 0.55), self.clearSearch)

        self.listFrame = DirectFrame(
            parent=self.root,
            relief=DGG.SUNKEN,
            frameColor=(0.85, 0.95, 1, 1),
            borderWidth=(0.02, 0.02),
            frameSize=(-1.05, -0.12, -0.62, 0.50),
            pos=(0, 0, 0)
        )

        self.accessoryList = DirectScrolledList(
            parent=self.root,
            relief=None,
            pos=(-0.98, 0, -0.05),
            itemFrame_pos=(0, 0, 0.48),
            itemFrame_relief=None,
            itemFrame_frameSize=(0, 0.86, -1.05, 0),
            numItemsVisible=14,
            forceHeight=0.07,
            incButton_image=(
                self.scrollGui.find('**/FndsLst_ScrollUp'),
                self.scrollGui.find('**/FndsLst_ScrollDN'),
                self.scrollGui.find('**/FndsLst_ScrollUp_Rllvr'),
                self.scrollGui.find('**/FndsLst_ScrollUp')
            ),
            incButton_relief=None,
            incButton_scale=(0.85, 0.85, -0.85),
            incButton_pos=(0.43, 0, -0.62),
            decButton_image=(
                self.scrollGui.find('**/FndsLst_ScrollUp'),
                self.scrollGui.find('**/FndsLst_ScrollDN'),
                self.scrollGui.find('**/FndsLst_ScrollUp_Rllvr'),
                self.scrollGui.find('**/FndsLst_ScrollUp')
            ),
            decButton_relief=None,
            decButton_scale=(0.85, 0.85, 0.85),
            decButton_pos=(0.43, 0, 0.51)
        )

        self.info = DirectLabel(
            parent=self.root,
            relief=None,
            text='Select an accessory',
            text_scale=0.045,
            text_fg=(0.25, 0.12, 0.02, 1),
            text_shadow=(1, 0.92, 0.68, 1),
            text_align=TextNode.ALeft,
            pos=(0.32, 0, 0.535)
        )

        self._buildTransformControls()

        self.saveButton = self._makeButton('Save', (0.20, 0, -0.72), self.savePlacement)
        self.exportButton = self._makeButton('Export', (0.55, 0, -0.72), self.exportPlacement)
        self.resetButton = self._makeButton('Reset', (0.90, 0, -0.72), self.resetPlacement)

        self.printButton = self._makeButton('Print Placement', (0.20, 0, -0.83), self.printPlacement)
        self.copyButton = self._makeButton('Copy', (0.55, 0, -0.83), self.copyPlacement)
        self.pasteButton = self._makeButton('Paste', (0.90, 0, -0.83), self.pastePlacement)
        self.closeButton = self._makeButton('Close', (0.86, 0, 0.76), self.destroy)

        self.populateList()
        self.createPreviewToon()

    def createPreviewToon(self):
        if self.previewToon is not None:
            try:
                self.previewToon.cleanup()
            except:
                pass
            try:
                self.previewToon.removeNode()
            except:
                pass
            self.previewToon = None

        try:
            from toontown.toon import Toon

            dna = ToonDNA.ToonDNA()
            dna.makeFromNetString(base.localAvatar.style.makeNetString())

            self.previewToon = Toon.Toon()
            self.previewToon.setDNA(dna)
            self.previewToon.reparentTo(base.aspect2d)
            self.previewToon.setPos(1.40, 0, -0.42)
            self.previewToon.setScale(0.18)
            self.previewToon.setH(180)
            self.previewToon.setDepthTest(True)
            self.previewToon.setDepthWrite(True)
            self.previewToon.setBin('fixed', 20)

            try:
                self.previewToon.setHat(*base.localAvatar.getHat())
            except:
                pass

            try:
                self.previewToon.setGlasses(*base.localAvatar.getGlasses())
            except:
                pass

            try:
                self.previewToon.setBackpack(*base.localAvatar.getBackpack())
            except:
                pass

            try:
                self.previewToon.loop('neutral')
            except:
                pass
        except Exception as error:
            print 'Accessory editor preview creation failed:', error
            self.previewToon = None

    def refreshPreviewAccessory(self):
        if self.previewToon is None:
            return

        try:
            if self.mode == HATS:
                if self.isCustom:
                    self.previewToon.hat = (self.selectedId, 0, 0)
                    self.previewToon.generateHat()
                elif self.selectedName is not None:
                    self.previewToon.setHat(*ToonDNA.HatStyles[self.selectedName])
            elif self.mode == GLASSES:
                if self.isCustom:
                    self.previewToon.glasses = (self.selectedId, 0, 0)
                    self.previewToon.generateGlasses()
                elif self.selectedName is not None:
                    self.previewToon.setGlasses(*ToonDNA.GlassesStyles[self.selectedName])
            else:
                if self.isCustom:
                    self.previewToon.backpack = (self.selectedId, 0, 0)
                    self.previewToon.generateBackpack()
                elif self.selectedName is not None:
                    self.previewToon.setBackpack(*ToonDNA.BackpackStyles[self.selectedName])
        except Exception as error:
            print 'Accessory editor preview refresh failed:', error

    def _makeButton(self, text, pos, command, extraArgs=None):
        if extraArgs is None:
            extraArgs = []

        return DirectButton(
            parent=self.root,
            relief=None,
            image=(
                self.buttonGui.find('**/QuitBtn_UP'),
                self.buttonGui.find('**/QuitBtn_DN'),
                self.buttonGui.find('**/QuitBtn_RLVR'),
                self.buttonGui.find('**/QuitBtn_RLVR')
            ),
            image_scale=(0.72, 1, 0.78),
            text=text,
            text_scale=0.045,
            text_pos=(0, -0.0125),
            text_fg=(0.18, 0.08, 0.01, 1),
            text1_fg=(0.18, 0.08, 0.01, 1),
            text2_fg=(0.18, 0.08, 0.01, 1),
            text3_fg=(0.45, 0.35, 0.18, 1),
            pos=pos,
            command=command,
            extraArgs=extraArgs
        )

    def _buildTransformControls(self):
        labels = (
            ('X', -1.0, 1.0),
            ('Y', -1.0, 1.0),
            ('Z', -1.0, 1.0),
            ('H', 0.0, 360.0),
            ('P', 0.0, 360.0),
            ('R', 0.0, 360.0),
            ('SX', 0.01, 1.0),
            ('SY', 0.01, 1.0),
            ('SZ', 0.01, 1.0),
        )

        startZ = 0.43
        for i, data in enumerate(labels):
            label, minimum, maximum = data
            z = startZ - (i * 0.12)

            DirectLabel(
                parent=self.root,
                relief=None,
                text=label,
                text_scale=0.045,
                text_fg=(0.25, 0.12, 0.02, 1),
                text_shadow=(1, 0.92, 0.68, 1),
                pos=(-0.07, 0, z)
            )

            slider = DirectSlider(
                parent=self.root,
                range=(minimum, maximum),
                value=0,
                pageSize=0,
                scale=(0.30, 0.35, 0.35),
                pos=(0.30, 0, z),
                thumb_geom=(
                    self.sliderGui.find('**/QuitBtn_UP'),
                    self.sliderGui.find('**/QuitBtn_DN'),
                    self.sliderGui.find('**/QuitBtn_RLVR'),
                    self.sliderGui.find('**/QuitBtn_UP')
                ),
                thumb_relief=None,
                thumb_geom_hpr=(0, 0, -90),
                thumb_geom_scale=(0.35, 1, 0.65),
                frameColor=(0.55, 0.34, 0.12, 1),
                command=self.onSliderChanged,
                extraArgs=[i]
            )

            entry = DirectEntry(
                parent=self.root,
                relief=DGG.SUNKEN,
                frameColor=(0.93, 0.97, 1, 1),
                borderWidth=(0.06, 0.06),
                text_fg=(0.12, 0.07, 0.02, 1),
                scale=0.045,
                width=7,
                pos=(0.70, 0, z - 0.01),
                initialText='0',
                numLines=1,
                focus=0,
                cursorKeys=1,
                command=self.onEntryChanged,
                extraArgs=[i]
            )

            self.sliders.append(slider)
            self.sliderEntries.append(entry)

    def changeMode(self, mode):
        self.mode = mode
        self.selectedName = None
        self.selectedId = None
        self.isCustom = False
        self.currentPlacement = None
        self.info['text'] = 'Select an accessory'
        self.populateList()

    def clearAccessoryButtons(self):
        items = self.accessoryList['items'][:]

        for item in items:
            try:
                self.accessoryList.removeItem(item, refresh=0)
            except:
                pass

        self.accessoryList.refresh()

        for button in self.accessoryButtons:
            try:
                button.destroy()
            except:
                pass

        self.accessoryButtons = []

    def populateList(self, searchText=''):
        self.clearAccessoryButtons()

        try:
            ToonDNA.registerCustomAccessoriesAsNative()
        except Exception as error:
            print 'Accessory editor native rescan failed:', error

        searchText = searchText.lower().replace(' ', '')

        if self.mode == HATS:
            styles = ToonDNA.HatStyles
        elif self.mode == GLASSES:
            styles = ToonDNA.GlassesStyles
        else:
            styles = ToonDNA.BackpackStyles

        names = list(styles.keys())
        names.sort()

        custom = []
        if self.mode == HATS:
            custom = _getCustomAccessories('hat')
        elif self.mode == GLASSES:
            custom = _getCustomAccessories('glasses')
        else:
            custom = _getCustomAccessories('backpack')

        customStyleNames = set()
        customIds = set()

        for customName, customId, customStyle, customDisplayName in custom:
            if customStyle:
                customStyleNames.add(customStyle)
            if isinstance(customId, int):
                customIds.add(customId)

        for name in names:
            if name == 'none':
                continue

            style = styles.get(name)

            if name in customStyleNames:
                continue

            if isinstance(style, (list, tuple)) and style:
                if style[0] in customIds:
                    continue

            realName = self.getRealName(name)
            if searchText:
                parsed = realName.lower().replace(' ', '')
                if searchText not in parsed:
                    continue

            button = DirectButton(
                relief=None,
                text=realName,
                text_scale=0.045,
                text_align=TextNode.ALeft,
                text_fg=(0.15, 0.08, 0.02, 1),
                text1_bg=(0.5, 0.9, 1, 1),
                text2_bg=(1, 1, 0.25, 1),
                text3_fg=(0.35, 0.65, 0.35, 1),
                command=self.selectAccessory,
                extraArgs=[name,False]
            )

            self.accessoryButtons.append(button)
            self.accessoryList.addItem(button, refresh=0)

        for cname, cid, customStyle, customDisplayName in custom:
            if searchText:
                parsed = customDisplayName.lower().replace(' ', '')
                if searchText not in parsed:
                    continue

            button=DirectButton(
                relief=None,
                text=customDisplayName,
                text_scale=0.045,
                text_align=TextNode.ALeft,
                text_fg=(0.15,0.08,0.02,1),
                text1_bg=(0.5,0.9,1,1),
                text2_bg=(1,1,0.25,1),
                text3_fg=(0.35,0.65,0.35,1),
                command=self.selectAccessory,
                extraArgs=[cname,True])
            self.accessoryButtons.append(button)
            self.accessoryList.addItem(button,refresh=0)

        self.accessoryList.refresh()

    def getRealName(self, name):
        try:
            if self.mode == HATS and hasattr(TTLocalizer, 'HatStylesDescriptions'):
                return TTLocalizer.HatStylesDescriptions.get(name, name)
            if self.mode == GLASSES and hasattr(TTLocalizer, 'GlassesStylesDescriptions'):
                return TTLocalizer.GlassesStylesDescriptions.get(name, name)
            if self.mode == BACKPACKS and hasattr(TTLocalizer, 'BackpackStylesDescriptions'):
                return TTLocalizer.BackpackStylesDescriptions.get(name, name)
        except:
            pass
        return name


    def _searchFocusIn(self):
        try:
            if hasattr(base, 'ttwl'):
                base.ttwl.typeGrabbed = 1
        except:
            pass

    def _searchFocusOut(self):
        try:
            if hasattr(base, 'ttwl'):
                base.ttwl.typeGrabbed = 0
        except:
            pass

    def applySearch(self, text=None):
        if text is None:
            text = self.searchEntry.get()
        self.populateList(text)

    def clearSearch(self):
        self.searchEntry.set('')
        self.populateList('')

    def _saveEquippedAccessories(self):
        avatar = getattr(base, 'localAvatar', None)
        if avatar is None:
            return False

        try:
            distributedAvatar = base.cr.doId2do.get(avatar.doId)
            if distributedAvatar is not None:
                avatar = distributedAvatar
        except:
            pass

        def normalizeAccessory(value):
            try:
                return (
                    int(value[0]),
                    int(value[1]),
                    int(value[2])
                )
            except:
                return (0, 0, 0)

        try:
            hatValue = avatar.getHat()
        except:
            hatValue = getattr(avatar, 'hat', (0, 0, 0))

        try:
            glassesValue = avatar.getGlasses()
        except:
            glassesValue = getattr(avatar, 'glasses', (0, 0, 0))

        try:
            backpackValue = avatar.getBackpack()
        except:
            backpackValue = getattr(avatar, 'backpack', (0, 0, 0))

        try:
            shoesValue = avatar.getShoes()
        except:
            shoesValue = getattr(avatar, 'shoes', (0, 0, 0))

        hat = normalizeAccessory(hatValue)
        glasses = normalizeAccessory(glassesValue)
        backpack = normalizeAccessory(backpackValue)
        shoes = normalizeAccessory(shoesValue)

        try:
            avatar.sendUpdate(
                'requestSetAccessories',
                [
                    hat[0], hat[1], hat[2],
                    glasses[0], glasses[1], glasses[2],
                    backpack[0], backpack[1], backpack[2],
                    shoes[0], shoes[1], shoes[2]
                ]
            )
            print 'Accessory editor save request sent:', hat, glasses, backpack, shoes
            return True
        except Exception as error:
            print 'Accessory editor could not save equipped accessories:', error
            return False

    def selectAccessory(self, name, isCustom=False):
        self.selectedName = name
        self.isCustom=isCustom
        if isCustom:
            path = _findAccessoryRegistryPath()
            savedPlacement = None

            if path:
                try:
                    registryFile = open(path, 'r')
                    try:
                        reg = json.load(registryFile)
                    finally:
                        registryFile.close()

                    for accessoryData in reg.get('accessories', {}).values():
                        if not isinstance(accessoryData, dict):
                            continue
                        if accessoryData.get('name') != name:
                            continue

                        self.selectedId = accessoryData.get('id')
                        break
                except Exception as error:
                    print 'Accessory editor registry read failed:', error

            if self.selectedId is not None:
                placementData = _loadAccessoryPlacements()
                typeName = {
                    HATS: 'hat',
                    GLASSES: 'glasses',
                    BACKPACKS: 'backpack'
                }[self.mode]

                savedData = placementData.get(typeName, {}).get(
                    str(self.selectedId), {}
                ).get(self.getPlacementKey())

                if isinstance(savedData, dict):
                    pos = savedData.get('pos')
                    hpr = savedData.get('hpr')
                    scale = savedData.get('scale')

                    if pos is not None and hpr is not None and scale is not None:
                        savedPlacement = (
                            tuple(pos),
                            tuple(hpr),
                            tuple(scale)
                        )

            if self.selectedId is None:
                print 'Accessory editor could not find custom accessory:', name
                self.info['text'] = '[Custom] %s (not found)' % name
                return

            if savedPlacement is not None:
                self.currentPlacement = copy.deepcopy(savedPlacement)

                key = self.getPlacementKey()
                if self.mode == HATS:
                    table = AccessoryGlobals.ExtendedHatTransTable
                elif self.mode == GLASSES:
                    table = AccessoryGlobals.ExtendedGlassesTransTable
                else:
                    table = AccessoryGlobals.ExtendedBackpackTransTable

                if self.selectedId not in table:
                    table[self.selectedId] = {}
                table[self.selectedId][key] = copy.deepcopy(savedPlacement)
            else:
                self.currentPlacement = copy.deepcopy(self.getPlacement())

            try:
                if self.mode == HATS:
                    base.localAvatar.hat = (self.selectedId, 0, 0)
                    base.localAvatar.generateHat()
                elif self.mode == GLASSES:
                    base.localAvatar.glasses = (self.selectedId, 0, 0)
                    base.localAvatar.generateGlasses()
                else:
                    base.localAvatar.backpack = (self.selectedId, 0, 0)
                    base.localAvatar.generateBackpack()
            except Exception as error:
                print 'Accessory editor could not equip custom accessory:', error

            self._saveEquippedAccessories()
            self.refreshPreviewAccessory()
            self.info['text'] = '[Custom] %s (ID %s)' % (name, self.selectedId)
            self.syncControlsFromPlacement()
            return


        if self.mode == HATS:
            style = ToonDNA.HatStyles[name]
            self.selectedId = style[0]
            base.localAvatar.setHat(*style)
        elif self.mode == GLASSES:
            style = ToonDNA.GlassesStyles[name]
            self.selectedId = style[0]
            base.localAvatar.setGlasses(*style)
        else:
            style = ToonDNA.BackpackStyles[name]
            self.selectedId = style[0]
            base.localAvatar.setBackpack(*style)

        self._saveEquippedAccessories()
        self.currentPlacement = copy.deepcopy(self.getPlacement())

        placementData = _loadAccessoryPlacements()
        typeName = {
            HATS: 'hat',
            GLASSES: 'glasses',
            BACKPACKS: 'backpack'
        }[self.mode]
        savedPlacement = placementData.get(typeName, {}).get(
            str(self.selectedId), {}
        ).get(self.getPlacementKey())

        if isinstance(savedPlacement, dict):
            pos = savedPlacement.get('pos')
            hpr = savedPlacement.get('hpr')
            scale = savedPlacement.get('scale')

            if pos is not None and hpr is not None and scale is not None:
                self.currentPlacement = (
                    tuple(pos),
                    tuple(hpr),
                    tuple(scale)
                )

                key = self.getPlacementKey()
                if self.mode == HATS:
                    table = AccessoryGlobals.ExtendedHatTransTable
                elif self.mode == GLASSES:
                    table = AccessoryGlobals.ExtendedGlassesTransTable
                else:
                    table = AccessoryGlobals.ExtendedBackpackTransTable

                if self.selectedId not in table:
                    table[self.selectedId] = {}
                table[self.selectedId][key] = copy.deepcopy(self.currentPlacement)
                self.forceRefreshAccessory()

        self.info['text'] = '%s  (ID %s)' % (self.getRealName(name), self.selectedId)
        self.syncControlsFromPlacement()

    def getPlacementKey(self):
        style = base.localAvatar.style

        if self.mode == HATS or self.mode == GLASSES:
            if hasattr(style, 'head'):
                return style.head[:2]
            if hasattr(style, 'getHead'):
                return style.getHead()[:2]

        if self.mode == BACKPACKS:
            if hasattr(style, 'torso'):
                return style.torso[0]
            if hasattr(style, 'getTorso'):
                return style.getTorso()[0]

        raise AttributeError('Unable to determine the current Toon DNA placement key.')

    def getPlacement(self):
        key = self.getPlacementKey()

        if self.mode == HATS:
            table = getattr(AccessoryGlobals, 'ExtendedHatTransTable', None)
            baseTable = AccessoryGlobals.HatTransTable
        elif self.mode == GLASSES:
            table = getattr(AccessoryGlobals, 'ExtendedGlassesTransTable', None)
            baseTable = AccessoryGlobals.GlassesTransTable
        else:
            table = getattr(AccessoryGlobals, 'ExtendedBackpackTransTable', None)
            baseTable = AccessoryGlobals.BackpackTransTable

        if table is None:
            raise AttributeError('Extended accessory placement tables are missing from AccessoryGlobals.')

        if self.selectedId not in table:
            table[self.selectedId] = copy.deepcopy(baseTable)

        if key not in table[self.selectedId]:
            table[self.selectedId][key] = copy.deepcopy(baseTable[key])

        return table[self.selectedId][key]

    def setPlacement(self, placement):
        key = self.getPlacementKey()

        if self.mode == HATS:
            table = AccessoryGlobals.ExtendedHatTransTable
            baseTable = AccessoryGlobals.HatTransTable
        elif self.mode == GLASSES:
            table = AccessoryGlobals.ExtendedGlassesTransTable
            baseTable = AccessoryGlobals.GlassesTransTable
        else:
            table = AccessoryGlobals.ExtendedBackpackTransTable
            baseTable = AccessoryGlobals.BackpackTransTable

        if self.selectedId not in table:
            table[self.selectedId] = copy.deepcopy(baseTable)

        if key not in table[self.selectedId]:
            table[self.selectedId][key] = copy.deepcopy(baseTable[key])

        table[self.selectedId][key] = copy.deepcopy(placement)
        self.currentPlacement = copy.deepcopy(placement)
        self.forceRefreshAccessory()

    def syncControlsFromPlacement(self):
        if self.currentPlacement is None:
            return

        pos, hpr, scale = self.currentPlacement
        values = list(pos) + list(hpr) + list(scale)

        for i, value in enumerate(values):
            self.sliders[i]['value'] = value
            self.sliderEntries[i].set(str(round(value, 5)))

    def readControls(self):
        values = [slider['value'] for slider in self.sliders]
        return (
            tuple(values[0:3]),
            tuple(values[3:6]),
            tuple(values[6:9])
        )

    def onSliderChanged(self, index):
        if self.selectedName is None:
            return

        value = self.sliders[index]['value']
        self.sliderEntries[index].set(str(round(value, 5)))
        self.setPlacement(self.readControls())

    def onEntryChanged(self, text, index):
        if self.selectedName is None:
            return

        try:
            value = float(text)
        except ValueError:
            self.sliderEntries[index].set(str(round(self.sliders[index]['value'], 5)))
            return

        minimum, maximum = self.sliders[index]['range']
        value = max(minimum, min(maximum, value))
        self.sliders[index]['value'] = value
        self.sliderEntries[index].set(str(round(value, 5)))
        self.setPlacement(self.readControls())

    def forceRefreshAccessory(self):
        if self.mode == HATS:
            geom = getattr(base.localAvatar, 'toonHat', None)
        elif self.mode == GLASSES:
            geom = getattr(base.localAvatar, 'toonGlasses', None)
        else:
            geom = getattr(base.localAvatar, 'toonBackpack', None)

        if geom is not None and hasattr(geom, 'forcePlace'):
            geom.forcePlace()
            return

        if self.isCustom and self.currentPlacement is not None:
            pos, hpr, scale = self.currentPlacement

            if self.mode == HATS:
                localNodes = getattr(base.localAvatar, 'hatNodes', [])
                previewNodes = getattr(self.previewToon, 'hatNodes', []) if self.previewToon is not None else []
            elif self.mode == GLASSES:
                localNodes = getattr(base.localAvatar, 'glassesNodes', [])
                previewNodes = getattr(self.previewToon, 'glassesNodes', []) if self.previewToon is not None else []
            else:
                localNodes = getattr(base.localAvatar, 'backpackNodes', [])
                previewNodes = getattr(self.previewToon, 'backpackNodes', []) if self.previewToon is not None else []

            for accessoryNode in list(localNodes) + list(previewNodes):
                try:
                    for child in accessoryNode.getChildren():
                        child.setPos(*pos)
                        child.setHpr(*hpr)
                        child.setScale(*scale)
                except Exception as error:
                    print 'Accessory editor direct custom placement failed:', error

            return

        self.refreshPreviewAccessory()

        if self.selectedName is not None:
            if self.mode == HATS:
                base.localAvatar.setHat(*ToonDNA.HatStyles[self.selectedName])
            elif self.mode == GLASSES:
                base.localAvatar.setGlasses(*ToonDNA.GlassesStyles[self.selectedName])
            else:
                base.localAvatar.setBackpack(*ToonDNA.BackpackStyles[self.selectedName])


    def savePlacement(self):
        if self.selectedId is None or self.currentPlacement is None:
            print 'Accessory editor: select and move an accessory before saving.'
            self.info['text'] = 'Nothing to save'
            return

        path = _findAccessoryPlacementsPath()
        if not path:
            print 'Accessory placement path could not be resolved.'
            self.info['text'] = 'Placement path missing'
            return

        data = _loadAccessoryPlacements()

        typeName = {
            HATS: 'hat',
            GLASSES: 'glasses',
            BACKPACKS: 'backpack'
        }[self.mode]
        key = self.getPlacementKey()

        typeData = data.setdefault(typeName, {})
        accessoryData = typeData.setdefault(str(self.selectedId), {})
        accessoryData[key] = {
            'name': self.selectedName,
            'pos': list(self.currentPlacement[0]),
            'hpr': list(self.currentPlacement[1]),
            'scale': list(self.currentPlacement[2])
        }

        temporaryPath = path + '.tmp'

        try:
            outputFile = open(temporaryPath, 'w')
            try:
                json.dump(data, outputFile, indent=4, sort_keys=True)
                outputFile.write('\n')
            finally:
                outputFile.close()

            if os.path.isfile(path):
                os.remove(path)
            os.rename(temporaryPath, path)

            print 'Saved accessory placement to:', path
            print 'Accessory:', self.selectedName
            print 'ID:', self.selectedId
            print 'DNA key:', key
            print 'Placement:', repr(self.currentPlacement)
            self._saveEquippedAccessories()
            self.info['text'] = 'Saved %s' % self.selectedName
        except Exception as error:
            try:
                if os.path.isfile(temporaryPath):
                    os.remove(temporaryPath)
            except:
                pass

            print 'Failed to save placement:', error
            self.info['text'] = 'Placement write failed'

    def exportPlacement(self):
        self.printPlacement()

    def copyPlacement(self):
        if self.currentPlacement is not None:
            self.copiedPlacement = copy.deepcopy(self.currentPlacement)

    def pastePlacement(self):
        if self.selectedName is None or self.copiedPlacement is None:
            return
        self.setPlacement(self.copiedPlacement)
        self.syncControlsFromPlacement()

    def resetPlacement(self):
        if self.selectedName is None:
            return

        key = self.getPlacementKey()

        if self.mode == HATS:
            placement = copy.deepcopy(AccessoryGlobals.HatTransTable[key])
        elif self.mode == GLASSES:
            placement = copy.deepcopy(AccessoryGlobals.GlassesTransTable[key])
        else:
            placement = copy.deepcopy(AccessoryGlobals.BackpackTransTable[key])

        self.setPlacement(placement)
        self.syncControlsFromPlacement()

    def printPlacement(self):
        if self.selectedName is None or self.currentPlacement is None:
            print 'Accessory editor: no accessory selected.'
            return

        print '========== ACCESSORY PLACEMENT =========='
        print 'Mode:', self.mode
        print 'Name:', self.selectedName
        print 'ID:', self.selectedId
        print 'DNA key:', self.getPlacementKey()
        print 'Placement:', repr(self.currentPlacement)
        print '========================================='

    def destroy(self):
        if self.destroyed:
            return
        self.destroyed = True

        self.clearAccessoryButtons()

        if self.previewToon is not None:
            try:
                self.previewToon.cleanup()
            except:
                pass
            try:
                self.previewToon.removeNode()
            except:
                pass
            self.previewToon = None

        if hasattr(self, 'root') and self.root:
            self.root.destroy()

        for modelName in ('buttonGui', 'scrollGui', 'sliderGui', 'closeGui'):
            model = getattr(self, modelName, None)
            if model is not None:
                try:
                    model.removeNode()
                except:
                    pass
                setattr(self, modelName, None)

        if hasattr(base, 'apPanel'):
            base.apPanel = None
