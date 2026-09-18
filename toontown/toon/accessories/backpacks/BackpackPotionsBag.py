from toontown.toon.accessories.ToonAccessory import ToonAccessory


class BackpackPotionsBag(ToonAccessory):
    def fixupAccessoryGeom(self):
        # To avoid dealing with flickering and transparency hell we'll apply bins manually
        bagMain = self.accessoryGeom.find('**/bag_main')
        bagSide_corks = self.accessoryGeom.find('**/bag_side_corks')
        bagSide_glass = self.accessoryGeom.find("**/bag_side_glass")
        if self.toonIsReal:
            bagMain.find("**/bag_main_pack").setBin('opaque', 1)
            bagMain.find("**/bag_main_corks").setBin('opaque', 1)
            bagMain.find("**/bag_main_glass").setBin('transparent', 1)
            bagMain.find("**/bag_main_liquid").setBin('opaque', 1)
            bagSide_corks.setBin('opaque', 1)
            bagSide_glass.setBin('fixed', 1)
            # may be redundant, can optimize later
            bagSide_glass.find("**/bag_side_liquid").setBin('fixed', 1)
            bagSide_glass.find("**/bubbles_green").setBin('fixed', 1)
            bagSide_glass.find("**/bubbles_blue").setBin('fixed', 1)
            bagSide_glass.find("**/bubbles_red").setBin('fixed', 1)
